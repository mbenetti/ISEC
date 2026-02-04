# Parameter Movement Visualizer
# Simple script to visualize how parameters cause sentences to move

import matplotlib.pyplot as plt
import numpy as np

def visualize_parameter_movement():
    """Create a simple visualization showing how parameters move sentences."""
    
    print("Parameter Movement Visualization")
    print("=" * 40)
    print("This script demonstrates how different parameter settings")
    print("cause sentences to move relative to each other.")
    print()
    
    # Create sample data showing movement
    semantic_weights = np.linspace(0.0, 1.0, 11)
    
    # Simulate how different sentences move with semantic weight
    # These represent typical patterns from our analysis
    sentence_patterns = {
        'XDKT11T3 (Target)': {
            'pattern': 'exponential',
            'color': 'red',
            'description': 'High-frequency, structurally and semantically similar'
        },
        'XDKG11T3 (Similar)': {
            'pattern': 'moderate',
            'color': 'orange',
            'description': 'Moderately similar in both aspects'
        },
        'LDKT11T3 (Different)': {
            'pattern': 'low',
            'color': 'blue',
            'description': 'Structurally different, less frequent'
        },
        'LDKT11T3QET (Very Different)': {
            'pattern': 'very_low',
            'color': 'green',
            'description': 'Very different in both aspects, rare'
        }
    }
    
    # Generate ISEC scores based on patterns
    def generate_scores(pattern_type):
        if pattern_type == 'exponential':
            # Starts moderate, grows exponentially
            return 2 + 20 * (semantic_weights ** 2)
        elif pattern_type == 'moderate':
            # Moderate growth
            return 1 + 10 * semantic_weights
        elif pattern_type == 'low':
            # Slow growth
            return 0.5 + 2 * semantic_weights
        elif pattern_type == 'very_low':
            # Very slow growth
            return 0.1 + 0.5 * semantic_weights
    
    # Create the visualization
    plt.style.use('seaborn-v0_8')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Trajectory visualization
    for sentence, info in sentence_patterns.items():
        scores = generate_scores(info['pattern'])
        ax1.plot(semantic_weights, scores, 
                marker='o', linewidth=2.5, markersize=8, 
                color=info['color'], label=sentence)
    
    ax1.set_xlabel('Semantic Weight (0=Structure, 1=Meaning)', fontsize=11)
    ax1.set_ylabel('ISEC Score (Higher = More Similar)', fontsize=11)
    ax1.set_title('How Sentences Move as Semantic Weight Changes\n(Trajectory Visualization)', 
                  fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Movement concept illustration
    # Show the same concept with annotations
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    
    # Draw axes
    ax2.axhline(y=5, color='black', linewidth=0.5)
    ax2.axvline(x=5, color='black', linewidth=0.5)
    
    # Add labels
    ax2.text(5, 9.5, 'More Similar\n(Higher ISEC)', ha='center', va='top', fontweight='bold')
    ax2.text(5, 0.5, 'Less Similar\n(Lower ISEC)', ha='center', va='bottom', fontweight='bold')
    ax2.text(0.5, 5, 'Structure-\nFocused\n(Weight=0.0)', ha='center', va='center', fontweight='bold', rotation=90)
    ax2.text(9.5, 5, 'Meaning-\nFocused\n(Weight=1.0)', ha='center', va='center', fontweight='bold', rotation=90)
    
    # Draw sample movement paths
    # Sentence A: Moves toward target
    ax2.annotate('', xy=(8, 7), xytext=(2, 3),
                arrowprops=dict(arrowstyle='->', color='red', lw=3))
    ax2.text(5, 7.5, 'Sentence A\n(Moves Closer)', ha='center', color='red', fontweight='bold')
    
    # Sentence B: Moves away from target
    ax2.annotate('', xy=(8, 2), xytext=(2, 6),
                arrowprops=dict(arrowstyle='->', color='blue', lw=3))
    ax2.text(5, 1.5, 'Sentence B\n(Moves Further)', ha='center', color='blue', fontweight='bold')
    
    # Sentence C: Stable movement
    ax2.annotate('', xy=(8, 5), xytext=(2, 5),
                arrowprops=dict(arrowstyle='->', color='green', lw=3))
    ax2.text(5, 5.5, 'Sentence C\n(Stable)', ha='center', color='green', fontweight='bold')
    
    ax2.set_title('Concept: Sentences Move Relative to Each Other\nas Parameters Change', 
                  fontsize=12, fontweight='bold')
    ax2.set_xticks([])
    ax2.set_yticks([])
    
    plt.tight_layout()
    plt.savefig('parameter_movement_concept.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✓ Visualization saved as 'parameter_movement_concept.png'")
    print()
    
    # Show example data points
    print("Example Movement Data:")
    print("-" * 25)
    sample_weights = [0.0, 0.3, 0.5, 0.7, 1.0]
    
    for weight in sample_weights:
        print(f"\nAt semantic_weight = {weight}:")
        for sentence, info in sentence_patterns.items():
            scores = generate_scores(info['pattern'])
            # Find closest score to this weight
            idx = int(weight * 10)
            score = scores[idx]
            print(f"  {sentence.split()[0]}: {score:.2f}")
    
    print()
    print("Key Insights:")
    print("-" * 15)
    print("1. Different sentences move at different rates")
    print("2. Some sentences move toward the target (become more similar)")
    print("3. Some sentences move away from the target (become less similar)")
    print("4. The relative rankings between sentences can change")
    print("5. This movement reveals different aspects of similarity")

if __name__ == "__main__":
    visualize_parameter_movement()