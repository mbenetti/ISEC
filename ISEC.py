# ISEC - Índice de Sensibilidad al Error Categórico (Index of Sensitivity to Categorical Error)
# Combined metric using Semantic Distance and Penalized Cost Distance

import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config import Config
from Distancia_Semantica import SemanticDistanceCalculator

# Import the semantic version that handles group information
from Distancia_Semantica import load_sentences_from_excel as load_sentences_semantic
from matriz_costo_caracteres import (
    EditCostCalculator,
    load_custom_costs_from_excel,
)
from matriz_costo_caracteres import (
    load_sentences_from_excel as load_sentences_edit,
)


@dataclass
class ISECResult:
    """Result of ISEC calculation for a single sentence."""

    sentence: str
    frequency: int
    frequency_median_normalized: float
    top_k_matches: List[
        Tuple[str, float, float, float, Dict]
    ]  # (sentence, semantic_dist, cost_dist, isec_score, metadata)


class ISECCalculator:
    """
    Calculate ISEC (Índice de Sensibilidad al Error Categórico) metric.

    Formula: ISEC = FMN / (semantic_weight × AvgSemanticDistance + morphologic_weight × AvgCostDistance)

    Where:
    - FMN: Frequency Median Normalized
    - AvgSemanticDistance: Average semantic distance to top k matches
    - AvgCostDistance: Average penalized edit distance to top k matches
    - semantic_weight: Weight for semantic component (0.0-1.0)
    - morphologic_weight: Weight for morphological component (1.0 - semantic_weight)
    """

    def __init__(
        self,
        sentences_file: str = None,
        custom_costs_file: str = None,
        ollama_host: str = None,
        embedding_model: str = None,
        semantic_weight: float = None,
    ):
        """
        Initialize ISEC Calculator.

        Args:
            sentences_file: Path to Excel file with sentences
            custom_costs_file: Path to Excel file with custom costs
            ollama_host: Ollama server host
            embedding_model: Ollama embedding model name
            semantic_weight: Weight for semantic distance (0.0-1.0). Morphologic weight = 1.0 - semantic_weight
        """
        self.sentences_file = sentences_file or Config.SENTENCES_FILE
        self.custom_costs_file = custom_costs_file or Config.CUSTOM_COSTS_FILE
        self.ollama_host = ollama_host or Config.OLLAMA_HOST
        self.embedding_model = embedding_model or Config.OLLAMA_EMBEDDING_MODEL
        self.semantic_weight = (
            semantic_weight
            if semantic_weight is not None
            else Config.ISEC_SEMANTIC_WEIGHT
        )
        self.morphologic_weight = 1.0 - self.semantic_weight

        # Load sentences and frequencies
        self.sentences = []
        self.frequencies = {}
        self._load_sentences()

        # Initialize calculators
        self.cost_calculator = None
        self.semantic_calculator = None
        self._initialize_calculators()

    def _load_sentences(self) -> None:
        """Load sentences and frequencies from Excel file."""
        try:
            self.sentences, metadata_list = load_sentences_semantic(
                self.sentences_file,
                name_column=Config.SENTENCES_NAME_COLUMN,
                frequency_column=Config.SENTENCES_FREQUENCY_COLUMN,
                group_column=Config.SENTENCES_GROUP_COLUMN,
                subgroup_column=Config.SENTENCES_SUBGROUP_COLUMN,
            )
            # Extract frequencies from metadata for backward compatibility
            self.frequencies = {
                sentence: metadata.get("frequency", 1)
                for sentence, metadata in zip(self.sentences, metadata_list)
            }
            print(
                f"✓ Loaded {len(self.sentences)} sentences from {self.sentences_file}"
            )
        except FileNotFoundError:
            print(f"✗ Excel file '{self.sentences_file}' not found")
            raise

    def _initialize_calculators(self) -> None:
        """Initialize cost and semantic calculators."""
        # Initialize EditCostCalculator
        self.cost_calculator = EditCostCalculator(
            default_substitution_cost=Config.DEFAULT_SUBSTITUTION_COST,
            default_insertion_cost=Config.DEFAULT_INSERTION_COST,
            default_deletion_cost=Config.DEFAULT_DELETION_COST,
            default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
        )

        # Load custom costs
        sub_costs, trans_costs = load_custom_costs_from_excel(
            self.custom_costs_file,
            char1_column=Config.COSTS_CHAR1_COLUMN,
            char2_column=Config.COSTS_CHAR2_COLUMN,
            cost_column=Config.COSTS_COST_COLUMN,
            operation_column=Config.COSTS_OPERATION_COLUMN,
        )

        if sub_costs:
            self.cost_calculator.set_custom_costs(sub_costs, operation="substitution")
        if trans_costs:
            self.cost_calculator.set_custom_costs(
                trans_costs, operation="transposition"
            )

        # Setup character matrices
        all_chars = set()
        for s in self.sentences:
            all_chars.update(s)
        if all_chars:
            self.cost_calculator.setup_characters(list(all_chars))

        print(f"✓ Cost calculator initialized")

        # Initialize SemanticDistanceCalculator
        self.semantic_calculator = SemanticDistanceCalculator(
            ollama_host=self.ollama_host,
            embedding_model=self.embedding_model,
            collection_name="isec_sentences",
        )

        # Load sentences into semantic calculator with full metadata including group information
        _, metadata_list = load_sentences_semantic(
            self.sentences_file,
            name_column=Config.SENTENCES_NAME_COLUMN,
            frequency_column=Config.SENTENCES_FREQUENCY_COLUMN,
            group_column=Config.SENTENCES_GROUP_COLUMN,
            subgroup_column=Config.SENTENCES_SUBGROUP_COLUMN,
        )
        self.semantic_calculator.load_sentences(self.sentences, metadata_list)
        print(f"✓ Semantic calculator initialized")

    def calculate_frequency_median_normalized(self) -> float:
        """
        Calculate frequency median normalized (FMN).

        FMN = frequency / median(all_frequencies)

        Returns:
            The median frequency value
        """
        freq_values = list(self.frequencies.values())
        if not freq_values:
            return 1.0

        # Apply log scaling to frequencies if enabled
        if Config.ISEC_FREQUENCY_SCALING_ENABLED:
            # Use log base from config, default to natural log if base <= 1
            log_base = (
                Config.ISEC_FREQUENCY_LOG_BASE
                if Config.ISEC_FREQUENCY_LOG_BASE > 1
                else math.e
            )
            # Apply log scaling to all frequency values
            scaled_freq_values = []
            for freq in freq_values:
                if freq > 0:
                    if log_base == math.e:
                        scaled_freq = math.log(freq)
                    else:
                        scaled_freq = math.log(freq, log_base)
                    # Ensure scaled frequency is positive
                    scaled_freq = max(scaled_freq, 1e-10)
                else:
                    scaled_freq = 1e-10
                scaled_freq_values.append(scaled_freq)
            freq_values = scaled_freq_values

        return statistics.median(freq_values)

    def find_closest_cost_sentence(self, query_sentence: str) -> Tuple[str, float]:
        """
        Find closest sentence by cost distance (excluding query itself).

        Args:
            query_sentence: Sentence to find closest match for

        Returns:
            Tuple of (closest_sentence, penalized_distance)
        """
        min_distance = float("inf")
        closest_sentence = None

        for sentence in self.sentences:
            if sentence == query_sentence:
                continue

            result = self.cost_calculator.calculate_edit_distance(
                query_sentence, sentence
            )
            if result.penalized_distance < min_distance:
                min_distance = result.penalized_distance
                closest_sentence = sentence

        if closest_sentence is None:
            return query_sentence, float("inf")
        return closest_sentence, min_distance

    def find_top_k_semantic_sentences(
        self, query_sentence: str, k: int = 3
    ) -> List[Tuple[str, float, Dict]]:
        """
        Find top k closest sentences by semantic distance (excluding query itself).

        Args:
            query_sentence: Sentence to find closest matches for
            k: Number of top matches to retrieve

        Returns:
            List of (sentence, normalized_distance, metadata) tuples sorted by distance (ascending)
        """
        # Use the semantic calculator's new find_top_k_semantic_matches method with group exclusion
        return self.semantic_calculator.find_top_k_semantic_matches(
            query_sentence,
            k=k,
            exclude_same_group=Config.SAME_GROUP_EXCLUSION,
            exclude_same_subgroup=Config.SAME_SUBGROUP_EXCLUSION,
        )

    def calculate_isec(self, sentence: str, frequency: int) -> ISECResult:
        """
        Calculate ISEC metric for a single sentence.

        Args:
            sentence: The sentence to analyze
            frequency: The frequency of this sentence

        Returns:
            ISECResult with per-match data
        """
        # Get top k semantic matches
        top_k_semantic = self.find_top_k_semantic_sentences(
            sentence, Config.ISEC_TOP_K_MATCHES
        )

        # Calculate frequency median normalized (needed for ISEC calculation)
        median_freq = self.calculate_frequency_median_normalized()

        # Apply log scaling to frequency if enabled
        if Config.ISEC_FREQUENCY_SCALING_ENABLED and frequency > 0:
            # Use log base from config, default to natural log if base <= 1
            log_base = (
                Config.ISEC_FREQUENCY_LOG_BASE
                if Config.ISEC_FREQUENCY_LOG_BASE > 1
                else math.e
            )
            if log_base == math.e:
                scaled_frequency = math.log(frequency)
            else:
                scaled_frequency = math.log(frequency, log_base)
            # Ensure scaled frequency is positive
            scaled_frequency = max(scaled_frequency, 1e-10)
        else:
            scaled_frequency = frequency

        fmn = scaled_frequency / median_freq if median_freq > 0 else scaled_frequency

        if not top_k_semantic:
            # No matches found
            return ISECResult(
                sentence=sentence,
                frequency=frequency,
                frequency_median_normalized=fmn,
                top_k_matches=[],
            )

        # Calculate cost distance and ISEC for each top k semantic match
        top_k_matches = []

        for matched_sentence, semantic_dist, metadata in top_k_semantic:
            # Calculate cost distance to this matched sentence
            cost_result = self.cost_calculator.calculate_edit_distance(
                sentence, matched_sentence
            )
            cost_dist = cost_result.penalized_distance

            # Calculate ISEC for this individual match
            match_weighted_distance = (
                self.semantic_weight * semantic_dist
                + self.morphologic_weight * cost_dist
            )
            if match_weighted_distance > 0:
                match_isec = fmn / match_weighted_distance
            else:
                match_isec = float("inf")

            top_k_matches.append(
                (matched_sentence, semantic_dist, cost_dist, match_isec, metadata)
            )

        return ISECResult(
            sentence=sentence,
            frequency=frequency,
            frequency_median_normalized=fmn,
            top_k_matches=top_k_matches,
        )

    def calculate_all_isec(self) -> List[ISECResult]:
        """
        Calculate ISEC metric for all sentences.

        Returns:
            List of ISECResult objects
        """
        results = []
        for sentence in self.sentences:
            frequency = self.frequencies.get(sentence, 1)
            result = self.calculate_isec(sentence, frequency)
            results.append(result)

        return results

    def print_result(self, result: ISECResult) -> None:
        """Print a formatted ISEC result."""
        print(f"\n'{result.sentence}'")
        print("-" * 120)
        print(f"  Frequency: {result.frequency}")
        print(
            f"  Frequency Median Normalized (FMN): {result.frequency_median_normalized:.4f}"
        )

        # Get group information for the main sentence
        main_sentence_metadata = self.semantic_calculator.metadata_cache.get(
            result.sentence, {}
        )
        main_group = main_sentence_metadata.get("group", "N/A")
        print(f"  Group: {main_group}")

        print(f"\n  Top {len(result.top_k_matches)} Semantic Matches with ISEC Scores:")
        for i, (matched_sent, sem_dist, cost_dist, match_isec, metadata) in enumerate(
            result.top_k_matches, 1
        ):
            print(f"    {i}. '{matched_sent}'")
            # Display group information for matched sentence
            matched_group = metadata.get("group", "N/A")
            # Get matched sentence frequency
            matched_freq = self.frequencies.get(matched_sent, 1)
            print(
                f"       Semantic Distance: {sem_dist:.4f}  |  Cost Distance: {cost_dist:.4f}  |  ISEC: {match_isec:.4f}  |  Group: {matched_group}  |  Frequency: {matched_freq}"
            )

        print(
            f"\n  Weights: semantic={self.semantic_weight:.1%}, morphologic={self.morphologic_weight:.1%}"
        )

    def print_batch_results(self, results: List[ISECResult]) -> None:
        """Print formatted results for all sentences."""
        print("\n" + "=" * 100)
        print("ISEC (Índice de Sensibilidad al Error Categórico) Analysis")
        print("=" * 100)

        for result in results:
            self.print_result(result)

        print("\n" + "=" * 100)
        print("Summary Statistics")
        print("=" * 100)

        if results:
            # Collect all individual match ISEC scores
            all_isec_scores = []
            for result in results:
                for _, _, _, match_isec, _ in result.top_k_matches:
                    if match_isec != float("inf"):
                        all_isec_scores.append(match_isec)

            fmn_values = [r.frequency_median_normalized for r in results]

            print(f"\n  Total sentences analyzed: {len(results)}")
            print(f"  Total match pairs analyzed: {len(all_isec_scores)}")

            if fmn_values:
                print(f"  FMN (Frequency Median Normalized):")
                print(f"    Average: {np.mean(fmn_values):.4f}")
                print(f"    Min: {np.min(fmn_values):.4f}")
                print(f"    Max: {np.max(fmn_values):.4f}")

            if all_isec_scores:
                print(f"  ISEC Scores (per match pair):")
                print(f"    Average: {np.mean(all_isec_scores):.4f}")
                print(f"    Min: {np.min(all_isec_scores):.4f}")
                print(f"    Max: {np.max(all_isec_scores):.4f}")

            if all_isec_scores:
                print(f"  ISEC Scores (per match pair):")
                print(f"    Average: {np.mean(all_isec_scores):.4f}")
                print(f"    Min: {np.min(all_isec_scores):.4f}")
                print(f"    Max: {np.max(all_isec_scores):.4f}")
                print(f"    Median: {np.median(all_isec_scores):.4f}")

        print("=" * 100)

    def export_to_excel(
        self, results: List[ISECResult], output_file: str = "ISEC_Results.xlsx"
    ) -> None:
        """
        Export ISEC results to Excel file.
        Each top k match gets its own row for detailed analysis.

        Args:
            results: List of ISECResult objects
            output_file: Output Excel filename
        """
        data = []
        for result in results:
            # Create one row for each top k match
            for rank, (
                matched_sent,
                sem_dist,
                cost_dist,
                match_isec,
                metadata,
            ) in enumerate(result.top_k_matches, 1):
                # Get group information
                main_group = self.semantic_calculator.metadata_cache.get(
                    result.sentence, {}
                ).get("group", "N/A")
                matched_group = metadata.get("group", "N/A")

                # Get matched sentence frequency
                matched_freq = self.frequencies.get(matched_sent, 1)

                data.append(
                    {
                        "Sentence": result.sentence,
                        "Sentence_Group": main_group,
                        "Frequency": result.frequency,
                        "FMN": round(result.frequency_median_normalized, 4),
                        "Match_Rank": rank,
                        "Matched_Sentence": matched_sent,
                        "Matched_Sentence_Group": matched_group,
                        "Matched_Frequency": matched_freq,
                        "Semantic_Distance": round(sem_dist, 4),
                        "Cost_Distance": round(cost_dist, 4),
                        "ISEC_Score": round(match_isec, 4),
                    }
                )

        df = pd.DataFrame(data)
        df.to_excel(output_file, index=False)
        print(f"\n✓ Results exported to {output_file} ({len(data)} rows)")


def main():
    """Main entry point for ISEC calculation."""
    print("=" * 90)
    print("ISEC - Índice de Sensibilidad al Error Categórico Calculator")
    print("=" * 90)
    print()

    # Display configuration
    Config.display()

    # Create ISEC calculator
    try:
        calculator = ISECCalculator()
        print(f"\nISEC Configuration:")
        print(f"  Semantic Weight: {calculator.semantic_weight:.1%}")
        print(f"  Morphologic Weight: {calculator.morphologic_weight:.1%}")
        print(f"  Top K Matches: {Config.ISEC_TOP_K_MATCHES}")
        print(f"  Output File: {Config.ISEC_OUTPUT_FILE}")
    except Exception as e:
        print(f"✗ Error initializing calculator: {e}")
        return

    # Calculate ISEC for all sentences
    print("\nCalculating ISEC metrics...")
    try:
        results = calculator.calculate_all_isec()
    except Exception as e:
        print(f"✗ Error calculating ISEC: {e}")
        return

    # Display results
    calculator.print_batch_results(results)

    # Export to Excel
    try:
        calculator.export_to_excel(results, Config.ISEC_OUTPUT_FILE)
    except Exception as e:
        print(f"Warning: Could not export to Excel: {e}")


if __name__ == "__main__":
    main()
