# Test script for parameter sensitivity analysis
# Quick verification that all components work correctly

from parameter_sensitivity_analysis import ParameterSensitivityAnalysis
import numpy as np

def test_parameter_sensitivity():
    """Test all parameter sensitivity analysis functions."""
    print("Testing Parameter Sensitivity Analysis...")
    
    # Initialize analysis
    analysis = ParameterSensitivityAnalysis()
    
    # Test semantic weight sweep
    print("\n1. Testing semantic weight sweep...")
    weights = [0.0, 0.5, 1.0]
    df_semantic = analysis.analyze_semantic_weight_sweep(weights)
    print(f"✓ Semantic weight sweep completed ({len(df_semantic)} rows)")
    print(df_semantic[['Semantic_Weight', 'Closest_Match', 'Match_ISEC']].head())
    
    # Test cost factor sweep
    print("\n2. Testing cost factor sweep...")
    factors = [0.0, 0.1, 0.5]
    df_cost = analysis.analyze_cost_factor_sweep(factors)
    print(f"✓ Cost factor sweep completed ({len(df_cost)} rows)")
    print(df_cost[['Cost_Factor', 'Closest_Match', 'Match_ISEC']].head())
    
    # Test operation cost sweep
    print("\n3. Testing operation cost sweep...")
    costs = [0.5, 1.0, 1.5]
    df_operation = analysis.analyze_operation_cost_sweep(costs)
    print(f"✓ Operation cost sweep completed ({len(df_operation)} rows)")
    print(df_operation[['Operation_Cost', 'Closest_Match', 'Match_ISEC']].head())
    
    # Test all sentences analysis
    print("\n4. Testing all sentences analysis...")
    df_all = analysis.analyze_all_sentences_across_weights([0.0, 0.5, 1.0])
    print(f"✓ All sentences analysis completed ({len(df_all)} rows)")
    print(df_all[['Semantic_Weight', 'Sentence', 'Overall_ISEC']].head())
    
    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    test_parameter_sensitivity()