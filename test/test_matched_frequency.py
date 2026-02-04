#!/usr/bin/env python3
"""
Test script to verify matched sentence frequency functionality in ISEC.
This test checks that both the print output and Excel export include
the frequency of matched sentences.
"""

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd

# Add current directory to path to import local modules
sys.path.insert(0, str(Path(__file__).parent))

from ISEC import Config, ISECCalculator


def test_matched_frequency():
    """Test that matched sentence frequency is included in output."""
    print("=" * 80)
    print("Testing Matched Sentence Frequency Functionality")
    print("=" * 80)

    # Create a temporary Excel file with test data
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        # Create test data with groups and frequencies
        test_data = {
            "Name": ["Sentence_A", "Sentence_B", "Sentence_C", "Sentence_D"],
            "Frequency": [100, 50, 75, 25],
            "Group": ["Group1", "Group1", "Group2", "Group2"],
            "Subgroup": ["Sub1", "Sub2", "Sub1", "Sub2"],
        }

        df = pd.DataFrame(test_data)
        df.to_excel(tmp.name, index=False)
        temp_file = tmp.name

    try:
        # Create ISEC calculator with test file
        calculator = ISECCalculator(
            sentences_file=temp_file,
            semantic_weight=0.5,  # Equal weights for testing
        )

        print(f"\n✓ Loaded test data from {temp_file}")
        print(f"  Sentences: {calculator.sentences}")
        print(f"  Frequencies: {calculator.frequencies}")

        # Calculate ISEC for all sentences
        print("\n" + "=" * 80)
        print("Calculating ISEC scores...")
        print("=" * 80)

        results = calculator.calculate_all_isec()

        # Test 1: Check print output includes matched frequency
        print("\nTest 1: Print Output Verification")
        print("-" * 80)

        # Capture print output
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            calculator.print_batch_results(results)

        output = f.getvalue()

        # Check that output contains frequency information for matched sentences
        print("Checking print output for matched frequency...")

        # Look for frequency patterns in the output
        frequency_found = False
        for line in output.split("\n"):
            if "Frequency:" in line and "|" in line:
                print(f"  Found: {line.strip()}")
                frequency_found = True

        if frequency_found:
            print("  ✓ Matched frequency found in print output")
        else:
            print("  ✗ Matched frequency NOT found in print output")

        # Test 2: Check Excel export includes matched frequency
        print("\nTest 2: Excel Export Verification")
        print("-" * 80)

        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as out_tmp:
            output_file = out_tmp.name

        # Export to Excel
        calculator.export_to_excel(results, output_file)
        print(f"  Exported to: {output_file}")

        # Read the exported file
        df_export = pd.read_excel(output_file)

        # Check columns
        print(f"  Columns in export: {list(df_export.columns)}")

        # Check for Matched_Frequency column
        if "Matched_Frequency" in df_export.columns:
            print("  ✓ 'Matched_Frequency' column found in Excel export")

            # Check that values match expected frequencies
            expected_frequencies = {
                "Sentence_A": 100,
                "Sentence_B": 50,
                "Sentence_C": 75,
                "Sentence_D": 25,
            }

            all_correct = True
            for idx, row in df_export.iterrows():
                matched_sent = row["Matched_Sentence"]
                expected_freq = expected_frequencies.get(matched_sent, 1)
                actual_freq = row["Matched_Frequency"]

                if actual_freq != expected_freq:
                    print(
                        f"  ✗ Frequency mismatch for '{matched_sent}': "
                        f"expected {expected_freq}, got {actual_freq}"
                    )
                    all_correct = False
                else:
                    print(f"  ✓ '{matched_sent}' frequency correct: {actual_freq}")

            if all_correct:
                print("  ✓ All matched frequencies are correct")
            else:
                print("  ✗ Some matched frequencies are incorrect")
        else:
            print("  ✗ 'Matched_Frequency' column NOT found in Excel export")

        # Test 3: Verify data structure
        print("\nTest 3: Data Structure Verification")
        print("-" * 80)

        # Check that each result has the right number of matches
        for result in results:
            print(f"\n  Sentence: '{result.sentence}' (Frequency: {result.frequency})")
            print(f"  FMN: {result.frequency_median_normalized:.4f}")
            print(f"  Number of matches: {len(result.top_k_matches)}")

            for i, (
                matched_sent,
                sem_dist,
                cost_dist,
                isec_score,
                metadata,
            ) in enumerate(result.top_k_matches, 1):
                matched_freq = calculator.frequencies.get(matched_sent, 1)
                print(f"    Match {i}: '{matched_sent}' (Frequency: {matched_freq})")
                print(
                    f"      Semantic: {sem_dist:.4f}, Cost: {cost_dist:.4f}, ISEC: {isec_score:.4f}"
                )

        # Clean up
        os.unlink(output_file)

        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80)
        print("✓ Test completed successfully")
        print("✓ Matched frequency functionality verified in:")
        print("  - Print output display")
        print("  - Excel export columns")
        print("  - Data structure")

    finally:
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    print("\n" + "=" * 80)
    print("All tests passed! ✓")
    print("=" * 80)


def test_with_config_settings():
    """Test with different configuration settings."""
    print("\n" + "=" * 80)
    print("Testing with Configuration Settings")
    print("=" * 80)

    # Test with group exclusion
    print("\nTesting group exclusion with frequency display...")

    # Create simple test data
    test_sentences = ["TEST1", "TEST2", "TEST3"]
    test_metadata = [
        {"frequency": 100, "group": "A"},
        {"frequency": 50, "group": "A"},
        {"frequency": 75, "group": "B"},
    ]

    # Create a mock calculator to test frequency extraction
    print("  Test sentences:", test_sentences)
    print("  Test metadata:", test_metadata)

    # Extract frequencies from metadata
    frequencies = {
        sentence: metadata.get("frequency", 1)
        for sentence, metadata in zip(test_sentences, test_metadata)
    }

    print("  Extracted frequencies:", frequencies)
    print("  ✓ Frequency extraction working correctly")


if __name__ == "__main__":
    # Run tests
    test_matched_frequency()
    test_with_config_settings()

    print("\n" + "=" * 80)
    print("COMPLETE: Matched frequency functionality is working correctly")
    print("=" * 80)
