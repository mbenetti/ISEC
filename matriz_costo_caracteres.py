# Character Cost Matrix for Edit Distance Calculations
# Levenshtein-Damerau distance with configurable operation costs

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config import Config


@dataclass
class Operation:
    """Represents a single edit operation."""

    op_type: str  # 'match', 'substitute', 'delete', 'insert', 'transpose'
    from_char: str
    to_char: str
    cost: float


@dataclass
class DistanceResult:
    """Complete result of distance calculation between two strings."""

    str1: str
    str2: str
    total_distance: float
    operations: List[Operation]
    operation_cost_factor: float = 0.1  # k value for penalized distance

    @property
    def num_operations(self) -> int:
        """Number of actual operations (excluding matches)."""
        return sum(1 for op in self.operations if op.op_type != "match")

    @property
    def average_cost(self) -> float:
        """Average cost per operation."""
        if self.num_operations == 0:
            return 0.0
        return self.total_distance / self.num_operations

    @property
    def sum_edit_costs(self) -> float:
        """Sum of all edit operation costs (insertion, deletion, and substitution).

        Note: Transposition costs are not included in penalization.
        """
        return sum(
            op.cost
            for op in self.operations
            if op.op_type in ("insert", "delete", "substitute")
        )

    @property
    def penalized_distance(self) -> float:
        """Penalized distance: average_cost + (k * sum_edit_costs)."""
        return self.average_cost + (self.operation_cost_factor * self.sum_edit_costs)


class EditCostCalculator:
    """
    Edit distance calculator with Levenshtein-Damerau algorithm and configurable operation costs.

    Features:
    - Set default costs for substitution, insertion, deletion, and transposition
    - Declare custom costs for specific character pairs (substitution and transposition)
    - Support for Levenshtein-Damerau distance calculation
    - Track individual operations with costs
    - Calculate distances between all pairs of sentences
    """

    def __init__(
        self,
        default_substitution_cost: float = 1.0,
        default_insertion_cost: float = 1.5,
        default_deletion_cost: float = 1.5,
        default_transposition_cost: float = 1.0,
    ):
        """
        Initialize the calculator with default operation costs.

        Args:
            default_substitution_cost: Default cost for character substitution
            default_insertion_cost: Default cost for inserting a character
            default_deletion_cost: Default cost for deleting a character
            default_transposition_cost: Default cost for transposing two adjacent characters
        """
        self.default_substitution_cost = default_substitution_cost
        self.default_insertion_cost = default_insertion_cost
        self.default_deletion_cost = default_deletion_cost
        self.default_transposition_cost = default_transposition_cost

        # Store custom substitution and transposition costs
        self.custom_substitution_costs: Dict[Tuple[str, str], float] = {}
        self.custom_transposition_costs: Dict[Tuple[str, str], float] = {}

        # Character set and substitution matrix
        self.characters: List[str] = []
        self.substitution_matrix: Optional[pd.DataFrame] = None
        self.transposition_matrix: Optional[pd.DataFrame] = None

    def set_custom_substitution_cost(self, char1: str, char2: str, cost: float) -> None:
        """
        Declare a custom substitution cost for a character pair.

        Args:
            char1: First character
            char2: Second character
            cost: Custom substitution cost (applies to both directions)
        """
        # Store both directions for symmetric costs
        self.custom_substitution_costs[(char1, char2)] = cost
        self.custom_substitution_costs[(char2, char1)] = cost

        # Update matrix if it exists
        if self.substitution_matrix is not None:
            if char1 in self.characters and char2 in self.characters:
                self.substitution_matrix.loc[char1, char2] = cost
                self.substitution_matrix.loc[char2, char1] = cost

    def set_custom_transposition_cost(
        self, char1: str, char2: str, cost: float
    ) -> None:
        """
        Declare a custom transposition cost for a character pair.

        Args:
            char1: First character
            char2: Second character
            cost: Custom transposition cost (applies to both directions)
        """
        # Store both directions for symmetric costs
        self.custom_transposition_costs[(char1, char2)] = cost
        self.custom_transposition_costs[(char2, char1)] = cost

        # Update matrix if it exists
        if self.transposition_matrix is not None:
            if char1 in self.characters and char2 in self.characters:
                self.transposition_matrix.loc[char1, char2] = cost
                self.transposition_matrix.loc[char2, char1] = cost

    def set_custom_costs(
        self, cost_dict: Dict[Tuple[str, str], float], operation: str = "substitution"
    ) -> None:
        """
        Declare multiple custom costs at once.

        Args:
            cost_dict: Dictionary with format {(char1, char2): cost}
            operation: Type of operation - "substitution" or "transposition"
        """
        if operation == "substitution":
            for (char1, char2), cost in cost_dict.items():
                self.set_custom_substitution_cost(char1, char2, cost)
        elif operation == "transposition":
            for (char1, char2), cost in cost_dict.items():
                self.set_custom_transposition_cost(char1, char2, cost)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def setup_characters(self, characters: List[str]) -> None:
        """
        Set up the character set and build substitution and transposition matrices.

        Args:
            characters: List of unique characters to include
        """
        self.characters = sorted(set(characters))
        n = len(self.characters)

        # Create substitution matrix with default costs
        sub_matrix = np.full((n, n), self.default_substitution_cost, dtype=float)
        np.fill_diagonal(sub_matrix, 0.0)  # Same character = 0 cost
        self.substitution_matrix = pd.DataFrame(
            sub_matrix, index=self.characters, columns=self.characters
        )

        # Create transposition matrix with default costs
        trans_matrix = np.full((n, n), self.default_transposition_cost, dtype=float)
        np.fill_diagonal(trans_matrix, 0.0)  # Same character = 0 cost
        self.transposition_matrix = pd.DataFrame(
            trans_matrix, index=self.characters, columns=self.characters
        )

        # Apply any custom costs that were already declared
        self._apply_custom_costs()

    def _apply_custom_costs(self) -> None:
        """Apply all declared custom costs to the matrices."""
        if self.substitution_matrix is None or self.transposition_matrix is None:
            return

        for (char1, char2), cost in self.custom_substitution_costs.items():
            if char1 in self.characters and char2 in self.characters:
                self.substitution_matrix.loc[char1, char2] = cost

        for (char1, char2), cost in self.custom_transposition_costs.items():
            if char1 in self.characters and char2 in self.characters:
                self.transposition_matrix.loc[char1, char2] = cost
        for (char1, char2), cost in self.custom_substitution_costs.items():
            if char1 in self.characters and char2 in self.characters:
                self.substitution_matrix.loc[char1, char2] = cost

        for (char1, char2), cost in self.custom_transposition_costs.items():
            if char1 in self.characters and char2 in self.characters:
                self.transposition_matrix.loc[char1, char2] = cost

    def get_substitution_cost(self, char1: str, char2: str) -> float:
        """
        Get substitution cost between two characters.

        Args:
            char1: First character
            char2: Second character

        Returns:
            Substitution cost (custom if declared, otherwise default)

        Raises:
            ValueError: If characters not in matrix
        """
        if self.substitution_matrix is None:
            raise ValueError("Characters not set up. Call setup_characters() first.")

        if char1 not in self.characters or char2 not in self.characters:
            raise ValueError(f"Character not in matrix: '{char1}' or '{char2}'")

        return self.substitution_matrix.loc[char1, char2]

    def get_transposition_cost(self, char1: str, char2: str) -> float:
        """
        Get transposition cost between two characters.

        Args:
            char1: First character
            char2: Second character

        Returns:
            Transposition cost (custom if declared, otherwise default)

        Raises:
            ValueError: If characters not in matrix
        """
        if self.transposition_matrix is None:
            raise ValueError("Characters not set up. Call setup_characters() first.")

        if char1 not in self.characters or char2 not in self.characters:
            raise ValueError(f"Character not in matrix: '{char1}' or '{char2}'")

        return self.transposition_matrix.loc[char1, char2]

    def calculate_edit_distance_ld(self, str1: str, str2: str) -> DistanceResult:
        """
        Calculate Levenshtein-Damerau distance between two strings.

        This implementation supports:
        - Insertion
        - Deletion
        - Substitution
        - Transposition (Damerau extension)

        Args:
            str1: First string
            str2: Second string

        Returns:
            DistanceResult with total distance and operations
        """
        len1, len2 = len(str1), len(str2)

        # Create a dictionary to store the last occurrence of each character
        da = defaultdict(int)

        # Maximum possible distance
        max_dist = len1 + len2

        # DP table with one extra row and column for max_dist
        H = {}
        H[-1, -1] = max_dist

        for i in range(0, len1 + 1):
            H[i, -1] = max_dist
            H[i, 0] = i * self.default_deletion_cost
        for j in range(0, len2 + 1):
            H[-1, j] = max_dist
            H[0, j] = j * self.default_insertion_cost

        for i in range(1, len1 + 1):
            DB = 0
            for j in range(1, len2 + 1):
                k = da[str2[j - 1]]
                l = DB
                cost = 1
                if str1[i - 1] == str2[j - 1]:
                    cost = 0
                    DB = j

                if str1[i - 1] == str2[j - 1]:
                    H[i, j] = H[i - 1, j - 1]
                else:
                    sub_cost = self.get_substitution_cost(str1[i - 1], str2[j - 1])
                    H[i, j] = min(
                        H[i - 1, j] + self.default_deletion_cost,  # deletion
                        H[i, j - 1] + self.default_insertion_cost,  # insertion
                        H[i - 1, j - 1] + sub_cost,  # substitution
                    )

                # Transposition
                if k > 0 and l > 0:
                    trans_cost = self.get_transposition_cost(str1[i - 1], str2[j - 1])
                    H[i, j] = min(
                        H[i, j],
                        H[k - 1, l - 1]
                        + (i - k - 1) * self.default_deletion_cost
                        + trans_cost
                        + (j - l - 1) * self.default_insertion_cost,
                    )

            da[str1[i - 1]] = i

        # Backtrack to find operations
        operations = self._backtrack_ld(str1, str2, H)
        total_distance = H[len1, len2]

        return DistanceResult(
            str1,
            str2,
            total_distance,
            operations,
            operation_cost_factor=Config.COST_FACTOR_PENALIZATION,
        )

    def _backtrack_ld(self, str1: str, str2: str, H: Dict) -> List[Operation]:
        """
        Backtrack through the DP table to find the operations.

        Args:
            str1: First string
            str2: Second string
            H: DP table dictionary

        Returns:
            List of Operation objects in order
        """
        operations = []
        i, j = len(str1), len(str2)

        while i > 0 or j > 0:
            if i > 0 and j > 0 and str1[i - 1] == str2[j - 1]:
                # Match - no operation needed
                operations.append(Operation("match", str1[i - 1], str2[j - 1], 0.0))
                i -= 1
                j -= 1
            elif i > 0 and j > 0:
                # Check which operation was used
                sub_cost = self.get_substitution_cost(str1[i - 1], str2[j - 1])
                trans_cost = self.get_transposition_cost(str1[i - 1], str2[j - 1])

                delete_score = (
                    H.get((i - 1, j), float("inf")) + self.default_deletion_cost
                    if i > 0
                    else float("inf")
                )
                insert_score = (
                    H.get((i, j - 1), float("inf")) + self.default_insertion_cost
                    if j > 0
                    else float("inf")
                )
                subst_score = H.get((i - 1, j - 1), float("inf")) + sub_cost
                transp_score = (
                    H.get((i - 2, j - 2), float("inf")) + trans_cost
                    if i > 1
                    and j > 1
                    and str1[i - 1] == str2[j - 2]
                    and str1[i - 2] == str2[j - 1]
                    else float("inf")
                )

                current = H.get((i, j), float("inf"))

                if abs(current - subst_score) < 1e-9:
                    operations.append(
                        Operation("substitute", str1[i - 1], str2[j - 1], sub_cost)
                    )
                    i -= 1
                    j -= 1
                elif abs(current - transp_score) < 1e-9:
                    operations.append(
                        Operation("transpose", str1[i - 1], str2[j - 1], trans_cost)
                    )
                    i -= 2
                    j -= 2
                elif abs(current - delete_score) < 1e-9:
                    operations.append(
                        Operation("delete", str1[i - 1], "", self.default_deletion_cost)
                    )
                    i -= 1
                else:
                    operations.append(
                        Operation(
                            "insert", "", str2[j - 1], self.default_insertion_cost
                        )
                    )
                    j -= 1
            elif i > 0:
                operations.append(
                    Operation("delete", str1[i - 1], "", self.default_deletion_cost)
                )
                i -= 1
            else:
                operations.append(
                    Operation("insert", "", str2[j - 1], self.default_insertion_cost)
                )
                j -= 1

        operations.reverse()
        return operations

    def calculate_edit_distance(self, str1: str, str2: str) -> DistanceResult:
        """
        Calculate edit distance between two strings (alias for LD).

        Args:
            str1: First string
            str2: Second string

        Returns:
            DistanceResult with total distance and operations
        """
        return self.calculate_edit_distance_ld(str1, str2)

    def calculate_all_distances(self, sentences: List[str]) -> List[DistanceResult]:
        """
        Calculate distances between all pairs of sentences.

        Args:
            sentences: List of sentences

        Returns:
            List of DistanceResult for all pairs (both directions)
        """
        results = []
        for i, sent1 in enumerate(sentences):
            for j, sent2 in enumerate(sentences):
                if i != j:
                    result = self.calculate_edit_distance(sent1, sent2)
                    results.append(result)
        return results

    def display_matrix(self, title: str = "Substitution Cost Matrix") -> None:
        """
        Display the substitution cost matrix.

        Args:
            title: Title to display above the matrix
        """
        if self.substitution_matrix is None:
            print("Matrix not initialized. Call setup_characters() first.")
            return

        print(f"\n{title}")
        print("=" * 80)
        print(self.substitution_matrix)
        print("=" * 80)

    def display_transposition_matrix(
        self, title: str = "Transposition Cost Matrix"
    ) -> None:
        """
        Display the transposition cost matrix.

        Args:
            title: Title to display above the matrix
        """
        if self.transposition_matrix is None:
            print("Matrix not initialized. Call setup_characters() first.")
            return

        print(f"\n{title}")
        print("=" * 80)
        print(self.transposition_matrix)
        print("=" * 80)

    def show_custom_costs(self) -> None:
        """Display all declared custom costs (substitution and transposition)."""
        has_sub = len(self.custom_substitution_costs) > 0
        has_trans = len(self.custom_transposition_costs) > 0

        if not has_sub and not has_trans:
            print("No custom costs declared.")
            return

        print("\nCustom Costs:")
        print("-" * 60)

        if has_sub:
            print("Substitution:")
            seen = set()
            for (char1, char2), cost in self.custom_substitution_costs.items():
                sorted_pair = tuple(sorted((char1, char2)))
                if sorted_pair not in seen:
                    seen.add(sorted_pair)
                    print(f"  {char1} ↔ {char2}: {cost}")

        if has_trans:
            print("Transposition:")
            seen = set()
            for (char1, char2), cost in self.custom_transposition_costs.items():
                sorted_pair = tuple(sorted((char1, char2)))
                if sorted_pair not in seen:
                    seen.add(sorted_pair)
                    print(f"  {char1} ↔ {char2}: {cost}")

        print("-" * 60)

    def print_result(self, result: DistanceResult, show_all_ops: bool = False) -> None:
        """
        Print a formatted distance result.

        Args:
            result: DistanceResult to print
            show_all_ops: If True, show all operations including matches
        """
        print(f"\n'{result.str1}' → '{result.str2}'")
        print("-" * 80)
        print(f"  Total Distance: {result.total_distance:.4f}")
        print(f"  Number of Operations: {result.num_operations}")
        if result.num_operations > 0:
            print(f"  Average cost per operation: {result.average_cost:.4f}")
            print(
                f"  Sum of all edit costs (insertion, deletion, substitution): {result.sum_edit_costs:.4f}"
            )
            print(
                f"  Penalized Distance (avg + k*sum_edit_costs): {result.penalized_distance:.4f}"
            )

        print(f"\n  Operations:")
        total_cost = 0.0
        for i, op in enumerate(result.operations, 1):
            if op.op_type == "match" and not show_all_ops:
                continue

            if op.op_type == "substitute":
                print(
                    f"    {i}. Substitute '{op.from_char}' → '{op.to_char}' (cost: {op.cost:.4f})"
                )
            elif op.op_type == "transpose":
                print(
                    f"    {i}. Transpose '{op.from_char}' ↔ '{op.to_char}' (cost: {op.cost:.4f})"
                )
            elif op.op_type == "delete":
                print(f"    {i}. Delete '{op.from_char}' (cost: {op.cost:.4f})")
            elif op.op_type == "insert":
                print(f"    {i}. Insert '{op.to_char}' (cost: {op.cost:.4f})")
            elif op.op_type == "match":
                print(f"    {i}. Match '{op.from_char}' (cost: {op.cost:.4f})")

            total_cost += op.cost

    def print_batch_results(self, results: List[DistanceResult]) -> None:
        """
        Print results for multiple distance calculations.

        Args:
            results: List of DistanceResult objects
        """
        print("\n" + "=" * 80)
        print("Levenshtein-Damerau Distance Results for All Pairs")
        print("=" * 80)

        for result in results:
            self.print_result(result)

        print("\n" + "=" * 80)
        print("Summary Statistics")
        print("=" * 80)

        if results:
            distances = [r.total_distance for r in results]
            avg_distances = [r.average_cost for r in results if r.num_operations > 0]
            penalized_distances = [
                r.penalized_distance for r in results if r.num_operations > 0
            ]

            print(f"  Total pairs analyzed: {len(results)}")
            print(f"  Average distance: {np.mean(distances):.4f}")
            print(f"  Min distance: {np.min(distances):.4f}")
            print(f"  Max distance: {np.max(distances):.4f}")
            if avg_distances:
                print(f"  Average cost per operation: {np.mean(avg_distances):.4f}")
            if penalized_distances:
                print(
                    f"  Average penalized distance: {np.mean(penalized_distances):.4f}"
                )
        print("=" * 80)

    def calculate_distances_with_filtering(
        self,
        sentences: List[str],
        metadata_list: List[Dict],
        exclude_same_group: bool = False,
        exclude_same_subgroup: bool = False,
    ) -> List[DistanceResult]:
        """
        Calculate edit distances between all sentence pairs with optional group/subgroup exclusion.

        Args:
            sentences: List of all sentences
            metadata_list: List of metadata dictionaries (one per sentence)
            exclude_same_group: If True, exclude comparisons within the same group
            exclude_same_subgroup: If True, exclude comparisons within the same subgroup

        Returns:
            List of DistanceResult objects for filtered comparisons
        """
        if len(sentences) != len(metadata_list):
            raise ValueError("Number of sentences and metadata must match")

        results = []

        # Calculate distances for all unique pairs
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                sentence1 = sentences[i]
                sentence2 = sentences[j]
                metadata1 = metadata_list[i]
                metadata2 = metadata_list[j]

                # Check group exclusion
                if exclude_same_group:
                    group1 = metadata1.get("group")
                    group2 = metadata2.get("group")
                    if group1 is not None and group2 is not None and group1 == group2:
                        continue

                # Check subgroup exclusion
                if exclude_same_subgroup:
                    subgroup1 = metadata1.get("subgroup")
                    subgroup2 = metadata2.get("subgroup")
                    if (
                        subgroup1 is not None
                        and subgroup2 is not None
                        and subgroup1 == subgroup2
                    ):
                        continue

                # Calculate edit distance
                result = self.calculate_edit_distance(sentence1, sentence2)
                results.append(result)

        return results


def load_sentences_from_excel(
    file_path: str,
    name_column: str = "Name",
    frequency_column: str = "Frequency",
    group_column: Optional[str] = None,
    subgroup_column: Optional[str] = None,
) -> Tuple[List[str], List[Dict]]:
    """
    Load sentences and metadata from an Excel file, ensuring all sentences are unique.
    Duplicate sentences are merged by summing frequencies and keeping the highest group/subgroup values.

    Args:
        file_path: Path to the Excel file
        name_column: Name of the column containing sentences
        frequency_column: Name of the column containing frequencies
        group_column: Optional name of the column containing group labels
        subgroup_column: Optional name of the column containing subgroup labels

    Returns:
        Tuple of (sentences_list, metadata_list) where metadata_list contains dictionaries with frequency, group, subgroup
    """
    try:
        df = pd.read_excel(file_path)

        # Group by sentence (name_column) and merge duplicates
        if name_column in df.columns:
            # Group by the sentence column
            grouped = df.groupby(name_column)

            # Lists to store unique sentences and their merged metadata
            unique_sentences = []
            merged_metadata_list = []

            # Process each group of duplicate sentences
            for sentence, group in grouped:
                unique_sentences.append(sentence)

                # Merge metadata for this sentence
                merged_metadata = {}

                # Sum frequencies if frequency column exists
                if frequency_column in group.columns:
                    merged_metadata["frequency"] = int(group[frequency_column].sum())
                else:
                    merged_metadata["frequency"] = 1

                # Keep the first group value if group column exists
                if group_column and group_column in group.columns:
                    # Get non-null group values and keep the first one
                    non_null_groups = group[group_column].dropna()
                    if len(non_null_groups) > 0:
                        merged_metadata["group"] = str(non_null_groups.iloc[0])

                # Keep the first subgroup value if subgroup column exists
                if subgroup_column and subgroup_column in group.columns:
                    # Get non-null subgroup values and keep the first one
                    non_null_subgroups = group[subgroup_column].dropna()
                    if len(non_null_subgroups) > 0:
                        merged_metadata["subgroup"] = str(non_null_subgroups.iloc[0])

                merged_metadata_list.append(merged_metadata)

            return unique_sentences, merged_metadata_list
        else:
            # Fallback to original behavior if name_column doesn't exist
            sentences = df[name_column].tolist()

            # Build metadata for each sentence
            metadata_list = []
            for idx, row in df.iterrows():
                metadata = {}
                if frequency_column in df.columns:
                    metadata["frequency"] = int(row[frequency_column])
                if group_column and group_column in df.columns:
                    metadata["group"] = str(row[group_column])
                if subgroup_column and subgroup_column in df.columns:
                    metadata["subgroup"] = str(row[subgroup_column])
                metadata_list.append(metadata)

            return sentences, metadata_list

    except FileNotFoundError:
        print(f"Error: Excel file '{file_path}' not found")
        raise
    except Exception as e:
        print(f"Error loading sentences from Excel: {e}")
        raise


def load_custom_costs_from_excel(
    file_path: str,
    char1_column: str = "Character1",
    char2_column: str = "Character2",
    cost_column: str = "Cost",
    operation_column: Optional[str] = None,
) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], float]]:
    """
    Load custom costs from an Excel file.

    Args:
        file_path: Path to the Excel file
        char1_column: Name of the column containing first character
        char2_column: Name of the column containing second character
        cost_column: Name of the column containing cost
        operation_column: Optional column specifying operation type ('substitution' or 'transposition')

    Returns:
        Tuple of (substitution_costs_dict, transposition_costs_dict)
    """
    try:
        df = pd.read_excel(file_path)

        substitution_costs = {}
        transposition_costs = {}

        for idx, row in df.iterrows():
            char1 = str(row[char1_column]).strip()
            char2 = str(row[char2_column]).strip()
            cost = float(row[cost_column])

            # Determine operation type
            if operation_column and operation_column in df.columns:
                op_type = str(row[operation_column]).strip().lower()
            else:
                op_type = "substitution"  # Default to substitution

            # Store in appropriate dictionary (both directions for symmetry)
            if op_type == "substitution":
                substitution_costs[(char1, char2)] = cost
                substitution_costs[(char2, char1)] = cost
            elif op_type == "transposition":
                transposition_costs[(char1, char2)] = cost
                transposition_costs[(char2, char1)] = cost

        return substitution_costs, transposition_costs

    except FileNotFoundError:
        print(f"Warning: File '{file_path}' not found. No custom costs loaded.")
        return {}, {}
    except KeyError as e:
        print(f"Warning: Column {e} not found in Excel file.")
        return {}, {}
    except Exception as e:
        print(f"Warning: Error loading custom costs from Excel file: {e}")
        return {}, {}


def create_default_calculator():
    """
    Create a default EditCostCalculator using settings from Config.
    
    Returns:
        EditCostCalculator: Configured calculator instance
    """
    return EditCostCalculator(
        default_substitution_cost=Config.DEFAULT_SUBSTITUTION_COST,
        default_insertion_cost=Config.DEFAULT_INSERTION_COST,
        default_deletion_cost=Config.DEFAULT_DELETION_COST,
        default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
    )


def main():
    """Demonstrate the Levenshtein-Damerau edit distance calculator with custom costs."""

    # Display configuration
    Config.display()

    # Load sentences from Excel file
    try:
        sentences, metadata_list = load_sentences_from_excel(
            Config.SENTENCES_FILE,
            name_column=Config.SENTENCES_NAME_COLUMN,
            frequency_column=Config.SENTENCES_FREQUENCY_COLUMN,
            group_column=Config.SENTENCES_GROUP_COLUMN,
            subgroup_column=Config.SENTENCES_SUBGROUP_COLUMN,
        )
        print(f"\nLoaded {len(sentences)} sentences from {Config.SENTENCES_FILE}")
    except FileNotFoundError:
        print(
            f"\nExcel file '{Config.SENTENCES_FILE}' not found. Using default example sentences."
        )
        sentences = ["XDKT11T3", "XDKG11T3", "LDKT11T3"]
        metadata_list = [{"frequency": 1} for _ in sentences]

    print("=" * 80)
    print("Levenshtein-Damerau Distance Calculator with Custom Operation Costs")
    print("=" * 80)
    print(f"Sentences loaded: {len(sentences)}")
    print(f"Sentences: {sentences}\n")

    if metadata_list:
        print("Metadata (first 5 sentences):")
        for i, (sentence, metadata) in enumerate(zip(sentences[:5], metadata_list[:5])):
            print(f"  {sentence}: {metadata}")
        print()

    # Create calculator with configured default costs
    calculator = EditCostCalculator(
        default_substitution_cost=Config.DEFAULT_SUBSTITUTION_COST,
        default_insertion_cost=Config.DEFAULT_INSERTION_COST,
        default_deletion_cost=Config.DEFAULT_DELETION_COST,
        default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
    )

    # Load custom costs from Excel file
    sub_costs, trans_costs = load_custom_costs_from_excel(
        Config.CUSTOM_COSTS_FILE,
        char1_column=Config.COSTS_CHAR1_COLUMN,
        char2_column=Config.COSTS_CHAR2_COLUMN,
        cost_column=Config.COSTS_COST_COLUMN,
        operation_column=Config.COSTS_OPERATION_COLUMN,
    )

    if sub_costs:
        print(
            f"Loaded {len(sub_costs) // 2} substitution cost pairs from {Config.CUSTOM_COSTS_FILE}"
        )
        calculator.set_custom_costs(sub_costs, operation="substitution")

    if trans_costs:
        print(
            f"Loaded {len(trans_costs) // 2} transposition cost pairs from {Config.CUSTOM_COSTS_FILE}"
        )
        calculator.set_custom_costs(trans_costs, operation="transposition")

    if not sub_costs and not trans_costs:
        print(
            f"No custom costs found in {Config.CUSTOM_COSTS_FILE}, using defaults only"
        )

    print()

    # Extract unique characters and set up matrices
    all_chars = set()
    for s in sentences:
        all_chars.update(s)
    calculator.setup_characters(list(all_chars))

    # Display the matrices
    calculator.display_matrix("Substitution Cost Matrix")
    calculator.display_transposition_matrix("Transposition Cost Matrix")

    # Show custom costs
    calculator.show_custom_costs()

    # Calculate distances between all pairs
    import time
    start_time = time.time()
    results = calculator.calculate_all_distances(sentences)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nProcessing complete in {elapsed_time:.2f} seconds.")
    print(f"Processed {len(sentences)} items.")

    # Print results
    calculator.print_batch_results(results)

    # Demonstrate metadata filtering functionality
    print("\n" + "=" * 80)
    print("Metadata Filtering Demonstration")
    print("=" * 80)

    # Check if we have group data
    has_group_data = any("group" in metadata for metadata in metadata_list)
    has_subgroup_data = any("subgroup" in metadata for metadata in metadata_list)

    if has_group_data or has_subgroup_data:
        print(f"\nMetadata available:")
        if has_group_data:
            print(f"  - Group data: YES")
            print(
                f"  - Same Group Exclusion (from config): {Config.SAME_GROUP_EXCLUSION}"
            )
        if has_subgroup_data:
            print(f"  - Subgroup data: YES")
            print(
                f"  - Same Subgroup Exclusion (from config): {Config.SAME_SUBGROUP_EXCLUSION}"
            )

        # Calculate distances with filtering
        print(f"\nCalculating distances with metadata filtering...")

        # Without filtering
        print(f"\n1. All comparisons (no filtering):")
        results_all = calculator.calculate_all_distances(sentences)
        print(f"   Total comparisons: {len(results_all)}")

        # With group filtering
        if has_group_data:
            print(f"\n2. Comparisons excluding same group:")
            results_no_same_group = calculator.calculate_distances_with_filtering(
                sentences,
                metadata_list,
                exclude_same_group=True,
                exclude_same_subgroup=False,
            )
            print(f"   Total comparisons: {len(results_no_same_group)}")
            print(
                f"   Excluded comparisons: {len(results_all) - len(results_no_same_group)}"
            )

        # With subgroup filtering
        if has_subgroup_data:
            print(f"\n3. Comparisons excluding same subgroup:")
            results_no_same_subgroup = calculator.calculate_distances_with_filtering(
                sentences,
                metadata_list,
                exclude_same_group=False,
                exclude_same_subgroup=True,
            )
            print(f"   Total comparisons: {len(results_no_same_subgroup)}")
            print(
                f"   Excluded comparisons: {len(results_all) - len(results_no_same_subgroup)}"
            )

        # With both group and subgroup filtering
        if has_group_data and has_subgroup_data:
            print(f"\n4. Comparisons excluding same group AND same subgroup:")
            results_no_same_group_subgroup = (
                calculator.calculate_distances_with_filtering(
                    sentences,
                    metadata_list,
                    exclude_same_group=True,
                    exclude_same_subgroup=True,
                )
            )
            print(f"   Total comparisons: {len(results_no_same_group_subgroup)}")
            print(
                f"   Excluded comparisons: {len(results_all) - len(results_no_same_group_subgroup)}"
            )

        # Show example of filtered comparisons
        if has_group_data and results_no_same_group and len(results_no_same_group) > 0:
            print(f"\nExample of filtered comparison (first result):")
            calculator.print_result(results_no_same_group[0])
    else:
        print(f"\nNo group or subgroup metadata found in the data.")
        print(
            f"To use metadata filtering, add 'Group' and/or 'Subgroup' columns to your Excel file."
        )


if __name__ == "__main__":
    main()
