# Character Cost Matrix for Edit Distance Calculations
# Levenshtein-Damerau distance with configurable operation costs

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

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
        return sum(1 for op in self.operations if op.op_type != 'match')
    
    @property
    def average_cost(self) -> float:
        """Average cost per operation."""
        if self.num_operations == 0:
            return 0.0
        return self.total_distance / self.num_operations
    
    @property
    def penalized_distance(self) -> float:
        """Penalized distance: average_cost + (k * total_distance)."""
        return self.average_cost + (self.operation_cost_factor * self.total_distance)


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

    def set_custom_transposition_cost(self, char1: str, char2: str, cost: float) -> None:
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

    def set_custom_costs(self, cost_dict: Dict[Tuple[str, str], float], operation: str = "substitution") -> None:
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

    def calculate_edit_distance_ld(
        self, str1: str, str2: str
    ) -> DistanceResult:
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
                        H[i - 1, j] + self.default_deletion_cost,      # deletion
                        H[i, j - 1] + self.default_insertion_cost,     # insertion
                        H[i - 1, j - 1] + sub_cost,                    # substitution
                    )
                
                # Transposition
                if k > 0 and l > 0:
                    trans_cost = self.get_transposition_cost(str1[i - 1], str2[j - 1])
                    H[i, j] = min(H[i, j], H[k - 1, l - 1] + (i - k - 1) * self.default_deletion_cost +
                                  trans_cost + (j - l - 1) * self.default_insertion_cost)
            
            da[str1[i - 1]] = i
        
        # Backtrack to find operations
        operations = self._backtrack_ld(str1, str2, H)
        total_distance = H[len1, len2]
        
        return DistanceResult(str1, str2, total_distance, operations, operation_cost_factor=Config.COST_FACTOR_PENALIZATION)

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
                operations.append(Operation('match', str1[i - 1], str2[j - 1], 0.0))
                i -= 1
                j -= 1
            elif i > 0 and j > 0:
                # Check which operation was used
                sub_cost = self.get_substitution_cost(str1[i - 1], str2[j - 1])
                trans_cost = self.get_transposition_cost(str1[i - 1], str2[j - 1])
                
                delete_score = H.get((i - 1, j), float('inf')) + self.default_deletion_cost if i > 0 else float('inf')
                insert_score = H.get((i, j - 1), float('inf')) + self.default_insertion_cost if j > 0 else float('inf')
                subst_score = H.get((i - 1, j - 1), float('inf')) + sub_cost
                transp_score = H.get((i - 2, j - 2), float('inf')) + trans_cost if i > 1 and j > 1 and str1[i - 1] == str2[j - 2] and str1[i - 2] == str2[j - 1] else float('inf')
                
                current = H.get((i, j), float('inf'))
                
                if abs(current - subst_score) < 1e-9:
                    operations.append(Operation('substitute', str1[i - 1], str2[j - 1], sub_cost))
                    i -= 1
                    j -= 1
                elif abs(current - transp_score) < 1e-9:
                    operations.append(Operation('transpose', str1[i - 1], str2[j - 1], trans_cost))
                    i -= 2
                    j -= 2
                elif abs(current - delete_score) < 1e-9:
                    operations.append(Operation('delete', str1[i - 1], '', self.default_deletion_cost))
                    i -= 1
                else:
                    operations.append(Operation('insert', '', str2[j - 1], self.default_insertion_cost))
                    j -= 1
            elif i > 0:
                operations.append(Operation('delete', str1[i - 1], '', self.default_deletion_cost))
                i -= 1
            else:
                operations.append(Operation('insert', '', str2[j - 1], self.default_insertion_cost))
                j -= 1
        
        operations.reverse()
        return operations

    def calculate_edit_distance(
        self, str1: str, str2: str
    ) -> DistanceResult:
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

    def display_transposition_matrix(self, title: str = "Transposition Cost Matrix") -> None:
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
            print(f"  Average edition cost between sentences: {result.average_cost:.4f}")
            print(f"  Penalized Distance (avg + k*total): {result.penalized_distance:.4f}")
        
        print(f"\n  Operations:")
        total_cost = 0.0
        for i, op in enumerate(result.operations, 1):
            if op.op_type == 'match' and not show_all_ops:
                continue
            
            if op.op_type == 'substitute':
                print(f"    {i}. Substitute '{op.from_char}' → '{op.to_char}' (cost: {op.cost:.4f})")
            elif op.op_type == 'transpose':
                print(f"    {i}. Transpose '{op.from_char}' ↔ '{op.to_char}' (cost: {op.cost:.4f})")
            elif op.op_type == 'delete':
                print(f"    {i}. Delete '{op.from_char}' (cost: {op.cost:.4f})")
            elif op.op_type == 'insert':
                print(f"    {i}. Insert '{op.to_char}' (cost: {op.cost:.4f})")
            elif op.op_type == 'match':
                print(f"    {i}. Match '{op.from_char}' (cost: {op.cost:.4f})")
            
            total_cost += op.cost

    def print_batch_results(self, results: List[DistanceResult]) -> None:
        """
        Print formatted results for multiple sentence pairs.

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
            penalized_distances = [r.penalized_distance for r in results if r.num_operations > 0]
            
            print(f"  Total pairs analyzed: {len(results)}")
            print(f"  Average distance: {np.mean(distances):.4f}")
            print(f"  Min distance: {np.min(distances):.4f}")
            print(f"  Max distance: {np.max(distances):.4f}")
            if avg_distances:
                print(f"  Average cost per operation: {np.mean(avg_distances):.4f}")
            if penalized_distances:
                print(f"  Average penalized distance: {np.mean(penalized_distances):.4f}")
        print("=" * 80)


def load_sentences_from_excel(file_path: str, name_column: str = "Name", frequency_column: str = "Frequency") -> Tuple[List[str], Dict[str, int]]:
    """
    Load sentences from an Excel file.

    Args:
        file_path: Path to the Excel file
        name_column: Name of the column containing sentences
        frequency_column: Name of the column containing frequencies

    Returns:
        Tuple of (sentences_list, frequency_dict) where frequency_dict maps sentence to frequency
    """
    try:
        df = pd.read_excel(file_path)
        
        # Extract sentences and frequencies
        sentences = df[name_column].tolist()
        frequencies = df[frequency_column].to_dict()
        
        # Create a dictionary mapping sentence to frequency
        freq_dict = {sentence: freq for sentence, freq in zip(df[name_column], df[frequency_column])}
        
        return sentences, freq_dict
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        raise
    except KeyError as e:
        print(f"Error: Column {e} not found in Excel file.")
        print(f"Available columns: {df.columns.tolist()}")
        raise
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        raise


def load_custom_costs_from_excel(file_path: str, char1_column: str = "Character1", char2_column: str = "Character2", cost_column: str = "Cost", operation_column: Optional[str] = None) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], float]]:
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


def main():
    """Demonstrate the Levenshtein-Damerau edit distance calculator with custom costs."""

    # Display configuration
    Config.display()

    # Load sentences from Excel file
    try:
        sentences, frequencies = load_sentences_from_excel(
            Config.SENTENCES_FILE,
            name_column=Config.SENTENCES_NAME_COLUMN,
            frequency_column=Config.SENTENCES_FREQUENCY_COLUMN
        )
    except FileNotFoundError:
        print(f"\nExcel file '{Config.SENTENCES_FILE}' not found. Using default example sentences.")
        sentences = ["XDKT11T3", "XDKG11T3", "LDKT11T3"]
        frequencies = {s: 1 for s in sentences}

    print("=" * 80)
    print("Levenshtein-Damerau Distance Calculator with Custom Operation Costs")
    print("=" * 80)
    print(f"Sentences loaded: {len(sentences)}")
    print(f"Sentences: {sentences}\n")
    
    if frequencies:
        print("Frequencies:")
        for sent, freq in frequencies.items():
            print(f"  {sent}: {freq}")
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
        operation_column=Config.COSTS_OPERATION_COLUMN
    )
    
    if sub_costs:
        print(f"Loaded {len(sub_costs) // 2} substitution cost pairs from {Config.CUSTOM_COSTS_FILE}")
        calculator.set_custom_costs(sub_costs, operation="substitution")
    
    if trans_costs:
        print(f"Loaded {len(trans_costs) // 2} transposition cost pairs from {Config.CUSTOM_COSTS_FILE}")
        calculator.set_custom_costs(trans_costs, operation="transposition")
    
    if not sub_costs and not trans_costs:
        print(f"No custom costs found in {Config.CUSTOM_COSTS_FILE}, using defaults only")
    
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
    results = calculator.calculate_all_distances(sentences)
    
    # Print results
    calculator.print_batch_results(results)


if __name__ == "__main__":
    main()
