#!/usr/bin/env python3
"""
Quick Start Guide - Levenshtein-Damerau Distance Calculator

This file demonstrates the most common use cases.
Run with: python quickstart.py
"""

from matriz_costo_caracteres import EditCostCalculator


def quickstart_1_simple_distance():
    """Simplest possible example: Just calculate distance between two strings."""
    print("\n" + "="*70)
    print("QUICKSTART 1: Simple Distance Calculation")
    print("="*70)
    
    # Create calculator with default settings
    calc = EditCostCalculator()
    
    # Setup characters from both strings
    calc.setup_characters(list(set("HELLOHALLO")))
    
    # Calculate distance
    result = calc.calculate_edit_distance("HELLO", "HALLO")
    
    print(f"\nDistance from 'HELLO' to 'HALLO': {result.total_distance}")
    print(f"Operations needed: {result.num_operations}")


def quickstart_2_custom_substitution_cost():
    """Most common use: Define which character pairs are similar."""
    print("\n" + "="*70)
    print("QUICKSTART 2: Custom Substitution Costs (Character Similarity)")
    print("="*70)
    
    calc = EditCostCalculator()
    
    # Define which characters are similar (cost less to substitute)
    # Example: 'A' and 'O' look similar, cost 0.5 instead of 1.0
    similar_pairs = {
        ("A", "O"): 0.5,      # Visually similar
        ("1", "I"): 0.3,      # Often confused
        ("S", "5"): 0.3,      # OCR confusion
    }
    
    calc.set_custom_costs(similar_pairs, operation="substitution")
    
    # Setup - include all characters from both words
    words = ["APPLE", "OPPLE", "5CORE", "SCORE"]
    all_chars = set("".join(words))
    calc.setup_characters(list(all_chars))
    
    # Show the matrix
    calc.display_matrix()
    
    # Compare distances
    print("\nComparison:")
    r1 = calc.calculate_edit_distance("APPLE", "OPPLE")
    print(f"  'APPLE' → 'OPPLE': {r1.total_distance} (A↔O costs 0.5)")
    
    r2 = calc.calculate_edit_distance("5CORE", "SCORE")
    print(f"  '5CORE' → 'SCORE': {r2.total_distance} (S↔5 costs 0.3)")


def quickstart_3_batch_analysis():
    """Analyze multiple strings at once."""
    print("\n" + "="*70)
    print("QUICKSTART 3: Batch Analysis - Compare Multiple Strings")
    print("="*70)
    
    calc = EditCostCalculator()
    
    # Define custom costs
    calc.set_custom_costs({
        ("C", "K"): 0.3,
        ("T", "D"): 0.3,
    }, operation="substitution")
    
    # Strings to compare
    words = ["CAT", "KATS", "DATS", "CATS"]
    all_chars = set("".join(words))
    calc.setup_characters(list(all_chars))
    
    # Calculate all pairwise distances
    results = calc.calculate_all_distances(words)
    
    # Print results with statistics
    calc.print_batch_results(results)


def quickstart_4_different_operation_costs():
    """Use different costs for insertion/deletion vs substitution."""
    print("\n" + "="*70)
    print("QUICKSTART 4: Different Operation Costs")
    print("="*70)
    
    # Scenario: Substitution is cheap, but adding/removing is expensive
    calc = EditCostCalculator(
        default_substitution_cost=0.5,   # Cheap
        default_insertion_cost=1.5,      # More expensive
        default_deletion_cost=1.5,       # More expensive
        default_transposition_cost=0.8,
    )
    
    calc.setup_characters(list("ABCDE"))
    
    print("\nCosts:")
    print(f"  Substitution: {calc.default_substitution_cost}")
    print(f"  Insertion: {calc.default_insertion_cost}")
    print(f"  Deletion: {calc.default_deletion_cost}")
    print(f"  Transposition: {calc.default_transposition_cost}")
    
    print("\nExamples:")
    r1 = calc.calculate_edit_distance("ABC", "ABD")
    print(f"  'ABC' → 'ABD' (substitute C→D): {r1.total_distance}")
    
    r2 = calc.calculate_edit_distance("ABC", "AB")
    print(f"  'ABC' → 'AB' (delete C): {r2.total_distance}")
    
    print("\nNote: Substitution is cheaper than deletion!")


def quickstart_5_real_world_example():
    """Real-world example: Typo detection."""
    print("\n" + "="*70)
    print("QUICKSTART 5: Real-World Example - Typo Detection")
    print("="*70)
    
    calc = EditCostCalculator()
    
    # Common keyboard and OCR errors
    confusions = {
        ("L", "I"): 0.3,      # L/I on keyboard
        ("O", "0"): 0.2,      # O/zero
        ("E", "F"): 0.4,      # E/F on keyboard
        ("1", "L"): 0.2,      # 1/L confusion
    }
    
    calc.set_custom_costs(confusions, operation="substitution")
    
    # Dictionary words
    dictionary = ["HELLO", "FIELD", "WORLD"]
    
    # OCR-scanned text (with errors)
    scanned = ["HE1LO", "FIE1D", "W0RLD"]
    
    # Setup - use characters from both dictionary and scanned
    all_chars = set("".join(dictionary + scanned))
    calc.setup_characters(list(all_chars))
    
    print("\nCorrecting OCR errors:")
    print("-" * 70)
    
    for scanned_word in scanned:
        distances = []
        for dict_word in dictionary:
            result = calc.calculate_edit_distance(scanned_word, dict_word)
            distances.append((dict_word, result.total_distance))
        
        # Find closest match
        best_match, best_distance = min(distances, key=lambda x: x[1])
        print(f"\n  Scanned: '{scanned_word}'")
        print(f"  Best match: '{best_match}' (distance: {best_distance:.2f})")
        for word, dist in distances:
            marker = " ← BEST" if word == best_match else ""
            print(f"    vs '{word}': {dist:.2f}{marker}")


def quickstart_6_understanding_operations():
    """See what operations are performed."""
    print("\n" + "="*70)
    print("QUICKSTART 6: Understanding Operations")
    print("="*70)
    
    calc = EditCostCalculator()
    calc.set_custom_substitution_cost("A", "O", 0.5)
    calc.setup_characters(list(set("CATCOTAPPLEOAPLEAPLE")))
    
    # Example 1: Simple substitution
    print("\nExample 1: Single substitution")
    print("-" * 70)
    result = calc.calculate_edit_distance("CAT", "COT")
    calc.print_result(result)
    
    # Example 2: Multiple operations
    print("\nExample 2: Multiple operations")
    print("-" * 70)
    result = calc.calculate_edit_distance("APPLE", "OAPLE")
    calc.print_result(result)
    
    # Example 3: Insertion/Deletion
    print("\nExample 3: Deletion")
    print("-" * 70)
    result = calc.calculate_edit_distance("APPLE", "APLE")
    calc.print_result(result)


def quickstart_7_transposition():
    """Support for transposed characters (swap two adjacent chars)."""
    print("\n" + "="*70)
    print("QUICKSTART 7: Transposition Support")
    print("="*70)
    
    calc = EditCostCalculator()
    
    # Make transposing 'A' and 'B' cheaper
    calc.set_custom_transposition_cost("A", "B", 0.3)
    calc.setup_characters(list("ABCDE"))
    
    print("\nTransposition is cheaper than two operations:")
    print("-" * 70)
    
    result = calc.calculate_edit_distance("AB", "BA")
    print(f"\n'AB' → 'BA':")
    print(f"  Distance: {result.total_distance}")
    print(f"  Operations: {result.num_operations}")
    calc.print_result(result)


def quickstart_8_advanced_configuration():
    """Advanced: All configuration options."""
    print("\n" + "="*70)
    print("QUICKSTART 8: Advanced Configuration")
    print("="*70)
    
    # Full configuration
    calc = EditCostCalculator(
        default_substitution_cost=1.0,
        default_insertion_cost=1.0,
        default_deletion_cost=1.0,
        default_transposition_cost=1.0,
    )
    
    # Set substitution costs (one by one or in batch)
    calc.set_custom_substitution_cost("A", "O", 0.5)
    calc.set_custom_substitution_cost("E", "I", 0.5)
    
    # Set transposition costs
    calc.set_custom_transposition_cost("T", "H", 0.4)
    
    # Or use batch method
    calc.set_custom_costs({
        ("S", "Z"): 0.3,
    }, operation="substitution")
    
    calc.setup_characters(list("AOEITSZHC"))
    
    # Display everything
    calc.display_matrix("Substitution Costs")
    calc.display_transposition_matrix("Transposition Costs")
    calc.show_custom_costs()


def main():
    """Run all quick start examples."""
    print("\n" + "="*70)
    print("LEVENSHTEIN-DAMERAU CALCULATOR - QUICK START GUIDE")
    print("="*70)
    print("\nThis guide shows the most common use cases.")
    print("See GUIDE.md for complete documentation.")
    
    quickstart_1_simple_distance()
    quickstart_2_custom_substitution_cost()
    quickstart_3_batch_analysis()
    quickstart_4_different_operation_costs()
    quickstart_5_real_world_example()
    quickstart_6_understanding_operations()
    quickstart_7_transposition()
    quickstart_8_advanced_configuration()
    
    print("\n" + "="*70)
    print("Quick start complete! See GUIDE.md for full documentation.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
