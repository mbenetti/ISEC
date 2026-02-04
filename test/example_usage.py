#!/usr/bin/env python3
"""
Comprehensive example demonstrating the Levenshtein-Damerau distance calculator
with custom operation costs for both substitution and transposition.
"""

from matriz_costo_caracteres import EditCostCalculator


def example_1_basic_usage():
    """Example 1: Basic usage with custom substitution costs."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Usage with Custom Substitution Costs")
    print("="*80)
    
    # Create a calculator
    calc = EditCostCalculator(
        default_substitution_cost=1.0,
        default_insertion_cost=1.0,
        default_deletion_cost=1.0,
        default_transposition_cost=1.0,
    )
    
    # Define custom substitution costs
    # A and S are similar, cost 0.5 instead of 1.0
    custom_sub_costs = {
        ("A", "S"): 0.5,
        ("E", "I"): 0.5,
        ("O", "U"): 0.5,
    }
    
    calc.set_custom_costs(custom_sub_costs, operation="substitution")
    
    # Setup characters from example sentences
    # sentences = ["CASE", "CASE", "CASE"]  # Will use these to extract chars
    sentences = ["CASE", "SASE", "IASE"]
    
    all_chars = set()
    for s in sentences:
        all_chars.update(s)
    calc.setup_characters(list(all_chars))
    
    # Display matrices
    calc.display_matrix()
    
    # Show custom costs
    calc.show_custom_costs()
    
    # Calculate distance between pairs
    print("\nDistance Calculations:")
    print("-" * 80)
    
    result1 = calc.calculate_edit_distance("CASE", "SASE")
    calc.print_result(result1)
    
    result2 = calc.calculate_edit_distance("CASE", "IASE")
    calc.print_result(result2)


def example_2_custom_transposition_costs():
    """Example 2: Using custom transposition costs."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Transposition Costs")
    print("="*80)
    
    calc = EditCostCalculator(
        default_substitution_cost=1.0,
        default_insertion_cost=1.0,
        default_deletion_cost=1.0,
        default_transposition_cost=1.0,
    )
    
    # Custom transposition costs (some transpositions are cheaper)
    custom_trans_costs = {
        ("A", "B"): 0.3,  # Transposing A and B is cheaper
        ("E", "R"): 0.4,
    }
    
    calc.set_custom_costs(custom_trans_costs, operation="transposition")
    
    # Setup from example sentences
    sentences = ["AB", "BA", "ABCDE", "EABCD"]
    all_chars = set()
    for s in sentences:
        all_chars.update(s)
    calc.setup_characters(list(all_chars))
    
    # Show matrices
    calc.display_transposition_matrix()
    calc.show_custom_costs()
    
    # Note: Transposition detection in LD algorithm requires careful backtracking
    print("\nDistance with transposition support:")
    print("-" * 80)
    result = calc.calculate_edit_distance("AB", "BA")
    calc.print_result(result)


def example_3_batch_analysis():
    """Example 3: Batch analysis of multiple sentences."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Batch Analysis of Multiple Sentences")
    print("="*80)
    
    calc = EditCostCalculator(
        default_substitution_cost=1.0,
        default_insertion_cost=1.0,
        default_deletion_cost=1.0,
        default_transposition_cost=1.0,
    )
    
    # Mixed custom costs
    custom_costs = {
        ("C", "K"): 0.3,  # Common phonetic similarity
        ("S", "Z"): 0.4,
        ("T", "D"): 0.3,
    }
    calc.set_custom_costs(custom_costs, operation="substitution")
    
    # Test sentences
    sentences = ["CATS", "KATS", "KADS", "ZATS"]
    
    all_chars = set()
    for s in sentences:
        all_chars.update(s)
    calc.setup_characters(list(all_chars))
    
    # Show setup
    calc.display_matrix()
    calc.show_custom_costs()
    
    # Calculate all pairwise distances
    results = calc.calculate_all_distances(sentences)
    
    # Print comprehensive results
    calc.print_batch_results(results)


def example_4_configurable_defaults():
    """Example 4: Different default operation costs."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Configurable Default Operation Costs")
    print("="*80)
    
    # Scenario: Insertion and deletion are expensive, substitution is cheap
    calc = EditCostCalculator(
        default_substitution_cost=0.5,   # Cheap
        default_insertion_cost=2.0,       # Expensive
        default_deletion_cost=2.0,        # Expensive
        default_transposition_cost=1.0,
    )
    
    sentences = ["CAT", "AT", "CART"]
    all_chars = set()
    for s in sentences:
        all_chars.update(s)
    calc.setup_characters(list(all_chars))
    
    print("\nWith cheap substitution and expensive insertion/deletion:")
    print("-" * 80)
    
    # Deletion vs Substitution comparison
    result1 = calc.calculate_edit_distance("CAT", "AT")
    print("Deleting 'C' from 'CAT' to get 'AT':")
    calc.print_result(result1)
    
    result2 = calc.calculate_edit_distance("CAT", "CAR")
    print("\nSubstituting 'T' → 'R' in 'CAT' to get 'CAR':")
    calc.print_result(result2)


def example_5_linguistic_similarity():
    """Example 5: Linguistic similarity - confusable letter pairs."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Linguistic Similarity - Common Letter Confusions")
    print("="*80)
    
    calc = EditCostCalculator(
        default_substitution_cost=1.0,
        default_insertion_cost=1.0,
        default_deletion_cost=1.0,
        default_transposition_cost=1.0,
    )
    
    # Define phonetically similar pairs that are common errors
    confusions = {
        ("L", "I"): 0.3,      # L/I confusion in OCR
        ("O", "0"): 0.2,      # O/zero confusion
        ("1", "I"): 0.2,      # 1/I confusion
        ("B", "8"): 0.3,      # B/8 confusion
        ("S", "5"): 0.2,      # S/5 confusion
    }
    
    calc.set_custom_costs(confusions, operation="substitution")
    
    # Setup
    words = ["HELLO", "HE1LO", "HEL1O", "0HI"]
    all_chars = set()
    for w in words:
        all_chars.update(w)
    calc.setup_characters(list(all_chars))
    
    calc.display_matrix()
    calc.show_custom_costs()
    
    # Test OCR confusions
    print("\nOCR Error Simulation:")
    print("-" * 80)
    
    test_pairs = [
        ("HELLO", "HEL1O"),  # I → L
        ("0HI", "OHI"),      # 0 → O
    ]
    
    for orig, confused in test_pairs:
        result = calc.calculate_edit_distance(orig, confused)
        print(f"\nOriginal: '{orig}' vs Confused: '{confused}'")
        calc.print_result(result)


def example_6_symmetric_costs():
    """Example 6: Demonstrating symmetric cost property."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Symmetric Cost Property")
    print("="*80)
    
    calc = EditCostCalculator()
    
    # Define custom costs
    costs = {
        ("A", "B"): 0.5,
    }
    calc.set_custom_costs(costs, operation="substitution")
    
    # Setup
    calc.setup_characters(["A", "B", "C"])
    
    print("\nThe cost of A→B should equal B→A:")
    print("-" * 80)
    
    # Show in matrix
    calc.display_matrix()
    
    # Verify with distances
    result_ab = calc.calculate_edit_distance("A", "B")
    result_ba = calc.calculate_edit_distance("B", "A")
    
    print(f"Distance A → B: {result_ab.total_distance}")
    print(f"Distance B → A: {result_ba.total_distance}")
    print(f"Are they equal? {result_ab.total_distance == result_ba.total_distance}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("LEVENSHTEIN-DAMERAU DISTANCE CALCULATOR - COMPREHENSIVE EXAMPLES")
    print("="*80)
    
    example_1_basic_usage()
    example_2_custom_transposition_costs()
    example_3_batch_analysis()
    example_4_configurable_defaults()
    example_5_linguistic_similarity()
    example_6_symmetric_costs()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
