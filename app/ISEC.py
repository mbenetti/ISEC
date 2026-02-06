# ISEC - Índice de Sensibilidad al Error Categórico (Index of Sensitivity to Categorical Error)
# Combined metric using Semantic Distance and Penalized Cost Distance

import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config import Config
# Import from local modules in app/ directory
from .Distancia_Semantica import SemanticDistanceCalculator
from .Distancia_Semantica import load_sentences_from_excel as load_sentences_semantic
from .matriz_costo_caracteres import (
    EditCostCalculator,
    load_custom_costs_from_excel,
)
from .matriz_costo_caracteres import (
    load_sentences_from_excel as load_sentences_edit,
)


@dataclass
class ISECResult:
    """Result of ISEC calculation for a single sentence."""

    sentence: str
    frequency: int
    median_frequency: float
    max_frequency: int
    raw_fmn: float
    frequency_median_normalized: float  # This is the SCALED numerator
    top_k_matches: List[
        Tuple[str, float, float, float, Dict, float]
    ]  # (sentence, semantic_dist, cost_dist, isec_score, metadata, pair_numerator)


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
        alpha: float = None,
        source_filter: str = None, # New filter
    ):
        """
        Initialize ISEC Calculator.

        Args:
            sentences_file: Path to Excel file with sentences
            custom_costs_file: Path to Excel file with custom costs
            ollama_host: Ollama server host
            embedding_model: Ollama embedding model name
            alpha: Geometric Mean exponent (0.0-1.0). Controls balance between Semantic (alpha) and Morphologic (1-alpha).
            source_filter: Optional source name (e.g. "Clases.xlsx") to restrict semantic search
        """
        self.sentences_file = sentences_file if sentences_file is not None else Config.SENTENCES_FILE
        self.custom_costs_file = custom_costs_file or Config.CUSTOM_COSTS_FILE
        self.ollama_host = ollama_host or Config.OLLAMA_HOST
        self.embedding_model = embedding_model or Config.OLLAMA_EMBEDDING_MODEL
        self.alpha = (
            alpha
            if alpha is not None
            else Config.ISEC_ALPHA
        )
        self.source_filter = source_filter

        # Load sentences and frequencies
        self.sentences = []
        self.frequencies = {}
        self.max_frequency = 1
        self.metadata_map = {} # Store full metadata keyed by sentence
        
        # Initialize calculators
        self.cost_calculator = None
        self.semantic_calculator = None
        self._initialize_calculators()

        # Only attempt automatic load if not explicitly disabled
        if sentences_file is not False:
            try:
                self._load_sentences()
                # Re-initialize with actual data if loaded
                self._initialize_calculators()
            except FileNotFoundError:
                if sentences_file:
                    raise
                print("Warning: Default sentences file not found. Calculator initialized without data.")

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
            self.max_frequency = max(self.frequencies.values()) if self.frequencies else 1
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

        # Load sentences into semantic calculator only if a file is provided
        if self.sentences_file is not False:
            try:
                _, metadata_list = load_sentences_semantic(
                    self.sentences_file,
                    name_column=Config.SENTENCES_NAME_COLUMN,
                    frequency_column=Config.SENTENCES_FREQUENCY_COLUMN,
                    group_column=Config.SENTENCES_GROUP_COLUMN,
                    subgroup_column=Config.SENTENCES_SUBGROUP_COLUMN,
                )
                self.semantic_calculator.load_sentences(self.sentences, metadata_list)
                print(f"✓ Semantic calculator initialized with {len(self.sentences)} sentences from {self.sentences_file}")
            except Exception as e:
                # If it's a default file missing, we already warned in __init__
                if self.sentences_file and not isinstance(self.sentences_file, bool):
                     print(f"Warning: Could not load semantic data from {self.sentences_file}: {e}")
                pass
        else:
             print(f"✓ Semantic calculator initialized (empty dataset)")
        print(f"✓ Semantic calculator initialized")

    def get_median_frequency(self) -> float:
        """
        Calculate the median frequency value of the entire collection.
        This is used for normalization in the ISEC formula.
        """
        freq_values = list(self.frequencies.values())
        if not freq_values:
            return 1.0
        
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
        # Get query metadata from our localized map
        query_meta = self.metadata_map.get(query_sentence, {})
        
        # Use the semantic calculator's method with localized metadata
        return self.semantic_calculator.find_top_k_semantic_matches(
            query_sentence,
            k=k,
            exclude_same_group=Config.SAME_GROUP_EXCLUSION,
            exclude_same_subgroup=Config.SAME_SUBGROUP_EXCLUSION,
            source_filter=self.source_filter,
            query_metadata=query_meta,
        )

    def calculate_isec(self, sentence: str, frequency: int, k: int = None) -> ISECResult:
        """
        Calculate ISEC metric for a single sentence.

        Args:
            sentence: The sentence to analyze
            frequency: The frequency of this sentence
            k: Number of matches (defaults to Config.ISEC_TOP_K_MATCHES)

        Returns:
            ISECResult with per-match data
        """
        # Get top k semantic matches
        top_k = k if k is not None else Config.ISEC_TOP_K_MATCHES
        top_k_semantic = self.find_top_k_semantic_sentences(
            sentence, top_k
        )
        # Calculate ISEC numerator for the sentence itself (for display/reference)
        # Requirement: Numerator = 1 + log10(Freq)
        log_f = math.log10(max(frequency, 1.0))
        numerator_self = 1.0 + log_f

        if not top_k_semantic:
            # No matches found
            return ISECResult(
                sentence=sentence,
                frequency=frequency,
                median_frequency=self.get_median_frequency(),
                max_frequency=self.max_frequency,
                raw_fmn=log_f, # Now just log10(Freq)
                frequency_median_normalized=numerator_self,
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

            # Calculate pair-based numerator: 1 + log10(mean_freq_pair)
            matched_freq = metadata.get("frequency", 1)
            pair_mean_freq = (frequency + matched_freq) / 2.0
            log_pair = math.log10(max(pair_mean_freq, 1.0))
            match_numerator = 1.0 + log_pair

            # Calculate ISEC for this individual match using Weighted Geometric Mean
            # ISEC = MatchNumerator / (DS^alpha * DM^(1-alpha))
            
            # Protection against zero distances
            ds = max(semantic_dist, 1e-6)
            dm = max(cost_dist, 1e-6)
            
            denominator = pow(ds, self.alpha) * pow(dm, 1.0 - self.alpha)
            
            if denominator > 0:
                match_isec = match_numerator / denominator
            else:
                match_isec = float("inf")

            top_k_matches.append(
                (matched_sentence, semantic_dist, cost_dist, match_isec, metadata, match_numerator)
            )

        return ISECResult(
            sentence=sentence,
            frequency=frequency,
            median_frequency=self.get_median_frequency(),
            max_frequency=self.max_frequency,
            raw_fmn=log_f,
            frequency_median_normalized=numerator_self,
            top_k_matches=top_k_matches,
        )

    def calculate_bulk_isec(self, k: int = 10) -> List[Dict]:
        """
        Calculate ISEC scores for all sentences in the current collection.
        Returns a list of dicts with sentence pairs and their ISEC scores.
        Each entry contains the source sentence and its best matching sentence.
        """
        results = []
        for sentence in self.sentences:
            freq = self.frequencies.get(sentence, 1)
            try:
                res = self.calculate_isec(sentence, freq, k=k)
                
                # Get the best match (highest ISEC score)
                # top_k_matches is a list of tuples: (sentence, semantic_dist, cost_dist, match_isec, metadata, pair_numerator)
                if res.top_k_matches and len(res.top_k_matches) > 0:
                    # Find the match with the highest ISEC score (index 3 in tuple)
                    best_match = max(res.top_k_matches, key=lambda x: x[3])
                    matched_sentence = best_match[0]
                    isec_score = best_match[3] if best_match[3] != float('inf') else 0
                    matched_metadata = best_match[4]
                    matched_group = matched_metadata.get('group', 'N/A')
                else:
                    isec_score = 0
                    matched_sentence = "No match found"
                    matched_group = "N/A"
                
                results.append({
                    "sentence": sentence,
                    "frequency": freq,
                    "group": self.metadata_map.get(sentence, {}).get("group", "N/A"),
                    "matched_sentence": matched_sentence,
                    "matched_group": matched_group,
                    "isec_score": isec_score
                })
            except Exception as e:
                print(f"Error calculating bulk ISEC for {sentence}: {e}")
                results.append({
                    "sentence": sentence,
                    "frequency": freq,
                    "group": self.metadata_map.get(sentence, {}).get("group", "N/A"),
                    "matched_sentence": "Error",
                    "matched_group": "N/A",
                    "isec_score": 0,
                    "error": str(e)
                })
        
        # Sort by ISEC score descending
        results.sort(key=lambda x: x["isec_score"], reverse=True)
        return results

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
        # Print optimized for brevity, keeping original logic if needed
        # ... logic same as original ...
        pass # Not critical for backend usage

    def print_batch_results(self, results: List[ISECResult]) -> None:
        pass

    def export_to_excel(
        self, results: List[ISECResult], output_file: str = "ISEC_Results.xlsx"
    ) -> None:
        pass

