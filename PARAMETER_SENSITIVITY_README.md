# ISEC Parameter Sensitivity Analysis

Visualize how ISEC parameters affect sentence rankings and scores to understand parameter impact on structural analysis.

## Overview

This analysis tool helps you understand how different ISEC parameters influence:
1. **Sentence rankings** - Which sentences become more/less similar
2. **ISEC scores** - How scores change with parameter variations
3. **Component weights** - Semantic vs. morphological influence

## Key Parameters Analyzed

### 1. Semantic Weight (`ISEC_SEMANTIC_WEIGHT`)
- **Range**: 0.0 (100% morphologic) to 1.0 (100% semantic)
- **Effect**: Controls balance between semantic and morphological similarity
- **Visualization**: Trajectory plots showing how sentences move as weight changes

### 2. Operation Cost Factors (Future Enhancement)
- **Default costs**: Substitution, insertion, deletion, transposition
- **Penalization factor**: `COST_FACTOR_PENALIZATION`
- **Effect**: Influences morphological distance calculations

## Installation

```bash
# Install visualization dependencies
uv pip install matplotlib seaborn openpyxl

# Or with pip
pip install matplotlib seaborn openpyxl
```

## Usage

### Basic Analysis
```bash
python parameter_sensitivity_analysis.py
```

This generates:
1. **4-panel visualization** (`semantic_weight_analysis.png`)
2. **Heatmap of all sentences** (`isec_heatmap_all_sentences.png`)
3. **Trajectory plots** (`sentence_trajectories.png`)
4. **Excel report** (`sensitivity_report.xlsx`)

### Custom Analysis
```python
from parameter_sensitivity_analysis import ParameterSensitivityAnalysis

# Analyze specific sentence
analysis = ParameterSensitivityAnalysis(query_sentence="XDKT11T3")

# Custom parameter ranges
weights = [0.0, 0.25, 0.5, 0.75, 1.0]
df = analysis.analyze_semantic_weight_sweep(weights)

# Generate specific visualizations
analysis.plot_semantic_weight_analysis(df)
```

## Output Files

### 1. semantic_weight_analysis.png
Four-panel visualization showing:
- **Top-left**: Individual match ISEC scores vs semantic weight
- **Top-right**: Overall ISEC scores vs semantic weight
- **Bottom-left**: Distance components (semantic vs cost) vs semantic weight
- **Bottom-right**: Table of closest matches at each weight

### 2. isec_heatmap_all_sentences.png
Heatmap visualization:
- **Rows**: All sentences in dataset
- **Columns**: Semantic weights (0.0 to 1.0)
- **Cells**: Overall ISEC scores (color-coded)
- **Use**: Identify which sentences are most sensitive to parameter changes

### 3. sentence_trajectories.png
Trajectory plots:
- **Lines**: How ISEC scores change for top sentences as semantic weight varies
- **X-axis**: Semantic weight (0.0 to 1.0)
- **Y-axis**: Overall ISEC score
- **Use**: Visualize sentence movement and identify crossovers

### 4. sensitivity_report.xlsx
Excel workbook with two sheets:
- **Semantic_Weight_Sweep**: Detailed data for the query sentence
- **All_Sentences**: Complete dataset for all sentences across weights

## Interpretation Guide

### Understanding Trajectories
- **Rising lines**: Sentences become more similar (higher ISEC) as semantic weight increases
- **Falling lines**: Sentences become less similar (lower ISEC) as semantic weight increases
- **Crossing lines**: Parameter change causes ranking shifts
- **Flat lines**: Insensitive to parameter changes

### Heatmap Analysis
- **Hot spots (red)**: High ISEC scores (similar sentences)
- **Cool spots (blue)**: Low ISEC scores (dissimilar sentences)
- **Vertical bands**: Parameter ranges where specific sentences dominate
- **Horizontal patterns**: Sentence groups with similar behavior

### Practical Examples

#### Example 1: Finding Optimal Balance
If you want sentences that are both semantically and morphologically similar:
- Look for sentences with **high ISEC at semantic_weight=0.5**
- These are well-balanced in both dimensions

#### Example 2: Identifying Parameter Sensitivity
If a sentence's trajectory has a **steep slope**:
- Small parameter changes cause large ISEC changes
- May indicate borderline cases or ambiguous structures

#### Example 3: Ranking Stability
If sentence trajectories **don't cross**:
- Rankings are stable across parameter ranges
- Results are robust to parameter variations

## Customization

### Parameter Ranges
Modify analysis ranges in the script:
```python
# Custom semantic weights
weights = np.linspace(0.0, 1.0, 21)  # More granular analysis

# Custom cost factors (future enhancement)
factors = [0.0, 0.05, 0.1, 0.2, 0.5]
```

### Visualization Options
Adjust plot settings:
```python
# Change figure size
fig, ax = plt.subplots(figsize=(16, 10))

# Modify color schemes
sns.heatmap(pivot_df, cmap='viridis')  # Different color scheme

# Adjust labels
ax.set_title('Custom Title', fontsize=16)
```

## Future Enhancements

### 1. Cost Factor Analysis
```python
# Planned feature
df_cost = analysis.analyze_cost_factor_sweep([0.0, 0.1, 0.2, 0.5, 1.0])
```

### 2. Multi-parameter Analysis
3D visualizations showing interactions between:
- Semantic weight
- Cost factor
- Default operation costs

### 3. Statistical Sensitivity Metrics
- **Sensitivity indices**: Quantify parameter impact
- **Variance decomposition**: Identify most influential parameters
- **Confidence intervals**: Uncertainty quantification

## Troubleshooting

### "No module named 'matplotlib'"
```bash
uv pip install matplotlib seaborn
```

### "Connection refused" for Ollama
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_HOST` in `.env`

### Empty visualizations
- Verify sentences file has multiple entries
- Check that sentences have varying structures
- Ensure custom costs file (if used) is properly formatted

## API Reference

### ParameterSensitivityAnalysis Class

```python
class ParameterSensitivityAnalysis:
    def __init__(self, query_sentence: str = None)
    
    def analyze_semantic_weight_sweep(self, weights: List[float] = None) -> pd.DataFrame
    
    def analyze_all_sentences_across_weights(self, weights: List[float] = None) -> pd.DataFrame
    
    def plot_semantic_weight_analysis(self, df: pd.DataFrame) -> None
    
    def plot_all_sentences_heatmap(self, df: pd.DataFrame) -> None
    
    def plot_sentence_trajectories(self, df: pd.DataFrame, num_closest: int = 3) -> None
    
    def generate_sensitivity_report(self, output_file: str = "sensitivity_report.xlsx") -> None
```

### Methods

#### `analyze_semantic_weight_sweep(weights)`
Analyze how ISEC scores change with semantic weight variation.

**Parameters:**
- `weights`: List of semantic weights to test (0.0 to 1.0)

**Returns:**
- DataFrame with semantic weight, closest match, and ISEC scores

#### `plot_sentence_trajectories(df, num_closest)`
Plot trajectories showing how sentences move with parameter changes.

**Parameters:**
- `df`: Results DataFrame from `analyze_all_sentences_across_weights`
- `num_closest`: Number of top sentences to highlight

#### `generate_sensitivity_report(output_file)`
Generate comprehensive Excel report with all analysis data.

## Sample Output

### Console Output
```
Query Sentence: 'XDKT11T3'
Frequency: 100

1. Analyzing semantic weight sensitivity...
   Semantic_Weight  Morphologic_Weight Closest_Match  Match_ISEC  Overall_ISEC
0              0.0                 1.0      XDKG11T3    6.666667      4.166667
1              0.5                 0.5      XDKG11T3   12.947297      7.988075
2              1.0                 0.0      XDKG11T3  223.593807     96.402083

2. Generating visualizations...
✓ Saved: semantic_weight_analysis.png
✓ Saved: isec_heatmap_all_sentences.png
✓ Saved: sentence_trajectories.png

3. Generating comprehensive report...
✓ Report saved: sensitivity_report.xlsx
```

### Excel Report Structure

**Sheet 1: Semantic_Weight_Sweep**
| Semantic_Weight | Morphologic_Weight | Closest_Match | Match_ISEC | Overall_ISEC | Avg_Semantic_Dist | Avg_Cost_Dist |
|----------------|-------------------|---------------|------------|--------------|-------------------|---------------|
| 0.0 | 1.0 | XDKG11T3 | 6.6667 | 4.1667 | 0.0346 | 0.8000 |
| 0.5 | 0.5 | XDKG11T3 | 12.9473 | 7.9881 | 0.0346 | 0.8000 |
| 1.0 | 0.0 | XDKG11T3 | 223.5938 | 96.4021 | 0.0346 | 0.8000 |

**Sheet 2: All_Sentences**
| Semantic_Weight | Sentence | Overall_ISEC | Avg_Semantic_Dist | Avg_Cost_Dist |
|----------------|----------|--------------|-------------------|---------------|
| 0.0 | XDKT11T3 | 4.1667 | 0.0346 | 0.8000 |
| 0.0 | XDKG11T3 | 3.8462 | 0.0400 | 0.8667 |
| 0.5 | XDKT11T3 | 7.9881 | 0.0346 | 0.8000 |

## Related Tools

- [ISEC Calculator](ISEC_README.md) - Main ISEC implementation
- [Levenshtein-Damerau Distance](COST_MATRIX_README.md) - Morphological distance calculator
- [Semantic Distance Calculator](SEMANTIC_DISTANCE_README.md) - Semantic similarity analyzer

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your analysis features
4. Submit a pull request