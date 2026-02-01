# Character Cost Matrix for Edit Distance Calculations
# This module creates a character cost matrix with custom costs for specific character pairs
# as specified: D_X = 0.5, X_D = 0.5, G_T = 0.5, T_G = 0.5, K_L = 0.5, L_K = 0.5
#%%
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


class CharacterCostMatrix:
    """
    A character cost matrix for edit distance calculations with custom costs.

    The matrix defines substitution costs between characters. By default, all
    substitutions cost 1.0, but specific character pairs can have custom costs.

    Example custom costs (order doesn't matter but both directions must be defined):
    - D and X: 0.5
    - G and T: 0.5
    - K and L: 0.5
    """

    def __init__(self, characters: List[str] = None, default_cost: float = 1.0):
        """
        Initialize the character cost matrix.

        Args:
            characters: List of unique characters (if None, will be auto-detected)
            default_cost: Default substitution cost (default: 1.0)
        """
        self.default_cost = default_cost
        self.custom_costs: Dict[Tuple[str, str], float] = {}
        self.characters: List[str] = []
        self.matrix: pd.DataFrame = None

        if characters:
            self.set_characters(characters)

    def set_characters(self, characters: List[str]) -> None:
        """
        Set the characters for the matrix.

        Args:
            characters: List of unique characters
        """
        self.characters = sorted(set(characters))
        self._create_matrix()

    def extract_characters_from_strings(self, strings: List[str]) -> None:
        """
        Extract unique characters from a list of strings.

        Args:
            strings: List of strings to extract characters from
        """
        all_chars = set()
        for s in strings:
            all_chars.update(s)
        self.set_characters(list(all_chars))

    def _create_matrix(self) -> None:
        """Create the base matrix with default costs."""
        n = len(self.characters)
        # Initialize with default cost
        matrix = np.full((n, n), self.default_cost, dtype=float)
        # Set diagonal to 0 (same character)
        np.fill_diagonal(matrix, 0.0)

        # Create DataFrame
        self.matrix = pd.DataFrame(
            matrix, index=self.characters, columns=self.characters
        )

        # Re-apply any custom costs that were set before
        self._reapply_custom_costs()

    def _reapply_custom_costs(self) -> None:
        """Re-apply custom costs to the matrix after recreation."""
        for (char1, char2), cost in self.custom_costs.items():
            if char1 in self.characters and char2 in self.characters:
                self.matrix.loc[char1, char2] = cost
                self.matrix.loc[char2, char1] = cost

    def add_custom_cost(self, char1: str, char2: str, cost: float) -> None:
        """
        Add a custom cost for a character pair.

        Args:
            char1: First character
            char2: Second character
            cost: Custom substitution cost

        Note: The cost is symmetric (char1->char2 = char2->char1 = cost)
        """
        # Store in custom costs dictionary
        self.custom_costs[(char1, char2)] = cost
        self.custom_costs[(char2, char1)] = cost

        # Update matrix if characters exist
        if self.matrix is not None:
            if char1 in self.characters and char2 in self.characters:
                self.matrix.loc[char1, char2] = cost
                self.matrix.loc[char2, char1] = cost

    def add_custom_costs(self, costs: Dict[Tuple[str, str], float]) -> None:
        """
        Add multiple custom costs at once.

        Args:
            costs: Dictionary of custom costs in format {(char1, char2): cost}
        """
        for (char1, char2), cost in costs.items():
            self.add_custom_cost(char1, char2, cost)

    def get_cost(self, char1: str, char2: str) -> float:
        """
        Get substitution cost between two characters.

        Args:
            char1: First character
            char2: Second character

        Returns:
            Substitution cost

        Raises:
            ValueError: If character(s) not in matrix
        """
        if self.matrix is None:
            raise ValueError("Matrix not initialized. Call set_characters() first.")

        if char1 not in self.characters or char2 not in self.characters:
            raise ValueError(f"Character not in matrix: '{char1}' or '{char2}'")

        return self.matrix.loc[char1, char2]

    def display(self, title: str = "Character Cost Matrix") -> None:
        """
        Display the character cost matrix.

        Args:
            title: Title to display above the matrix
        """
        if self.matrix is None:
            print("Matrix not initialized.")
            return

        print(f"\n{title}")
        print("=" * 60)
        print(self.matrix)
        print("=" * 60)

    def verify_custom_costs(self) -> bool:
        """
        Verify that all custom costs are correctly set in the matrix.

        Returns:
            True if all custom costs are correct, False otherwise
        """
        if self.matrix is None:
            print("Matriz no inicializada.")
            return False

        print("\nVerificación de Costos Personalizados")
        print("-" * 40)

        all_correct = True
        for (char1, char2), expected_cost in self.custom_costs.items():
            if char1 in self.characters and char2 in self.characters:
                actual_cost = self.get_cost(char1, char2)
                if actual_cost == expected_cost:
                    print(f"✓ {char1} ↔ {char2}: {expected_cost}")
                else:
                    print(
                        f"✗ {char1} ↔ {char2}: Expected {expected_cost}, Got {actual_cost}"
                    )
                    all_correct = False
            else:
                print(f"✗ {char1} ↔ {char2}: Character(s) not in matrix")
                all_correct = False

        if all_correct:
            print("All custom costs verified successfully!")
        else:
            print("Some custom costs are incorrect!")

        print("-" * 40)
        return all_correct

    def get_custom_cost_pairs(self) -> List[Tuple[str, str, float]]:
        """
        Get list of custom cost pairs (without duplicates).

        Returns:
            List of (char1, char2, cost) tuples
        """
        # Use a set to avoid duplicates (since we store both directions)
        seen = set()
        result = []

        for (char1, char2), cost in self.custom_costs.items():
            # Sort characters to create a canonical representation
            sorted_pair = tuple(sorted((char1, char2)))
            if sorted_pair not in seen:
                seen.add(sorted_pair)
                result.append((char1, char2, cost))

        return result


def levenshtein_with_custom_costs(
    str1: str,
    str2: str,
    cost_matrix: CharacterCostMatrix,
    insertion_cost: float = 1.0,
    deletion_cost: float = 1.0,
    return_average_cost: bool = False,
    return_operation_details: bool = False
) -> float | Tuple[float, float] | Tuple[float, float, List[Tuple[str, str, float]]]:
    """
    Calculate Levenshtein distance with custom character substitution costs.

    Args:
        str1: First string
        str2: Second string
        cost_matrix: CharacterCostMatrix instance
        insertion_cost: Cost for inserting a character
        deletion_cost: Cost for deleting a character
        return_average_cost: If True, also returns the average cost per operation
        return_operation_details: If True, also returns details of operations performed

    Returns:
        Minimum edit distance with custom costs, optionally with average cost per operation
        and optionally with operation details
    """
    m, n = len(str1), len(str2)

    # Create DP table
    dp = [[0.0] * (n + 1) for _ in range(m + 1)]

    # Initialize first row and column
    for i in range(m + 1):
        dp[i][0] = i * deletion_cost

    for j in range(n + 1):
        dp[0][j] = j * insertion_cost

    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                substitution_cost = cost_matrix.get_cost(str1[i - 1], str2[j - 1])

                dp[i][j] = min(
                    dp[i - 1][j] + deletion_cost,  # Delete
                    dp[i][j - 1] + insertion_cost,  # Insert
                    dp[i - 1][j - 1] + substitution_cost,  # Substitute
                )

    if not return_average_cost and not return_operation_details:
        return dp[m][n]
    
    # Backtrack to find the actual operations and their costs
    operation_costs = []
    operation_details = []
    i, j = m, n
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and str1[i-1] == str2[j-1]:
            # Characters match, no operation needed
            i -= 1
            j -= 1
        elif i > 0 and j > 0:
            # Possible operations: substitution, deletion, insertion
            substitution_cost = cost_matrix.get_cost(str1[i-1], str2[j-1])
            subst_score = dp[i-1][j-1] + substitution_cost
            delete_score = dp[i-1][j] + deletion_cost
            insert_score = dp[i][j-1] + insertion_cost
            
            # Choose the operation that led to the current cell value
            if abs(dp[i][j] - subst_score) < 1e-9:  # Substitution
                operation_costs.append(substitution_cost)
                operation_details.append(("substitution", str1[i-1], str2[j-1], substitution_cost))
                i -= 1
                j -= 1
            elif abs(dp[i][j] - delete_score) < 1e-9:  # Deletion
                operation_costs.append(deletion_cost)
                operation_details.append(("deletion", str1[i-1], "", deletion_cost))
                i -= 1
            else:  # Insertion
                operation_costs.append(insertion_cost)
                operation_details.append(("insertion", "", str2[j-1], insertion_cost))
                j -= 1
        elif i > 0:  # Only deletions left
            operation_costs.append(deletion_cost)
            operation_details.append(("deletion", str1[i-1], "", deletion_cost))
            i -= 1
        else:  # Only insertions left
            operation_costs.append(insertion_cost)
            operation_details.append(("insertion", "", str2[j-1], insertion_cost))
            j -= 1

    # Calculate average cost
    average_cost = sum(operation_costs) / len(operation_costs) if operation_costs else 0.0
    
    result = dp[m][n]
    if return_average_cost and return_operation_details:
        return result, average_cost, operation_details
    elif return_average_cost:
        return result, average_cost
    elif return_operation_details:
        return result, operation_details
    else:
        return result


def create_default_cost_matrix() -> CharacterCostMatrix:
    """
    Create a character cost matrix with the default custom costs as specified.

    Custom costs:
    - D and X: 0.5
    - G and T: 0.5
    - K and L: 0.5

    Returns:
        CharacterCostMatrix instance with default custom costs
    """
    # Define the default custom costs as specified
    default_custom_costs = {
        ("D", "X"): 0.5,
        ("G", "T"): 0.5,
        ("K", "L"): 0.5,
    }

    # Create matrix
    matrix = CharacterCostMatrix(default_cost=1.0)

    # Add default custom costs
    matrix.add_custom_costs(default_custom_costs)

    return matrix


#%%
def main():
    """Main function demonstrating the character cost matrix."""

    # Example data from the original problem
    example_strings = [
        "XDKT11T3",
        "XDKG11T3",
        "LDKT11T3",
    ]

    print("Construccion de una Matriz de Costos de Caracteres")
    print("=" * 60)
    print(f"Categorias: {example_strings}")
    print()

    # Create matrix with default custom costs
    cost_matrix = create_default_cost_matrix()

    # Extract characters from example strings
    cost_matrix.extract_characters_from_strings(example_strings)

    # Display the matrix
    cost_matrix.display("Matriz de Costos de Caracteres")

    # Verify custom costs
    cost_matrix.verify_custom_costs()

    # Show custom cost pairs
    custom_pairs = cost_matrix.get_custom_cost_pairs()
    print("\nPares de Caracteres con Costos Personalizados:")
    for char1, char2, cost in custom_pairs:
        print(f"  {char1} ↔ {char2}: {cost}")

    # Example calculations
    print("\n" + "=" * 60)
    print("Cálculos de Distancia de Edición:")
    print("=" * 60)

    test_pairs = [
        ("XDKT11T3", "XDKG11T3"),  # T -> G (should be 0.5)
        ("XDKT11T3", "LDKT11T3"),  # X -> L (should be 1.0, default)
        ("XDKG11T3", "LDKT11T3"),  # X->L (1.0) and G->T (0.5)
    ]

    for str1, str2 in test_pairs:
        distance, avg_cost, operations = levenshtein_with_custom_costs(
            str1, str2, cost_matrix, return_average_cost=True, return_operation_details=True
        )
        print(f"\n'{str1}' → '{str2}':")
        print(f"  Distancia total: {distance:.2f}")
        print(f"  Costo promedio por operación: {avg_cost:.2f}")
        
        # Show operation details
        print("  Operaciones realizadas:")
        for op_type, char1, char2, cost in operations:
            if op_type == "substitution":
                print(f"    Sustitución: '{char1}' → '{char2}' (costo: {cost})")
            elif op_type == "deletion":
                print(f"    Eliminación: '{char1}' (costo: {cost})")
            elif op_type == "insertion":
                print(f"    Inserción: '{char2}' (costo: {cost})")

        # Show detailed character differences
        print("  Caracter por caracter:")
        for i in range(min(len(str1), len(str2))):
            char1_char = str1[i]
            char2_char = str2[i]
            if char1_char == char2_char:
                print(f"    Posición {i}: '{char1_char}' = '{char2_char}' (coinciden)")
            else:
                cost = cost_matrix.get_cost(char1_char, char2_char)
                print(f"    Posición {i}: '{char1_char}' → '{char2_char}' = {cost}")

        # Handle length differences
        len_diff = len(str1) - len(str2)
        if len_diff > 0:
            print(f"  Borrado {len_diff} de la primera cadena")
        elif len_diff < 0:
            print(f"  Inserto {abs(len_diff)} en la primera cadena")

    print("\n" + "=" * 60)
    print("Resumen de Costos Personalizados:")
    print("=" * 60)
    print("Los costos personalizados son:")
    print("  - D ↔ X")
    print("  - G ↔ T")
    print("  - K ↔ L")
    print("\nPor defecto, todos los demás pares de caracteres tienen un costo de 1.0.")
    print("La matriz es simetrica: cost(char1, char2) = cost(char2, char1)")


if __name__ == "__main__":
    main()

# %%