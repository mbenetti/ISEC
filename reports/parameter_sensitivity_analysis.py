# Parameter Sensitivity Analysis for ISEC
# Analyze how parameter changes affect ISEC scores and sentence rankings

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config import Config
from ISEC import ISECCalculator
from matriz_costo_caracteres import EditCostCalculator, load_custom_costs_from_excel


class ParameterSensitivityAnalysis:
    """Analyze how ISEC parameters affect sentence rankings and scores."""
    
    def __init__(self, query_sentence: str = None):
        """
        Initialize sensitivity analysis.
        
        Args:
            query_sentence: Sentence to analyze (uses first if None)
        """
        # Initialize calculator once - embeddings are cached in Chroma
        self.calculator = ISECCalculator()
        self.query_sentence = query_sentence or self.calculator.sentences[0]
        self.frequency = self.calculator.frequencies.get(self.query_sentence, 1)
        
        print(f"Query Sentence: '{self.query_sentence}'")
        print(f"Frequency: {self.frequency}\n")
    
    def analyze_semantic_weight_sweep(self, weights: List[float] = None) -> pd.DataFrame:
        """
        Analyze how ISEC scores change with semantic weight variation.
        
        Args:
            weights: List of semantic weights to test (0.0 to 1.0)
            
        Returns:
            DataFrame with results
        """
        if weights is None:
            weights = np.linspace(0.0, 1.0, 11)  # 0.0, 0.1, 0.2, ..., 1.0
        
        results = []
        
        for weight in weights:
            # Temporarily change weight (no recalculation of embeddings)
            original_weight = self.calculator.semantic_weight
            self.calculator.semantic_weight = weight
            self.calculator.morphologic_weight = 1.0 - weight
            
            # Calculate ISEC (reuses existing embeddings)
            result = self.calculator.calculate_isec(self.query_sentence, self.frequency)
            
            # Restore original
            self.calculator.semantic_weight = original_weight
            self.calculator.morphologic_weight = 1.0 - original_weight
            
            # Get top matches info
            top_match = result.top_k_matches[0] if result.top_k_matches else None
            if top_match:
                matched_sent, sem_dist, cost_dist, match_isec = top_match
                results.append({
                    'Semantic_Weight': weight,
                    'Morphologic_Weight': 1.0 - weight,
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
            factors = np.linspace(0.0, 1.0, 11)
        
        results = []
        
        # Store original factor
        original_factor = Config.COST_FACTOR_PENALIZATION
        
        for factor in factors:
            # Temporarily change factor in config
            Config.COST_FACTOR_PENALIZATION = factor
            
            # Recalculate ISEC with new factor (reuses existing embeddings)
            result = self.calculator.calculate_isec(self.query_sentence, self.frequency)
            
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
        
        # Restore original factor
        Config.COST_FACTOR_PENALIZATION = original_factor
        
        return pd.DataFrame(results)
    
    def analyze_operation_cost_sweep(self, cost_values: List[float] = None) -> pd.DataFrame:
        """
        Analyze how ISEC scores change with operation cost variations.
        
        Args:
            cost_values: List of operation cost values to test
            
        Returns:
            DataFrame with results
        """
        if cost_values is None:
            cost_values = np.linspace(0.5, 2.0, 11)
        
        results = []
        
        # Store original costs
        original_costs = {
            'sub': Config.DEFAULT_SUBSTITUTION_COST,
            'ins': Config.DEFAULT_INSERTION_COST,
            'del': Config.DEFAULT_DELETION_COST,
            'trans': Config.DEFAULT_TRANSPOSITION_COST
        }
        
        for cost in cost_values:
            # Temporarily change all operation costs
            Config.DEFAULT_SUBSTITUTION_COST = cost
            Config.DEFAULT_INSERTION_COST = cost
            Config.DEFAULT_DELETION_COST = cost
            Config.DEFAULT_TRANSPOSITION_COST = cost
            
            # Reinitialize cost calculator with new costs (reuses embeddings)
            self._reinitialize_cost_calculator()
            
            # Calculate ISEC with new operation costs
            result = self.calculator.calculate_isec(self.query_sentence, self.frequency)
            
            # Get top matches info
            top_match = result.top_k_matches[0] if result.top_k_matches else None
            if top_match:
                matched_sent, sem_dist, cost_dist, match_isec = top_match
                results.append({
                    'Operation_Cost': cost,
                    'Closest_Match': matched_sent,
                    'Match_ISEC': match_isec,
                    'Overall_ISEC': result.isec_score,
                    'Avg_Semantic_Dist': result.avg_semantic_distance,
                    'Avg_Cost_Dist': result.avg_cost_distance,
                })
        
        # Restore original costs
        Config.DEFAULT_SUBSTITUTION_COST = original_costs['sub']
        Config.DEFAULT_INSERTION_COST = original_costs['ins']
        Config.DEFAULT_DELETION_COST = original_costs['del']
        Config.DEFAULT_TRANSPOSITION_COST = original_costs['trans']
        
        # Reinitialize with original costs
        self._reinitialize_cost_calculator()
        
        return pd.DataFrame(results)
    
    def _reinitialize_cost_calculator(self) -> None:
        """
        Reinitialize the cost calculator with current configuration.
        """
        # Reinitialize EditCostCalculator
        self.calculator.cost_calculator = EditCostCalculator(
            default_substitution_cost=Config.DEFAULT_SUBSTITUTION_COST,
            default_insertion_cost=Config.DEFAULT_INSERTION_COST,
            default_deletion_cost=Config.DEFAULT_DELETION_COST,
            default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
        )
        
        # Load custom costs
        sub_costs, trans_costs = load_custom_costs_from_excel(
            self.calculator.custom_costs_file,
            char1_column=Config.COSTS_CHAR1_COLUMN,
            char2_column=Config.COSTS_CHAR2_COLUMN,
            cost_column=Config.COSTS_COST_COLUMN,
            operation_column=Config.COSTS_OPERATION_COLUMN
        )
        
        if sub_costs:
            self.calculator.cost_calculator.set_custom_costs(sub_costs, operation="substitution")
        if trans_costs:
            self.calculator.cost_calculator.set_custom_costs(trans_costs, operation="transposition")
        
        # Setup character matrices
        all_chars = set()
        for s in self.calculator.sentences:
            all_chars.update(s)
        if all_chars:
            self.calculator.cost_calculator.setup_characters(list(all_chars))
    
    def analyze_all_sentences_across_weights(self, weights: List[float] = None) -> pd.DataFrame:
        """
        Get ISEC scores for all sentences across different semantic weights.
        
        Args:
            weights: List of semantic weights to test
            
        Returns:
            DataFrame with all sentences and their ISEC scores
        """
        if weights is None:
            weights = np.linspace(0.0, 1.0, 11)
        
        results = []
        
        for weight in weights:
            # Temporarily change weight (no recalculation of embeddings)
            original_weight = self.calculator.semantic_weight
            self.calculator.semantic_weight = weight
            self.calculator.morphologic_weight = 1.0 - weight
            
            # Calculate ISEC for each sentence (reuses existing embeddings)
            for sentence in self.calculator.sentences:
                freq = self.calculator.frequencies.get(sentence, 1)
                result = self.calculator.calculate_isec(sentence, freq)
                
                results.append({
                    'Semantic_Weight': weight,
                    'Sentence': sentence,
                    'Overall_ISEC': result.isec_score if result.isec_score != float('inf') else 0,
                    'Avg_Semantic_Dist': result.avg_semantic_distance,
                    'Avg_Cost_Dist': result.avg_cost_distance,
                })
            
            # Restore original
            self.calculator.semantic_weight = original_weight
            self.calculator.morphologic_weight = 1.0 - original_weight
        
        return pd.DataFrame(results)
    
    def plot_semantic_weight_analysis(self, df: pd.DataFrame) -> None:
        """
        Plot ISEC scores vs semantic weight for top matches.
        
        Args:
            df: Results DataFrame from analyze_semantic_weight_sweep
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Semantic Weight Sensitivity Analysis\nQuery: '{self.query_sentence}'", 
                     fontsize=14, fontweight='bold')
        
        # Plot 1: Match ISEC score
        ax1 = axes[0, 0]
        ax1.plot(df['Semantic_Weight'], df['Match_ISEC'], marker='o', linewidth=2, markersize=8)
        ax1.set_xlabel('Semantic Weight', fontsize=11)
        ax1.set_ylabel('Closest Match ISEC Score', fontsize=11)
        ax1.set_title('Individual Match ISEC Score vs Semantic Weight')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Overall ISEC score
        ax2 = axes[0, 1]
        ax2.plot(df['Semantic_Weight'], df['Overall_ISEC'], marker='s', linewidth=2, 
                 markersize=8, color='orange')
        ax2.set_xlabel('Semantic Weight', fontsize=11)
        ax2.set_ylabel('Overall ISEC Score', fontsize=11)
        ax2.set_title('Overall ISEC Score vs Semantic Weight')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Distance components
        ax3 = axes[1, 0]
        ax3.plot(df['Semantic_Weight'], df['Avg_Semantic_Dist'], marker='^', 
                label='Avg Semantic Distance', linewidth=2, markersize=8)
        ax3.plot(df['Semantic_Weight'], df['Avg_Cost_Dist'], marker='v', 
                label='Avg Cost Distance', linewidth=2, markersize=8)
        ax3.set_xlabel('Semantic Weight', fontsize=11)
        ax3.set_ylabel('Distance', fontsize=11)
        ax3.set_title('Distance Components vs Semantic Weight')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Table of closest matches
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        table_data = []
        for idx, row in df.iterrows():
            table_data.append([
                f"{row['Semantic_Weight']:.1f}",
                row['Closest_Match'][:15],  # Truncate long names
                f"{row['Match_ISEC']:.4f}",
                f"{row['Overall_ISEC']:.4f}"
            ])
        
        table = ax4.table(cellText=table_data,
                         colLabels=['Sem Weight', 'Closest Match', 'Match ISEC', 'Overall ISEC'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.2, 0.3, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        plt.tight_layout()
        plt.savefig('semantic_weight_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: semantic_weight_analysis.png")
        plt.show()
    
    def plot_cost_factor_analysis(self, df: pd.DataFrame) -> None:
        """
        Plot ISEC scores vs cost factor for sensitivity analysis.
        
        Args:
            df: Results DataFrame from analyze_cost_factor_sweep
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Cost Factor Sensitivity Analysis\nQuery: '{self.query_sentence}'", 
                     fontsize=14, fontweight='bold')
        
        # Plot 1: Match ISEC score
        ax1 = axes[0, 0]
        ax1.plot(df['Cost_Factor'], df['Match_ISEC'], marker='o', linewidth=2, markersize=8, color='green')
        ax1.set_xlabel('Cost Factor', fontsize=11)
        ax1.set_ylabel('Closest Match ISEC Score', fontsize=11)
        ax1.set_title('Individual Match ISEC Score vs Cost Factor')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Overall ISEC score
        ax2 = axes[0, 1]
        ax2.plot(df['Cost_Factor'], df['Overall_ISEC'], marker='s', linewidth=2, 
                 markersize=8, color='red')
        ax2.set_xlabel('Cost Factor', fontsize=11)
        ax2.set_ylabel('Overall ISEC Score', fontsize=11)
        ax2.set_title('Overall ISEC Score vs Cost Factor')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Distance components
        ax3 = axes[1, 0]
        ax3.plot(df['Cost_Factor'], df['Avg_Semantic_Dist'], marker='^', 
                label='Avg Semantic Distance', linewidth=2, markersize=8)
        ax3.plot(df['Cost_Factor'], df['Avg_Cost_Dist'], marker='v', 
                label='Avg Cost Distance', linewidth=2, markersize=8, color='purple')
        ax3.set_xlabel('Cost Factor', fontsize=11)
        ax3.set_ylabel('Distance', fontsize=11)
        ax3.set_title('Distance Components vs Cost Factor')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Table of closest matches
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        table_data = []
        for idx, row in df.iterrows():
            table_data.append([
                f"{row['Cost_Factor']:.1f}",
                row['Closest_Match'][:15],  # Truncate long names
                f"{row['Match_ISEC']:.4f}",
                f"{row['Overall_ISEC']:.4f}"
            ])
        
        table = ax4.table(cellText=table_data,
                         colLabels=['Cost Factor', 'Closest Match', 'Match ISEC', 'Overall ISEC'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.2, 0.3, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        plt.tight_layout()
        plt.savefig('cost_factor_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: cost_factor_analysis.png")
        plt.show()
    
    def plot_operation_cost_analysis(self, df: pd.DataFrame) -> None:
        """
        Plot ISEC scores vs operation cost for sensitivity analysis.
        
        Args:
            df: Results DataFrame from analyze_operation_cost_sweep
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Operation Cost Sensitivity Analysis\nQuery: '{self.query_sentence}'", 
                     fontsize=14, fontweight='bold')
        
        # Plot 1: Match ISEC score
        ax1 = axes[0, 0]
        ax1.plot(df['Operation_Cost'], df['Match_ISEC'], marker='o', linewidth=2, markersize=8, color='blue')
        ax1.set_xlabel('Operation Cost', fontsize=11)
        ax1.set_ylabel('Closest Match ISEC Score', fontsize=11)
        ax1.set_title('Individual Match ISEC Score vs Operation Cost')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Overall ISEC score
        ax2 = axes[0, 1]
        ax2.plot(df['Operation_Cost'], df['Overall_ISEC'], marker='s', linewidth=2, 
                 markersize=8, color='brown')
        ax2.set_xlabel('Operation Cost', fontsize=11)
        ax2.set_ylabel('Overall ISEC Score', fontsize=11)
        ax2.set_title('Overall ISEC Score vs Operation Cost')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Distance components
        ax3 = axes[1, 0]
        ax3.plot(df['Operation_Cost'], df['Avg_Semantic_Dist'], marker='^', 
                label='Avg Semantic Distance', linewidth=2, markersize=8)
        ax3.plot(df['Operation_Cost'], df['Avg_Cost_Dist'], marker='v', 
                label='Avg Cost Distance', linewidth=2, markersize=8, color='orange')
        ax3.set_xlabel('Operation Cost', fontsize=11)
        ax3.set_ylabel('Distance', fontsize=11)
        ax3.set_title('Distance Components vs Operation Cost')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Table of closest matches
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        table_data = []
        for idx, row in df.iterrows():
            table_data.append([
                f"{row['Operation_Cost']:.1f}",
                row['Closest_Match'][:15],  # Truncate long names
                f"{row['Match_ISEC']:.4f}",
                f"{row['Overall_ISEC']:.4f}"
            ])
        
        table = ax4.table(cellText=table_data,
                         colLabels=['Operation Cost', 'Closest Match', 'Match ISEC', 'Overall ISEC'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.2, 0.3, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        plt.tight_layout()
        plt.savefig('operation_cost_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: operation_cost_analysis.png")
        plt.show()
    
    def plot_all_sentences_heatmap(self, df: pd.DataFrame) -> None:
        """
        Plot heatmap showing ISEC scores for all sentences across semantic weights.
        
        Args:
            df: Results DataFrame from analyze_all_sentences_across_weights
        """
        # Pivot for heatmap
        pivot_df = df.pivot(index='Sentence', columns='Semantic_Weight', values='Overall_ISEC')
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sns.heatmap(pivot_df, annot=True, fmt='.3f', cmap='RdYlGn_r', 
                   cbar_kws={'label': 'Overall ISEC Score'}, ax=ax)
        
        ax.set_title('ISEC Score Sensitivity Heatmap\n(Rows: Sentences, Columns: Semantic Weight)',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Semantic Weight (0=100% Morphologic, 1=100% Semantic)', fontsize=11)
        ax.set_ylabel('Sentence', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('isec_heatmap_all_sentences.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: isec_heatmap_all_sentences.png")
        plt.show()
    
    def plot_sentence_trajectories(self, df: pd.DataFrame, num_closest: int = 3) -> None:
        """
        Plot trajectories of top sentences as semantic weight changes.
        
        Args:
            df: Results DataFrame from analyze_all_sentences_across_weights
            num_closest: Number of sentences to highlight
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Get top sentences at middle weight (0.5)
        mid_df = df[df['Semantic_Weight'] == 0.5].nlargest(num_closest, 'Overall_ISEC')
        top_sentences = mid_df['Sentence'].values
        
        # Plot trajectory for each top sentence
        colors = plt.cm.tab10(np.linspace(0, 1, len(top_sentences)))
        
        for sentence, color in zip(top_sentences, colors):
            sentence_df = df[df['Sentence'] == sentence].sort_values('Semantic_Weight')
            ax.plot(sentence_df['Semantic_Weight'], sentence_df['Overall_ISEC'],
                   marker='o', label=sentence, linewidth=2.5, markersize=8, color=color)
        
        ax.set_xlabel('Semantic Weight', fontsize=12)
        ax.set_ylabel('Overall ISEC Score', fontsize=12)
        ax.set_title(f'ISEC Score Trajectories for Top {num_closest} Sentences\n(How sentences move as semantic weight varies)',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        
        plt.tight_layout()
        plt.savefig('sentence_trajectories.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: sentence_trajectories.png")
        plt.show()
    
    def generate_sensitivity_report(self, output_file: str = "sensitivity_report.xlsx") -> None:
        """
        Generate comprehensive sensitivity analysis report.
        
        Args:
            output_file: Output Excel filename
        """
        # Analyze semantic weight sweep
        df_semantic = self.analyze_semantic_weight_sweep()
        
        # Analyze cost factor sweep
        df_cost = self.analyze_cost_factor_sweep()
        
        # Analyze operation cost sweep
        df_operation = self.analyze_operation_cost_sweep()
        
        # Analyze all sentences
        df_all = self.analyze_all_sentences_across_weights()
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_semantic.to_excel(writer, sheet_name='Semantic_Weight_Sweep', index=False)
            df_cost.to_excel(writer, sheet_name='Cost_Factor_Sweep', index=False)
            df_operation.to_excel(writer, sheet_name='Operation_Cost_Sweep', index=False)
            df_all.to_excel(writer, sheet_name='All_Sentences', index=False)
        
        print(f"✓ Report saved: {output_file}")
        return df_semantic, df_cost, df_operation, df_all


def main():
    """Main entry point for parameter sensitivity analysis."""
    print("=" * 90)
    print("ISEC Parameter Sensitivity Analysis")
    print("=" * 90)
    print()
    
    # Initialize analysis
    analysis = ParameterSensitivityAnalysis()
    
    print("\n1. Analyzing semantic weight sensitivity...")
    df_semantic = analysis.analyze_semantic_weight_sweep()
    print(df_semantic.head())
    
    print("\n2. Analyzing cost factor sensitivity...")
    df_cost = analysis.analyze_cost_factor_sweep()
    print(df_cost.head())
    
    print("\n3. Analyzing operation cost sensitivity...")
    df_operation = analysis.analyze_operation_cost_sweep()
    print(df_operation.head())
    
    print("\n4. Analyzing all sentences across semantic weights...")
    df_all = analysis.analyze_all_sentences_across_weights()
    
    print("\n5. Generating visualizations...")
    analysis.plot_semantic_weight_analysis(df_semantic)
    analysis.plot_cost_factor_analysis(df_cost)
    analysis.plot_operation_cost_analysis(df_operation)
    analysis.plot_all_sentences_heatmap(df_all)
    analysis.plot_sentence_trajectories(df_all)
    
    print("\n6. Generating comprehensive report...")
    analysis.generate_sensitivity_report()
    
    print("\n" + "=" * 90)
    print("Analysis Complete!")
    print("=" * 90)
    print("\nGenerated files:")
    print("  - semantic_weight_analysis.png: 4-panel analysis of weight sensitivity")
    print("  - cost_factor_analysis.png: Analysis of cost factor sensitivity")
    print("  - operation_cost_analysis.png: Analysis of operation cost sensitivity")
    print("  - isec_heatmap_all_sentences.png: Heatmap of all sentences")
    print("  - sentence_trajectories.png: How sentences move with parameter changes")
    print("  - sensitivity_report.xlsx: Detailed data for further analysis")


if __name__ == "__main__":
    main()
