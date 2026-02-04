# Comprehensive Parameter Analysis for ISEC
# Analyze interactions between all ISEC parameters

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

from config import Config
from ISEC import ISECCalculator
from matriz_costo_caracteres import EditCostCalculator


class ComprehensiveParameterAnalysis:
    """Analyze interactions between all ISEC parameters."""
    
    def __init__(self, query_sentence: str = None):
        """
        Initialize comprehensive parameter analysis.
        
        Args:
            query_sentence: Sentence to analyze (uses first if None)
        """
        self.base_calculator = ISECCalculator()
        self.query_sentence = query_sentence or self.base_calculator.sentences[0]
        self.frequency = self.base_calculator.frequencies.get(self.query_sentence, 1)
        
        print(f"Query Sentence: '{self.query_sentence}'")
        print(f"Frequency: {self.frequency}\n")
    
    def analyze_parameter_interactions(self) -> pd.DataFrame:
        """
        Analyze interactions between semantic weight and substitution cost.
        
        Returns:
            DataFrame with interaction results
        """
        # Parameter ranges
        semantic_weights = np.linspace(0.0, 1.0, 6)  # 0.0, 0.2, 0.4, 0.6, 0.8, 1.0
        substitution_costs = np.linspace(0.5, 2.0, 6)  # 0.5, 0.8, 1.1, 1.4, 1.7, 2.0
        
        results = []
        
        for sem_weight in semantic_weights:
            for sub_cost in substitution_costs:
                # Create new calculator with modified parameters
                calculator = ISECCalculator(semantic_weight=sem_weight)
                
                # Update cost calculator
                calculator.cost_calculator = EditCostCalculator(
                    default_substitution_cost=sub_cost,
                    default_insertion_cost=Config.DEFAULT_INSERTION_COST,
                    default_deletion_cost=Config.DEFAULT_DELETION_COST,
                    default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
                )
                calculator.cost_calculator.operation_cost_factor = Config.COST_FACTOR_PENALIZATION
                
                # Setup character matrices
                all_chars = set()
                for s in calculator.sentences:
                    all_chars.update(s)
                if all_chars:
                    calculator.cost_calculator.setup_characters(list(all_chars))
                
                # Calculate ISEC
                result = calculator.calculate_isec(self.query_sentence, self.frequency)
                
                # Get overall ISEC
                results.append({
                    'Semantic_Weight': sem_weight,
                    'Substitution_Cost': sub_cost,
                    'Overall_ISEC': result.isec_score if result.isec_score != float('inf') else 0,
                    'Avg_Semantic_Dist': result.avg_semantic_distance,
                    'Avg_Cost_Dist': result.avg_cost_distance,
                })
        
        return pd.DataFrame(results)
    
    def analyze_three_way_interactions(self) -> pd.DataFrame:
        """
        Analyze three-way interactions between semantic weight, substitution cost, and cost factor.
        
        Returns:
            DataFrame with three-way interaction results
        """
        # Parameter ranges
        semantic_weights = np.linspace(0.0, 1.0, 4)  # 0.0, 0.33, 0.67, 1.0
        substitution_costs = np.linspace(0.5, 2.0, 4)  # 0.5, 1.0, 1.5, 2.0
        cost_factors = np.linspace(0.0, 0.3, 4)  # 0.0, 0.1, 0.2, 0.3
        
        results = []
        
        for sem_weight in semantic_weights:
            for sub_cost in substitution_costs:
                for cost_factor in cost_factors:
                    # Create new calculator with modified parameters
                    calculator = ISECCalculator(semantic_weight=sem_weight)
                    
                    # Update cost calculator
                    calculator.cost_calculator = EditCostCalculator(
                        default_substitution_cost=sub_cost,
                        default_insertion_cost=Config.DEFAULT_INSERTION_COST,
                        default_deletion_cost=Config.DEFAULT_DELETION_COST,
                        default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
                    )
                    calculator.cost_calculator.operation_cost_factor = cost_factor
                    
                    # Setup character matrices
                    all_chars = set()
                    for s in calculator.sentences:
                        all_chars.update(s)
                    if all_chars:
                        calculator.cost_calculator.setup_characters(list(all_chars))
                    
                    # Calculate ISEC
                    result = calculator.calculate_isec(self.query_sentence, self.frequency)
                    
                    # Get overall ISEC
                    results.append({
                        'Semantic_Weight': sem_weight,
                        'Substitution_Cost': sub_cost,
                        'Cost_Factor': cost_factor,
                        'Overall_ISEC': result.isec_score if result.isec_score != float('inf') else 0,
                        'Avg_Semantic_Dist': result.avg_semantic_distance,
                        'Avg_Cost_Dist': result.avg_cost_distance,
                    })
        
        return pd.DataFrame(results)
    
    def plot_parameter_interaction_heatmap(self, df: pd.DataFrame) -> None:
        """
        Plot heatmap showing ISEC scores for semantic weight vs substitution cost.
        
        Args:
            df: Results DataFrame from analyze_parameter_interactions
        """
        # Pivot for heatmap
        pivot_df = df.pivot(index='Substitution_Cost', columns='Semantic_Weight', values='Overall_ISEC')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        sns.heatmap(pivot_df, annot=True, fmt='.3f', cmap='RdYlGn_r', 
                   cbar_kws={'label': 'Overall ISEC Score'}, ax=ax)
        
        ax.set_title('ISEC Parameter Interaction Heatmap\n(Rows: Substitution Cost, Columns: Semantic Weight)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Semantic Weight (0=100% Morphologic, 1=100% Semantic)', fontsize=11)
        ax.set_ylabel('Substitution Cost', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('parameter_interaction_heatmap.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: parameter_interaction_heatmap.png")
        plt.show()
    
    def plot_3d_parameter_interaction(self, df: pd.DataFrame) -> None:
        """
        Create 3D plot showing semantic weight, substitution cost, and ISEC score.
        
        Args:
            df: Results DataFrame from analyze_parameter_interactions
        """
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Scatter plot with color mapping to ISEC score
        scatter = ax.scatter(df['Semantic_Weight'], df['Substitution_Cost'], df['Overall_ISEC'], 
                           c=df['Overall_ISEC'], cmap='viridis', s=150)
        
        ax.set_xlabel('Semantic Weight', fontsize=11)
        ax.set_ylabel('Substitution Cost', fontsize=11)
        ax.set_zlabel('Overall ISEC Score', fontsize=11)
        ax.set_title('3D Parameter Interaction\n(X: Semantic Weight, Y: Substitution Cost, Z: ISEC Score)', 
                    fontsize=14, fontweight='bold')
        
        # Add color bar
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.5, aspect=5)
        cbar.set_label('Overall ISEC Score', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('3d_parameter_interaction.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: 3d_parameter_interaction.png")
        plt.show()
    
    def plot_contour_interaction(self, df: pd.DataFrame) -> None:
        """
        Create contour plot showing parameter interactions.
        
        Args:
            df: Results DataFrame from analyze_parameter_interactions
        """
        # Pivot for contour plot
        pivot_df = df.pivot(index='Substitution_Cost', columns='Semantic_Weight', values='Overall_ISEC')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create contour plot
        contour = ax.contour(pivot_df.columns, pivot_df.index, pivot_df.values, levels=15, colors='black', alpha=0.5)
        contourf = ax.contourf(pivot_df.columns, pivot_df.index, pivot_df.values, levels=15, cmap='RdYlGn_r')
        
        # Add labels
        ax.clabel(contour, inline=True, fontsize=10)
        ax.set_xlabel('Semantic Weight', fontsize=12)
        ax.set_ylabel('Substitution Cost', fontsize=12)
        ax.set_title('ISEC Score Contour Plot\n(Lines show equal ISEC score levels)', 
                    fontsize=14, fontweight='bold')
        
        # Add color bar
        cbar = plt.colorbar(contourf, ax=ax)
        cbar.set_label('Overall ISEC Score', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('parameter_contour_plot.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: parameter_contour_plot.png")
        plt.show()
    
    def plot_parameter_sensitivity_comparison(self) -> None:
        """
        Compare sensitivity of ISEC to different parameters.
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle(f'ISEC Parameter Sensitivity Comparison\nQuery: "{self.query_sentence}"', 
                     fontsize=16, fontweight='bold')
        
        # 1. Semantic weight sensitivity
        semantic_weights = np.linspace(0.0, 1.0, 11)
        semantic_scores = []
        for weight in semantic_weights:
            calculator = ISECCalculator(semantic_weight=weight)
            result = calculator.calculate_isec(self.query_sentence, self.frequency)
            semantic_scores.append(result.isec_score if result.isec_score != float('inf') else 0)
        
        ax1 = axes[0, 0]
        ax1.plot(semantic_weights, semantic_scores, marker='o', linewidth=2.5, markersize=8, color='blue')
        ax1.set_xlabel('Semantic Weight', fontsize=11)
        ax1.set_ylabel('Overall ISEC Score', fontsize=11)
        ax1.set_title('Semantic Weight Sensitivity')
        ax1.grid(True, alpha=0.3)
        
        # 2. Substitution cost sensitivity
        sub_costs = np.linspace(0.5, 2.0, 11)
        sub_scores = []
        for cost in sub_costs:
            calculator = ISECCalculator()
            calculator.cost_calculator = EditCostCalculator(
                default_substitution_cost=cost,
                default_insertion_cost=Config.DEFAULT_INSERTION_COST,
                default_deletion_cost=Config.DEFAULT_DELETION_COST,
                default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
            )
            calculator.cost_calculator.operation_cost_factor = Config.COST_FACTOR_PENALIZATION
            
            # Setup character matrices
            all_chars = set()
            for s in calculator.sentences:
                all_chars.update(s)
            if all_chars:
                calculator.cost_calculator.setup_characters(list(all_chars))
            
            result = calculator.calculate_isec(self.query_sentence, self.frequency)
            sub_scores.append(result.isec_score if result.isec_score != float('inf') else 0)
        
        ax2 = axes[0, 1]
        ax2.plot(sub_costs, sub_scores, marker='s', linewidth=2.5, markersize=8, color='red')
        ax2.set_xlabel('Substitution Cost', fontsize=11)
        ax2.set_ylabel('Overall ISEC Score', fontsize=11)
        ax2.set_title('Substitution Cost Sensitivity')
        ax2.grid(True, alpha=0.3)
        
        # 3. Cost factor sensitivity
        cost_factors = np.linspace(0.0, 0.5, 11)
        factor_scores = []
        for factor in cost_factors:
            calculator = ISECCalculator()
            calculator.cost_calculator.operation_cost_factor = factor
            result = calculator.calculate_isec(self.query_sentence, self.frequency)
            factor_scores.append(result.isec_score if result.isec_score != float('inf') else 0)
        
        ax3 = axes[1, 0]
        ax3.plot(cost_factors, factor_scores, marker='^', linewidth=2.5, markersize=8, color='green')
        ax3.set_xlabel('Cost Factor (Penalization)', fontsize=11)
        ax3.set_ylabel('Overall ISEC Score', fontsize=11)
        ax3.set_title('Cost Factor Sensitivity')
        ax3.grid(True, alpha=0.3)
        
        # 4. Combined comparison
        ax4 = axes[1, 1]
        # Normalize scores to 0-1 range for comparison
        sem_norm = np.array(semantic_scores) / max(semantic_scores) if max(semantic_scores) > 0 else semantic_scores
        sub_norm = np.array(sub_scores) / max(sub_scores) if max(sub_scores) > 0 else sub_scores
        fac_norm = np.array(factor_scores) / max(factor_scores) if max(factor_scores) > 0 else factor_scores
        
        ax4.plot(semantic_weights, sem_norm, marker='o', linewidth=2, markersize=6, 
                label='Semantic Weight', color='blue')
        ax4.plot(sub_costs, sub_norm, marker='s', linewidth=2, markersize=6, 
                label='Substitution Cost', color='red')
        ax4.plot(cost_factors, fac_norm, marker='^', linewidth=2, markersize=6, 
                label='Cost Factor', color='green')
        
        ax4.set_xlabel('Parameter Value', fontsize=11)
        ax4.set_ylabel('Normalized ISEC Score', fontsize=11)
        ax4.set_title('Parameter Sensitivity Comparison')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('parameter_sensitivity_comparison.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: parameter_sensitivity_comparison.png")
        plt.show()
    
    def generate_comprehensive_report(self, output_file: str = "comprehensive_parameter_report.xlsx") -> None:
        """
        Generate comprehensive parameter analysis report.
        
        Args:
            output_file: Output Excel filename
        """
        # Analyze parameter interactions
        df_interactions = self.analyze_parameter_interactions()
        
        # Analyze three-way interactions
        df_three_way = self.analyze_three_way_interactions()
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_interactions.to_excel(writer, sheet_name='Two_Way_Interactions', index=False)
            df_three_way.to_excel(writer, sheet_name='Three_Way_Interactions', index=False)
        
        print(f"✓ Report saved: {output_file}")
        return df_interactions, df_three_way


def main():
    """Main entry point for comprehensive parameter analysis."""
    print("=" * 90)
    print("ISEC Comprehensive Parameter Analysis")
    print("=" * 90)
    print()
    
    # Initialize analysis
    analysis = ComprehensiveParameterAnalysis()
    
    print("\n1. Analyzing parameter interactions...")
    df_interactions = analysis.analyze_parameter_interactions()
    print(f"Analyzed {len(df_interactions)} parameter combinations")
    
    print("\n2. Analyzing three-way parameter interactions...")
    df_three_way = analysis.analyze_three_way_interactions()
    print(f"Analyzed {len(df_three_way)} three-way combinations")
    
    print("\n3. Generating visualizations...")
    analysis.plot_parameter_interaction_heatmap(df_interactions)
    analysis.plot_3d_parameter_interaction(df_interactions)
    analysis.plot_contour_interaction(df_interactions)
    analysis.plot_parameter_sensitivity_comparison()
    
    print("\n4. Generating comprehensive report...")
    analysis.generate_comprehensive_report()
    
    print("\n" + "=" * 90)
    print("Comprehensive Analysis Complete!")
    print("=" * 90)
    print("\nGenerated files:")
    print("  - parameter_interaction_heatmap.png: 2D parameter interaction heatmap")
    print("  - 3d_parameter_interaction.png: 3D visualization of parameter interactions")
    print("  - parameter_contour_plot.png: Contour plot of parameter interactions")
    print("  - parameter_sensitivity_comparison.png: Comparison of parameter sensitivities")
    print("  - comprehensive_parameter_report.xlsx: Detailed data for further analysis")


if __name__ == "__main__":
    main()