#!/usr/bin/env python3
"""
Test file for the Levenshtein-Damerau Edit Cost Calculator.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matriz_costo_caracteres import EditCostCalculator, create_default_calculator


def test_default_calculator():
    """Test the default calculator with original custom costs."""
    print("Testing default calculator...")

    # Create calculator with default custom costs
    calculator = create_default_calculator()

    # Set up characters from example strings
    example_strings = ["XDKT11T3", "XDKG11T3", "LDKT11T3"]
    all_chars = set()
    for s in example_strings:
        all_chars.update(s)
    calculator.setup_characters(list(all_chars))

    # Test custom substitution costs
    assert calculator.get_substitution_cost("D", "X") == 0.5, "D ↔ X should be 0.5"
    assert calculator.get_substitution_cost("X", "D") == 0.5, "X ↔ D should be 0.5"
    assert calculator.get_substitution_cost("G", "T") == 0.5, "G ↔ T should be 0.5"
    assert calculator.get_substitution_cost("T", "G") == 0.5, "T ↔ G should be 0.5"
    assert calculator.get_substitution_cost("K", "L") == 0.5, "K ↔ L should be 0.5"
    assert calculator.get_substitution_cost("L", "K") == 0.5, "L ↔ K should be 0.5"

    # Test default costs
    assert calculator.get_substitution_cost("X", "L") == 1.0, "X ↔ L should be 1.0"
    assert calculator.get_substitution_cost("1", "3") == 1.0, "1 ↔ 3 should be 1.0"

    # Test same character cost
    assert calculator.get_substitution_cost("X", "X") == 0.0, "X ↔ X should be 0.0"
    assert calculator.get_substitution_cost("1", "1") == 0.0, "1 ↔ 1 should be 0.0"

    print("✓ Default calculator tests passed!")


def test_custom_calculator():
    """Test creating a custom calculator with different costs."""
    print("\nTesting custom calculator...")

    # Create custom calculator
    calculator = EditCostCalculator(
        default_substitution_cost=2.0,
        default_insertion_cost=1.5,
        default_deletion_cost=1.5,
        default_transposition_cost=1.5,
    )

    # Add custom costs
    calculator.set_custom_substitution_cost("A", "B", 0.3)
    calculator.set_custom_substitution_cost("C", "D", 0.7)
    calculator.set_custom_transposition_cost("E", "F", 0.5)

    # Set up characters
    calculator.setup_characters(["A", "B", "C", "D", "E", "F"])

    # Test custom substitution costs
    assert calculator.get_substitution_cost("A", "B") == 0.3, "A ↔ B should be 0.3"
    assert calculator.get_substitution_cost("B", "A") == 0.3, "B ↔ A should be 0.3"
    assert calculator.get_substitution_cost("C", "D") == 0.7, "C ↔ D should be 0.7"

    # Test custom transposition costs
    assert calculator.get_transposition_cost("E", "F") == 0.5, "E ↔ F transposition should be 0.5"
    assert calculator.get_transposition_cost("F", "E") == 0.5, "F ↔ E transposition should be 0.5"

    # Test default costs
    assert calculator.get_substitution_cost("A", "F") == 2.0, (
        "A ↔ F should be 2.0 (default)"
    )
    assert calculator.get_substitution_cost("E", "E") == 0.0, "E ↔ E should be 0.0"

    print("✓ Custom calculator tests passed!")


def test_edit_distance_calculation():
    """Test edit distance calculations."""
    print("\nTesting edit distance calculations...")

    # Create calculator with default custom costs
    calculator = create_default_calculator()
    example_strings = ["XDKT11T3", "XDKG11T3", "LDKT11T3"]
    all_chars = set()
    for s in example_strings:
        all_chars.update(s)
    calculator.setup_characters(list(all_chars))

    # Test 1: Single substitution with custom cost (0.5)
    str1 = "XDKT11T3"
    str2 = "XDKG11T3"  # T -> G (should be 0.5)
    result = calculator.calculate_edit_distance(str1, str2)
    assert abs(result.total_distance - 0.5) < 1e-9, f"Expected 0.5, got {result.total_distance}"
    print(f"✓ Test 1: '{str1}' → '{str2}' = {result.total_distance:.2f}")

    # Test 2: Single substitution with default cost (1.0)
    str1 = "XDKT11T3"
    str2 = "LDKT11T3"  # X -> L (should be 1.0)
    result = calculator.calculate_edit_distance(str1, str2)
    assert abs(result.total_distance - 1.0) < 1e-9, f"Expected 1.0, got {result.total_distance}"
    print(f"✓ Test 2: '{str1}' → '{str2}' = {result.total_distance:.2f}")

    # Test 3: Multiple substitutions
    str1 = "XDKG11T3"
    str2 = "LDKT11T3"  # X->L (1.0) and G->T (0.5) = 1.5
    result = calculator.calculate_edit_distance(str1, str2)
    assert abs(result.total_distance - 1.5) < 1e-9, f"Expected 1.5, got {result.total_distance}"
    print(f"✓ Test 3: '{str1}' → '{str2}' = {result.total_distance:.2f}")

    # Test 4: Same string
    str1 = "XDKT11T3"
    str2 = "XDKT11T3"
    result = calculator.calculate_edit_distance(str1, str2)
    assert abs(result.total_distance - 0.0) < 1e-9, f"Expected 0.0, got {result.total_distance}"
    print(f"✓ Test 4: '{str1}' → '{str2}' = {result.total_distance:.2f}")

    # Test 5: With different operation costs
    calculator2 = EditCostCalculator(
        default_substitution_cost=1.0,
        default_insertion_cost=2.0,  # Higher insertion cost
        default_deletion_cost=2.0,  # Higher deletion cost
        default_transposition_cost=1.0,
    )
    calculator2.set_custom_substitution_cost("D", "X", 0.5)
    calculator2.set_custom_substitution_cost("G", "T", 0.5)
    calculator2.set_custom_substitution_cost("K", "L", 0.5)
    all_chars_extended = list(all_chars) + ["A"]
    calculator2.setup_characters(all_chars_extended)

    # Test insertion/deletion
    str1 = "XDKT11T3"
    str2 = "XDKT11T3A"  # Insert 'A' at end (cost should be 2.0)
    result = calculator2.calculate_edit_distance(str1, str2)
    assert abs(result.total_distance - 2.0) < 1e-9, f"Expected 2.0, got {result.total_distance}"
    print(f"✓ Test 5: Insertion cost = {result.total_distance:.2f}")

    print("✓ All edit distance tests passed!")


def test_operation_tracking():
    """Test operation tracking functionality."""
    print("\nTesting operation tracking...")

    calculator = create_default_calculator()
    example_strings = ["XDKT11T3", "XDKG11T3", "LDKT11T3"]
    all_chars = set()
    for s in example_strings:
        all_chars.update(s)
    calculator.setup_characters(list(all_chars))

    # Test with operation tracking
    str1 = "XDKT11T3"
    str2 = "XDKG11T3"
    result = calculator.calculate_edit_distance(str1, str2)

    assert abs(result.total_distance - 0.5) < 1e-9, f"Expected 0.5, got {result.total_distance}"
    assert result.num_operations >= 1, f"Expected at least 1 operation, got {result.num_operations}"

    # Check operations
    substitutions = [op for op in result.operations if op.op_type == "substitute"]
    assert len(substitutions) >= 1, "Expected at least one substitution"

    op = substitutions[0]
    assert op.from_char == "T" or op.from_char == "G", f"Unexpected character: {op.from_char}"
    assert op.cost == 0.5, f"Expected 0.5 cost, got {op.cost}"

    print(f"✓ Operation tracking: {result.num_operations} operations detected")

    # Test with deletion
    str1 = "ABC"
    str2 = "AB"
    calculator2 = EditCostCalculator()
    calculator2.setup_characters(["A", "B", "C"])
    result = calculator2.calculate_edit_distance(str1, str2)

    deletions = [op for op in result.operations if op.op_type == "delete"]
    assert len(deletions) >= 1, f"Expected at least one deletion, got {len(deletions)}"

    print(f"✓ Operation tracking: Delete operation detected")

    print("✓ All operation tracking tests passed!")


def test_batch_operations():
    """Test batch distance calculations."""
    print("\nTesting batch operations...")

    calculator = create_default_calculator()
    sentences = ["XDKT11T3", "XDKG11T3", "LDKT11T3"]
    all_chars = set()
    for s in sentences:
        all_chars.update(s)
    calculator.setup_characters(list(all_chars))

    # Calculate all distances
    results = calculator.calculate_all_distances(sentences)

    # Should have n*(n-1) results
    expected_results = len(sentences) * (len(sentences) - 1)
    assert len(results) == expected_results, (
        f"Expected {expected_results} results, got {len(results)}"
    )

    # All results should have valid distances
    for result in results:
        assert result.total_distance >= 0, f"Distance should be non-negative"
        assert result.num_operations >= 0, f"Number of operations should be non-negative"

    print(f"✓ Batch operations: {len(results)} pairwise distances calculated")
    print("✓ All batch operation tests passed!")


def test_matrix_display():
    """Test matrix display functionality."""
    print("\nTesting matrix display...")

    calculator = create_default_calculator()
    calculator.setup_characters(["A", "B", "C"])

    # These should not crash
    calculator.display_matrix("Test Substitution Matrix")
    calculator.display_transposition_matrix("Test Transposition Matrix")

    # Show custom costs
    calculator.show_custom_costs()

    print("✓ Matrix display tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Levenshtein-Damerau Edit Cost Calculator")
    print("=" * 60)

    try:
        test_default_calculator()
        test_custom_calculator()
        test_edit_distance_calculation()
        test_operation_tracking()
        test_batch_operations()
        test_matrix_display()

        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
