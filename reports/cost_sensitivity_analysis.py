# Cost Parameter Sensitivity Analysis for ISEC
# Analyze how operation cost parameters affect ISEC scores

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import Config
from ISEC import ISECCalculator
from matriz_costo_caracteres import EditCostCalculator


class CostSensitivityAnalysis:
    """Analyze how operation cost parameters affect ISEC scores."""
    
    def __init__(self, query_sentence: str = None):
        """
        Initialize cost sensitivity analysis.
        
        Args:
            query_sentence: Sentence to analyze (uses first if None)
        """
        self.base_calculator = ISECCalculator()
        self.query_sentence = query_sentence or self.base_calculator.sentences[0]
        self.frequency = self.base_calculator.frequencies.get(self.query_sentence, 1)
        
        print(f"Query Sentence: '{self.query_sentence}'")
        print(f"Frequency: {self.frequency}\n")
    
    def analyze_substitution_cost_sweep(self, costs: List[float] = None) -> pd.DataFrame:
        """
        Analyze how ISEC scores change with substitution cost variation.
        
        Args:
            costs: List of substitution costs to test
            
        Returns:
            DataFrame with results
        """
        if costs is None:
            costs = np.linspace(0.5, 2.0, 16)  # 0.5 to 2.0 in 0.1 steps
        
        results = []
        
        for cost in costs:
            # Create new calculator with modified substitution cost
            calculator = ISECCalculator()
            
            # Update cost calculator with new substitution cost
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
            
            # Calculate ISEC
            result = calculator.calculate_isec(self.query_sentence, self.frequency)
            
            # Get top matches info
            top_match = result.top_k_matches[0] if result.top_k_matches else None
            if top_match:
                matched_sent, sem_dist, cost_dist, match_isec = top_match
                results.append({
                    'Substitution_Cost': cost,
                    'Closest_Match': matched_sent,
                    'Match_ISEC': match_isec,
                    'Overall_ISEC': result.isec_score,
                    'Avg_Semantic_Dist': result.avg_semantic_distance,
                    'Avg_Cost_Dist': result.avg_cost_distance,
                })
        
        return pd.DataFrame(results)
    
    def analyze_cost_factor_sweep(self, factors: List[float] = None) -> pd.DataFrame:
        """
        Analyze how ISEC scores change with cost factor (penalization) variation.
        
        Args:
            factors: List of cost factors to test
            
        Returns:
            DataFrame with results
        """
        if factors is None:
            factors = np.linspace(0.0, 0.5, 11)  # 0.0 to 0.5 in 0.05 steps
        
        results = []
        
        for factor in factors:
            # Create new calculator with modified cost factor
            calculator = ISECCalculator()
            
            # Update cost factor
            calculator.cost_calculator.operation_cost_factor = factor
            
            # Calculate ISEC
            result = calculator.calculate_isec(self.query_sentence, self.frequency)
            
            # Get top matches info
            top_match = result.top_k_matches[0] if result.top_k_matches else None
            if top_match:
                matched_sent, sem_dist, cost_dist, match_isec = top_match
                results.append({
                    'Cost_Factor': factor,
                    'Closest_Match': matched_sent,
                    'Match_ISEC': match_isec,
                    'Overall_ISEC': result.isec_score,
                    'Avg_Semantic_Dist': result.avg_semantic_distance,
                    'Avg_Cost_Dist': result.avg_cost_distance,
                })
        
        return pd.DataFrame(results)
    
    def analyze_all_costs_sweep(self) -> pd.DataFrame:
        """
        Analyze how ISEC scores change with all operation cost variations.
        
        Returns:
            DataFrame with results for all cost types
        """
        # Test ranges for different cost types
        substitution_costs = np.linspace(0.5, 2.0, 4)  # 0.5, 1.0, 1.5, 2.0
        insertion_costs = np.linspace(0.5, 2.0, 4)
        deletion_costs = np.linspace(0.5, 2.0, 4)
        
        results = []
        
        for sub_cost in substitution_costs:
            for ins_cost in insertion_costs:
                for del_cost in deletion_costs:
                    # Create new calculator with modified costs
                    calculator = ISECCalculator()
                    
                    # Update cost calculator
                    calculator.cost_calculator = EditCostCalculator(
                        default_substitution_cost=sub_cost,
                        default_insertion_cost=ins_cost,
                        default_deletion_cost=del_cost,
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
                        'Substitution_Cost': sub_cost,
                        'Insertion_Cost': ins_cost,
                        'Deletion_Cost': del_cost,
                        'Overall_ISEC': result.isec_score if result.isec_score != float('inf') else 0,
                        'Avg_Semantic_Dist': result.avg_semantic_distance,
                        'Avg_Cost_Dist': result.avg_cost_distance,
                    })
        
        return pd.DataFrame(results)
    
    def plot_substitution_cost_analysis(self, df: pd.DataFrame) -> None:
        """
        Plot ISEC scores vs substitution cost.
        
        Args:
            df: Results DataFrame from analyze_substitution_cost_sweep
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Substitution Cost Sensitivity Analysis\nQuery: '{self.query_sentence}'", 
                     fontsize=14, fontweight='bold')
        
        # Plot 1: Match ISEC score
        ax1 = axes[0, 0]
        ax1.plot(df['Substitution_Cost'], df['Match_ISEC'], marker='o', linewidth=2, markersize=8)
        ax1.set_xlabel('Substitution Cost', fontsize=11)
        ax1.set_ylabel('Closest Match ISEC Score', fontsize=11)
        ax1.set_title('Individual Match ISEC Score vs Substitution Cost')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Overall ISEC score
        ax2 = axes[0, 1]
        ax2.plot(df['Substitution_Cost'], df['Overall_ISEC'], marker='s', linewidth=2, 
                 markersize=8, color='orange')
        ax2.set_xlabel('Substitution Cost', fontsize=11)
        ax2.set_ylabel('Overall ISEC Score', fontsize=11)
        ax2.set_title('Overall ISEC Score vs Substitution Cost')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Distance components
        ax3 = axes[1, 0]
        ax3.plot(df['Substitution_Cost'], df['Avg_Semantic_Dist'], marker='^', 
                label='Avg Semantic Distance', linewidth=2, markersize=8)
        ax3.plot(df['Substitution_Cost'], df['Avg_Cost_Dist'], marker='v', 
                label='Avg Cost Distance', linewidth=2, markersize=8)
        ax3.set_xlabel('Substitution Cost', fontsize=11)
        ax3.set_ylabel('Distance', fontsize=11)
        ax3.set_title('Distance Components vs Substitution Cost')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Table of closest matches
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        table_data = []
        for idx, row in df.iterrows():
            table_data.append([
                f"{row['Substitution_Cost']:.1f}",
                row['Closest_Match'][:15],  # Truncate long names
                f"{row['Match_ISEC']:.4f}",
                f"{row['Overall_ISEC']:.4f}"
            ])
        
        table = ax4.table(cellText=table_data,
                         colLabels=['Sub Cost', 'Closest Match', 'Match ISEC', 'Overall ISEC'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.2, 0.3, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        plt.tight_layout()
        plt.savefig('substitution_cost_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: substitution_cost_analysis.png")
        plt.show()
    
    def plot_cost_factor_analysis(self, df: pd.DataFrame) -> None:
        """
        Plot ISEC scores vs cost factor.
        
        Args:
            df: Results DataFrame from analyze_cost_factor_sweep
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f"Cost Factor Sensitivity Analysis\nQuery: '{self.query_sentence}'", 
                     fontsize=14, fontweight='bold')
        
        # Plot 1: Overall ISEC score
        ax1 = axes[0]
        ax1.plot(df['Cost_Factor'], df['Overall_ISEC'], marker='o', linewidth=2, 
                 markersize=8, color='green')
        ax1.set_xlabel('Cost Factor (Penalization)', fontsize=11)
        ax1.set_ylabel('Overall ISEC Score', fontsize=11)
        ax1.set_title('Overall ISEC Score vs Cost Factor')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Cost distance
        ax2 = axes[1]
        ax2.plot(df['Cost_Factor'], df['Avg_Cost_Dist'], marker='s', linewidth=2, 
                 markersize=8, color='red')
        ax2.set_xlabel('Cost Factor (Penalization)', fontsize=11)
        ax2.set_ylabel('Average Cost Distance', fontsize=11)
        ax2.set_title('Cost Distance vs Cost Factor')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('cost_factor_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: cost_factor_analysis.png")
        plt.show()
    
    def plot_3d_cost_analysis(self, df: pd.DataFrame) -> None:
        """
        Create 3D plot showing how substitution, insertion, and deletion costs interact.
        
        Args:
            df: Results DataFrame from analyze_all_costs_sweep
        """
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Scatter plot with color mapping to ISEC score
        scatter = ax.scatter(df['Substitution_Cost'], df['Insertion_Cost'], df['Deletion_Cost'], 
                           c=df['Overall_ISEC'], cmap='viridis', s=100)
        
        ax.set_xlabel('Substitution Cost', fontsize=11)
        ax.set_ylabel('Insertion Cost', fontsize=11)
        ax.set_zlabel('Deletion Cost', fontsize=11)
        ax.set_title('3D Cost Parameter Interaction\n(Color = Overall ISEC Score)', 
                    fontsize=14, fontweight='bold')
        
        # Add color bar
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.5, aspect=5)
        cbar.set_label('Overall ISEC Score', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('3d_cost_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: 3d_cost_analysis.png")
        plt.show()
    
    def generate_cost_report(self, output_file: str = "cost_sensitivity_report.xlsx") -> None:
        """
        Generate comprehensive cost sensitivity analysis report.
        
        Args:
            output_file: Output Excel filename
        """
        # Analyze substitution cost sweep
        df_substitution = self.analyze_substitution_cost_sweep()
        
        # Analyze cost factor sweep
        df_factor = self.analyze_cost_factor_sweep()
        
        # Analyze all costs
        df_all = self.analyze_all_costs_sweep()
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_substitution.to_excel(writer, sheet_name='Substitution_Cost_Sweep', index=False)
            df_factor.to_excel(writer, sheet_name='Cost_Factor_Sweep', index=False)
            df_all.to_excel(writer, sheet_name='All_Costs_Sweep', index=False)
        
        print(f"✓ Report saved: {output_file}")
        return df_substitution, df_factor, df_all


def main():
    """Main entry point for cost parameter sensitivity analysis."""
    print("=" * 90)
    print("ISEC Cost Parameter Sensitivity Analysis")
    print("=" * 90)
    print()
    
    # Initialize analysis
    analysis = CostSensitivityAnalysis()
    
    print("\n1. Analyzing substitution cost sensitivity...")
    df_substitution = analysis.analyze_substitution_cost_sweep()
    print(df_substitution.head(10))
    
    print("\n2. Analyzing cost factor sensitivity...")
    df_factor = analysis.analyze_cost_factor_sweep()
    print(df_factor.head(10))
    
    print("\n3. Analyzing all cost parameters...")
    df_all = analysis.analyze_all_costs_sweep()
    print(f"Analyzed {len(df_all)} cost combinations")
    
    print("\n4. Generating visualizations...")
    analysis.plot_substitution_cost_analysis(df_substitution)
    analysis.plot_cost_factor_analysis(df_factor)
    analysis.plot_3d_cost_analysis(df_all)
    
    print("\n5. Generating comprehensive report...")
    analysis.generate_cost_report()
    
    print("\n" + "=" * 90)
    print("Cost Analysis Complete!")
    print("=" * 90)
    print("\nGenerated files:")
    print("  - substitution_cost_analysis.png: Substitution cost sensitivity")
    print("  - cost_factor_analysis.png: Cost factor sensitivity")
    print("  - 3d_cost_analysis.png: 3D visualization of cost interactions")
    print("  - cost_sensitivity_report.xlsx: Detailed data for further analysis")


if __name__ == "__main__":
    main()