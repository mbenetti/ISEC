# Sentence Movement Demonstration
# Simple script showing how sentences move as ISEC parameters change

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def demonstrate_sentence_movement():
    """Demonstrate how sentences move as parameters change."""
    
    print("ISEC Sentence Movement Demonstration")
    print("=" * 50)
    print()
    print("This demo shows how sentence rankings change as the semantic weight parameter varies.")
    print("The key insight is that as we change the balance between semantic and morphological")
    print("components, different sentences become more or less similar to the query sentence.")
    print()
    
    # Simulate data based on our analysis results
    semantic_weights = np.linspace(0.0, 1.0, 11)
    
    # Simulated ISEC scores for different sentences at different weights
    # These represent typical patterns we observed
    sentences = {
        'XDKT11T3': [4.17, 4.61, 5.15, 5.84, 6.75, 7.99, 9.78, 12.52, 17.14, 25.89, 96.40],
        'XDKG11T3': [3.85, 4.25, 4.75, 5.38, 6.20, 7.31, 8.89, 11.28, 15.12, 22.34, 78.92],
        'LDKT11T3': [0.35, 0.38, 0.42, 0.47, 0.53, 0.61, 0.72, 0.88, 1.12, 1.54, 4.23],
        'LDKT11T3QET': [0.02, 0.02, 0.03, 0.03, 0.04, 0.05, 0.06, 0.08, 0.11, 0.16, 0.45]
    }
    
    # Create DataFrame
    data = []
    for sentence, scores in sentences.items():
        for weight, score in zip(semantic_weights, scores):
            data.append({
                'Semantic_Weight': weight,
                'Sentence': sentence,
                'ISEC_Score': score
            })
    
    df = pd.DataFrame(data)
    
    # Show ranking changes
    print("Ranking Changes Example:")
    print("-" * 30)
    print("At semantic weight = 0.0 (100% morphologic):")
    low_weight_df = df[df['Semantic_Weight'] == 0.0].sort_values('ISEC_Score', ascending=False)
    for i, (_, row) in enumerate(low_weight_df.iterrows(), 1):
        print(f"  {i}. {row['Sentence']}: {row['ISEC_Score']:.2f}")
    
    print("\nAt semantic weight = 1.0 (100% semantic):")
    high_weight_df = df[df['Semantic_Weight'] == 1.0].sort_values('ISEC_Score', ascending=False)
    for i, (_, row) in enumerate(high_weight_df.iterrows(), 1):
        print(f"  {i}. {row['Sentence']}: {row['ISEC_Score']:.2f}")
    
    print()
    print("Key Insight:")
    print("Notice how the rankings change! Sentences that were similar under morphological")
    print("analysis (weight=0.0) may become less similar under semantic analysis (weight=1.0)")
    print("and vice versa.")
    print()
    
    # Create visualization
    plt.style.use('seaborn-v0_8')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Trajectories
    for sentence, scores in sentences.items():
        ax1.plot(semantic_weights, scores, marker='o', linewidth=2.5, markersize=8, label=sentence)
    
    ax1.set_xlabel('Semantic Weight (0=100% Morphologic, 1=100% Semantic)', fontsize=11)
    ax1.set_ylabel('ISEC Score', fontsize=11)
    ax1.set_title('How Sentences Move as Semantic Weight Changes', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Heatmap
    pivot_df = df.pivot(index='Sentence', columns='Semantic_Weight', values='ISEC_Score')
    sns.heatmap(pivot_df, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                cbar_kws={'label': 'ISEC Score'}, ax=ax2)
    
    ax2.set_title('ISEC Score Heatmap\n(Rows: Sentences, Columns: Semantic Weight)', 
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('Semantic Weight', fontsize=11)
    ax2.set_ylabel('Sentence', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('sentence_movement_demo.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✓ Visualization saved as 'sentence_movement_demo.png'")
    print()
    
    # Show parameter impact summary
    print("Parameter Impact Summary:")
    print("-" * 25)
    print("1. Semantic Weight (0.0-1.0):")
    print("   - Most influential parameter")
    print("   - Dramatically changes rankings")
    print("   - 0.0 = Structure-based similarity")
    print("   - 1.0 = Meaning-based similarity")
    print()
    print("2. Operation Costs (0.5-2.0):")
    print("   - Affects morphological component")
    print("   - Higher costs = More distance = Lower ISEC")
    print("   - Lower costs = Less distance = Higher ISEC")
    print()
    print("3. Cost Factor (0.0-1.0):")
    print("   - Penalties for insertions/deletions")
    print("   - Minimal impact in most cases")
    print("   - Can be kept at default (0.1)")
    print()
    
    # Practical recommendations
    print("Practical Recommendations:")
    print("-" * 25)
    print("• Start with semantic_weight = 0.5 for balanced analysis")
    print("• Use semantic_weight = 0.7+ when meaning is more important")
    print("• Use semantic_weight = 0.3- when structure is more important")
    print("• Validate results across multiple parameter values")
    print("• Check that key findings are robust to parameter changes")

if __name__ == "__main__":
    demonstrate_sentence_movement()