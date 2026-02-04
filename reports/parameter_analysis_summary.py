# Parameter Analysis Summary
# Demonstrate key findings from parameter sensitivity analysis

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import Config
from ISEC import ISECCalculator


def demonstrate_parameter_impact():
    """Demonstrate how different parameters affect ISEC scores."""
    
    print("=" * 80)
    print("ISEC Parameter Impact Demonstration")
    print("=" * 80)
    print()
    
    # Initialize calculator
    calculator = ISECCalculator()
    query_sentence = calculator.sentences[0]
    frequency = calculator.frequencies.get(query_sentence, 1)
    
    print(f"Analyzing sentence: '{query_sentence}' (frequency: {frequency})")
    print()
    
    # 1. Semantic Weight Impact
    print("1. Semantic Weight Impact (0.0 to 1.0)")
    print("-" * 40)
    
    semantic_weights = [0.0, 0.25, 0.5, 0.75, 1.0]
    semantic_scores = []
    
    for weight in semantic_weights:
        calc = ISECCalculator(semantic_weight=weight)
        result = calc.calculate_isec(query_sentence, frequency)
        score = result.isec_score if result.isec_score != float('inf') else 0
        semantic_scores.append(score)
        print(f"   Weight {weight:4.2f}: ISEC = {score:8.4f}")
    
    print()
    
    # 2. Substitution Cost Impact
    print("2. Substitution Cost Impact (0.5 to 2.0)")
    print("-" * 40)
    
    sub_costs = [0.5, 1.0, 1.5, 2.0]
    sub_scores = []
    
    for cost in sub_costs:
        calc = ISECCalculator()
        # Update cost calculator
        from matriz_costo_caracteres import EditCostCalculator
        calc.cost_calculator = EditCostCalculator(
            default_substitution_cost=cost,
            default_insertion_cost=Config.DEFAULT_INSERTION_COST,
            default_deletion_cost=Config.DEFAULT_DELETION_COST,
            default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
        )
        calc.cost_calculator.operation_cost_factor = Config.COST_FACTOR_PENALIZATION
        
        # Setup character matrices
        all_chars = set()
        for s in calc.sentences:
            all_chars.update(s)
        if all_chars:
            calc.cost_calculator.setup_characters(list(all_chars))
        
        result = calc.calculate_isec(query_sentence, frequency)
        score = result.isec_score if result.isec_score != float('inf') else 0
        sub_scores.append(score)
        print(f"   Cost {cost:4.1f}: ISEC = {score:8.4f}")
    
    print()
    
    # 3. Cost Factor Impact
    print("3. Cost Factor Impact (0.0 to 0.3)")
    print("-" * 40)
    
    cost_factors = [0.0, 0.1, 0.2, 0.3]
    factor_scores = []
    
    for factor in cost_factors:
        calc = ISECCalculator()
        calc.cost_calculator.operation_cost_factor = factor
        result = calc.calculate_isec(query_sentence, frequency)
        score = result.isec_score if result.isec_score != float('inf') else 0
        factor_scores.append(score)
        print(f"   Factor {factor:4.1f}: ISEC = {score:8.4f}")
    
    print()
    
    # 4. Key Insights
    print("4. Key Insights")
    print("-" * 40)
    
    # Find most sensitive parameter
    sem_range = max(semantic_scores) - min(semantic_scores) if semantic_scores else 0
    sub_range = max(sub_scores) - min(sub_scores) if sub_scores else 0
    fac_range = max(factor_scores) - min(factor_scores) if factor_scores else 0
    
    sensitivity = {
        'Semantic Weight': sem_range,
        'Substitution Cost': sub_range,
        'Cost Factor': fac_range
    }
    
    most_sensitive = max(sensitivity, key=sensitivity.get)
    print(f"   Most sensitive parameter: {most_sensitive}")
    print(f"   Sensitivity range: {sensitivity[most_sensitive]:.4f}")
    
    # ISEC interpretation
    avg_score = np.mean([score for score in semantic_scores if score > 0])
    if avg_score > 5.0:
        interpretation = "sentences are generally similar (high ISEC)"
    elif avg_score > 2.0:
        interpretation = "sentences show moderate similarity"
    else:
        interpretation = "sentences are generally dissimilar (low ISEC)"
    
    print(f"   Average ISEC score: {avg_score:.4f} → {interpretation}")
    
    print()
    
    # 5. Recommendations
    print("5. Parameter Tuning Recommendations")
    print("-" * 40)
    
    if sem_range > sub_range and sem_range > fac_range:
        print("   • Semantic weight has strongest impact")
        print("   • For more semantic focus: increase semantic weight (>0.5)")
        print("   • For more structural focus: decrease semantic weight (<0.5)")
    
    if sub_range > sem_range and sub_range > fac_range:
        print("   • Substitution cost has strongest impact")
        print("   • For stricter character matching: increase substitution cost (>1.0)")
        print("   • For more flexible matching: decrease substitution cost (<1.0)")
    
    if fac_range > sem_range and fac_range > sub_range:
        print("   • Cost factor has strongest impact")
        print("   • For heavier penalization of structural changes: increase cost factor (>0.1)")
        print("   • For balanced treatment: use default cost factor (0.1)")
    
    print()
    print("=" * 80)
    print("For detailed analysis, run:")
    print("  python parameter_sensitivity_analysis.py")
    print("  python cost_sensitivity_analysis.py") 
    print("  python comprehensive_parameter_analysis.py")
    print("=" * 80)


def create_parameter_impact_chart():
    """Create a visual summary of parameter impacts."""
    
    # Get data (simplified version)
    calculator = ISECCalculator()
    query_sentence = calculator.sentences[0]
    frequency = calculator.frequencies.get(query_sentence, 1)
    
    # Semantic weight impact
    semantic_weights = np.linspace(0.0, 1.0, 11)
    semantic_scores = []
    for weight in semantic_weights:
        calc = ISECCalculator(semantic_weight=weight)
        result = calc.calculate_isec(query_sentence, frequency)
        score = result.isec_score if result.isec_score != float('inf') else 0
        semantic_scores.append(score)
    
    # Substitution cost impact
    sub_costs = np.linspace(0.5, 2.0, 11)
    sub_scores = []
    for cost in sub_costs:
        calc = ISECCalculator()
        from matriz_costo_caracteres import EditCostCalculator
        calc.cost_calculator = EditCostCalculator(
            default_substitution_cost=cost,
            default_insertion_cost=Config.DEFAULT_INSERTION_COST,
            default_deletion_cost=Config.DEFAULT_DELETION_COST,
            default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
        )
        calc.cost_calculator.operation_cost_factor = Config.COST_FACTOR_PENALIZATION
        
        # Setup character matrices
        all_chars = set()
        for s in calc.sentences:
            all_chars.update(s)
        if all_chars:
            calc.cost_calculator.setup_characters(list(all_chars))
        
        result = calc.calculate_isec(query_sentence, frequency)
        score = result.isec_score if result.isec_score != float('inf') else 0
        sub_scores.append(score)
    
    # Cost factor impact
    cost_factors = np.linspace(0.0, 0.3, 11)
    factor_scores = []
    for factor in cost_factors:
        calc = ISECCalculator()
        calc.cost_calculator.operation_cost_factor = factor
        result = calc.calculate_isec(query_sentence, frequency)
        score = result.isec_score if result.isec_score != float('inf') else 0
        factor_scores.append(score)
    
    # Create plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f'ISEC Parameter Impact Summary\n(Query: "{query_sentence}")', 
                 fontsize=14, fontweight='bold')
    
    # Semantic weight
    axes[0].plot(semantic_weights, semantic_scores, marker='o', linewidth=2, 
                markersize=6, color='blue')
    axes[0].set_xlabel('Semantic Weight')
    axes[0].set_ylabel('ISEC Score')
    axes[0].set_title('Semantic Weight Impact')
    axes[0].grid(True, alpha=0.3)
    
    # Substitution cost
    axes[1].plot(sub_costs, sub_scores, marker='s', linewidth=2, 
                markersize=6, color='red')
    axes[1].set_xlabel('Substitution Cost')
    axes[1].set_ylabel('ISEC Score')
    axes[1].set_title('Substitution Cost Impact')
    axes[1].grid(True, alpha=0.3)
    
    # Cost factor
    axes[2].plot(cost_factors, factor_scores, marker='^', linewidth=2, 
                markersize=6, color='green')
    axes[2].set_xlabel('Cost Factor')
    axes[2].set_ylabel('ISEC Score')
    axes[2].set_title('Cost Factor Impact')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('parameter_impact_summary.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: parameter_impact_summary.png")
    plt.show()


def main():
    """Main function to demonstrate parameter impacts."""
    demonstrate_parameter_impact()
    create_parameter_impact_chart()


if __name__ == "__main__":
    main()