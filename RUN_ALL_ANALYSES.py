# Run All ISEC Analyses
# Comprehensive script to run all analyses and generate all outputs

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Run all ISEC analyses."""
    print("ISEC Comprehensive Analysis Suite")
    print("=" * 50)
    print("This script will run all analyses and generate all outputs.")
    print()
    
    # Check if required files exist
    required_files = ['ISEC.py', 'parameter_sensitivity_analysis.py', 
                     'sentence_movement_demo.py']
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"ERROR: Missing required files: {missing_files}")
        return False
    
    # Run analyses in order
    analyses = [
        ("python ISEC.py", "Main ISEC Analysis"),
        ("python parameter_sensitivity_analysis.py", "Parameter Sensitivity Analysis"),
        ("python sentence_movement_demo.py", "Sentence Movement Demonstration"),
        ("python test_parameter_sensitivity.py", "Parameter Sensitivity Tests"),
    ]
    
    success_count = 0
    for command, description in analyses:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"FAILED: {description}")
    
    # Summary
    print(f"\n{'='*60}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Successfully completed: {success_count}/{len(analyses)} analyses")
    
    if success_count == len(analyses):
        print("\n✓ All analyses completed successfully!")
        print("\nGenerated files:")
        print("  - ISEC_Results.xlsx (main ISEC results)")
        print("  - semantic_weight_analysis.png (parameter sensitivity)")
        print("  - cost_factor_analysis.png (cost factor analysis)")
        print("  - operation_cost_analysis.png (operation cost analysis)")
        print("  - isec_heatmap_all_sentences.png (sentence heatmap)")
        print("  - sentence_trajectories.png (sentence movement)")
        print("  - sentence_movement_demo.png (movement demonstration)")
        print("  - sensitivity_report.xlsx (detailed parameter data)")
        print("\nNext steps:")
        print("1. Review the generated visualizations")
        print("2. Examine sensitivity_report.xlsx for detailed data")
        print("3. Check ISEC_Results.xlsx for main analysis results")
        print("4. Use PARAMETER_SENSITIVITY_OVERVIEW.md for interpretation guidance")
    else:
        print(f"\n⚠️  {len(analyses) - success_count} analyses failed!")
        print("Check the error messages above and fix issues before proceeding.")
    
    return success_count == len(analyses)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)