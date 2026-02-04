# ISEC Cost Parameter Sensitivity Analysis

Visualize how operation cost parameters affect ISEC scores and sentence analysis to understand cost model impact.

## Overview

This analysis tool helps you understand how different cost parameters influence:
1. **Morphological distance calculations** - How substitution, insertion, deletion costs affect edit distances
2. **ISEC scores** - How cost parameters change overall structural analysis
3. **Parameter interactions** - How multiple cost parameters work together

## Key Parameters Analyzed

### 1. Operation Costs
- **Substitution Cost**: Cost for replacing one character with another
- **Insertion Cost**: Cost for adding a character
- **Deletion Cost**: Cost for removing a character
- **Transposition Cost**: Cost for swapping adjacent characters

### 2. Cost Factor (`COST_FACTOR_PENALIZATION`)
- **Range**: 0.0 (no penalization) to 1.0+ (heavy penalization)
- **Effect**: Controls how much edit operations (insertion, deletion, and substitution) are penalized in final score

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
python cost_sensitivity_analysis.py
```

This generates:
1. **Substitution cost analysis** (`substitution_cost_analysis.png`)
2. **Cost factor analysis** (`cost_factor_analysis.png`)
3. **3D cost interaction visualization** (`3d_cost_analysis.png`)
4. **Excel report** (`cost_sensitivity_report.xlsx`)

### Custom Analysis
```python
from cost_sensitivity_analysis import CostSensitivityAnalysis

# Analyze specific sentence
analysis = CostSensitivityAnalysis(query_sentence="XDKT11T3")

# Custom parameter ranges
costs = [0.5, 1.0, 1.5, 2.0]
df = analysis.analyze_substitution_cost_sweep(costs)

# Generate specific visualizations
analysis.plot_substitution_cost_analysis(df)
```

## Output Files

### 1. substitution_cost_analysis.png
Four-panel visualization showing:
- **Top-left**: Individual match ISEC scores vs substitution cost
- **Top-right**: Overall ISEC scores vs substitution cost
- **Bottom-left**: Distance components (semantic vs cost) vs substitution cost
- **Bottom-right**: Table of closest matches at each cost

### 2. cost_factor_analysis.png
Two-panel visualization:
- **Left**: Overall ISEC scores vs cost factor
- **Right**: Average cost distance vs cost factor

### 3. 3d_cost_analysis.png
3D scatter plot:
- **X-axis**: Substitution cost
- **Y-axis**: Insertion cost
- **Z-axis**: Deletion cost
- **Color**: Overall ISEC score (warmer colors = higher scores)

### 4. cost_sensitivity_report.xlsx
Excel workbook with three sheets:
- **Substitution_Cost_Sweep**: Detailed data for substitution cost analysis
- **Cost_Factor_Sweep**: Detailed data for cost factor analysis
- **All_Costs_Sweep**: Complete 3D parameter sweep data

## Interpretation Guide

### Understanding Cost Impact

#### High Operation Costs
- **Effect**: Make morphological differences more pronounced
- **Result**: Sentences with more character differences get lower similarity scores
- **Use case**: When you want to emphasize exact character matching

#### Low Operation Costs
- **Effect**: Make morphological differences less pronounced
- **Result**: Sentences with character differences still show high similarity
- **Use case**: When you want to focus more on semantic meaning

#### Cost Factor (Penalization)
- **High values (0.5+)**: Heavily penalize edit operations (insertion, deletion, and substitution)
- **Low values (0.0-0.1)**: Treat all operations more equally
- **Zero**: No additional penalization beyond operation costs

### 3D Analysis Insights

The 3D visualization reveals:
- **Parameter interaction effects**: How substitution, insertion, and deletion costs work together
- **Score landscapes**: Regions where ISEC scores are high/low
- **Optimal parameter combinations**: Sweet spots for specific analysis goals

### Practical Examples

#### Example 1: Finding Balanced Costs
If you want moderate sensitivity to character differences:
- Look for parameter combinations with **moderate ISEC scores** (2.0-5.0)
- These provide balanced semantic and morphological analysis

#### Example 2: Identifying Cost Sensitivity
If the 3D plot shows **steep gradients**:
- Small cost changes cause large ISEC changes
- May indicate borderline cases or ambiguous structures

#### Example 3: Parameter Optimization
If you want to maximize differentiation:
- Look for parameter combinations with **high variance** in ISEC scores
- These settings make similar sentences more distinguishable

## Customization

### Parameter Ranges
Modify analysis ranges in the script:
```python
# Custom substitution costs
sub_costs = np.linspace(0.1, 3.0, 30)  # More granular analysis

# Custom cost factors
factors = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]
```

### Visualization Options
Adjust plot settings:
```python
# Change figure size
fig, ax = plt.subplots(figsize=(16, 10))

# Modify color schemes
scatter = ax.scatter(x, y, z, c=scores, cmap='plasma')

# Adjust labels
ax.set_title('Custom Title', fontsize=16)
```

## Future Enhancements

### 1. Custom Cost Matrix Analysis
```python
# Planned feature
df_custom = analysis.analyze_custom_cost_impact()
```

### 2. Multi-dimensional Parameter Analysis
Advanced visualizations showing interactions between:
- All four operation costs
- Cost factor
- Semantic weight
- Top-k matches

### 3. Statistical Sensitivity Metrics
- **Sensitivity indices**: Quantify parameter impact on results
- **Variance decomposition**: Identify most influential parameters
- **Confidence intervals**: Uncertainty quantification for scores

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

### CostSensitivityAnalysis Class

```python
class CostSensitivityAnalysis:
    def __init__(self, query_sentence: str = None)
    
    def analyze_substitution_cost_sweep(self, costs: List[float] = None) -> pd.DataFrame
    
    def analyze_cost_factor_sweep(self, factors: List[float] = None) -> pd.DataFrame
    
    def analyze_all_costs_sweep(self) -> pd.DataFrame
    
    def plot_substitution_cost_analysis(self, df: pd.DataFrame) -> None
    
    def plot_cost_factor_analysis(self, df: pd.DataFrame) -> None
    
    def plot_3d_cost_analysis(self, df: pd.DataFrame) -> None
    
    def generate_cost_report(self, output_file: str = "cost_sensitivity_report.xlsx") -> None
```

### Methods

#### `analyze_substitution_cost_sweep(costs)`
Analyze how ISEC scores change with substitution cost variation.

**Parameters:**
- `costs`: List of substitution costs to test

**Returns:**
- DataFrame with substitution costs, closest match, and ISEC scores

#### `analyze_cost_factor_sweep(factors)`
Analyze how ISEC scores change with cost factor variation.

**Parameters:**
- `factors`: List of cost factors to test

**Returns:**
- DataFrame with cost factors and ISEC scores

#### `analyze_all_costs_sweep()`
Analyze interactions between all operation cost parameters.

**Returns:**
- DataFrame with all cost combinations and ISEC scores

#### `plot_3d_cost_analysis(df)`
Create 3D visualization of cost parameter interactions.

**Parameters:**
- `df`: Results DataFrame from `analyze_all_costs_sweep`

## Sample Output

### Console Output
```
Query Sentence: 'XDKT11T3'
Frequency: 100

1. Analyzing substitution cost sensitivity...
   Substitution_Cost Closest_Match  Match_ISEC  Overall_ISEC
0               0.5      XDKG11T3    9.090909      5.882353
1               1.0      XDKG11T3    7.692308      4.761905
2               1.5      XDKG11T3    6.666667      4.000000
3               2.0      XDKG11T3    5.882353      3.448276

2. Analyzing cost factor sensitivity...
   Cost_Factor Closest_Match  Match_ISEC  Overall_ISEC
0          0.0      XDKG11T3    7.692308      4.761905
1          0.1      XDKG11T3    7.382949      4.607502
2          0.2      XDKG11T3    7.100592      4.464286
3          0.5      XDKG11T3    6.451613      4.117647

3. Analyzing all cost parameters...
Analyzed 64 cost combinations

4. Generating visualizations...
✓ Saved: substitution_cost_analysis.png
✓ Saved: cost_factor_analysis.png
✓ Saved: 3d_cost_analysis.png

5. Generating comprehensive report...
✓ Report saved: cost_sensitivity_report.xlsx
```

### Excel Report Structure

**Sheet 1: Substitution_Cost_Sweep**
| Substitution_Cost | Closest_Match | Match_ISEC | Overall_ISEC | Avg_Semantic_Dist | Avg_Cost_Dist |
|------------------|---------------|------------|--------------|-------------------|---------------|
| 0.5 | XDKG11T3 | 9.0909 | 5.8824 | 0.0346 | 0.6500 |
| 1.0 | XDKG11T3 | 7.6923 | 4.7619 | 0.0346 | 0.8000 |
| 1.5 | XDKG11T3 | 6.6667 | 4.0000 | 0.0346 | 0.9500 |
| 2.0 | XDKG11T3 | 5.8824 | 3.4483 | 0.0346 | 1.1000 |

**Sheet 2: Cost_Factor_Sweep**
| Cost_Factor | Closest_Match | Match_ISEC | Overall_ISEC | Avg_Semantic_Dist | Avg_Cost_Dist |
|------------|---------------|------------|--------------|-------------------|---------------|
| 0.0 | XDKG11T3 | 7.6923 | 4.7619 | 0.0346 | 0.8000 |
| 0.1 | XDKG11T3 | 7.3829 | 4.6075 | 0.0346 | 0.8000 |
| 0.2 | XDKG11T3 | 7.1006 | 4.4643 | 0.0346 | 0.8000 |
| 0.5 | XDKG11T3 | 6.4516 | 4.1176 | 0.0346 | 0.8000 |

**Sheet 3: All_Costs_Sweep**
| Substitution_Cost | Insertion_Cost | Deletion_Cost | Overall_ISEC | Avg_Semantic_Dist | Avg_Cost_Dist |
|------------------|----------------|---------------|--------------|-------------------|---------------|
| 0.5 | 0.5 | 0.5 | 5.8824 | 0.0346 | 0.6500 |
| 0.5 | 0.5 | 1.0 | 5.5556 | 0.0346 | 0.6750 |
| 0.5 | 1.0 | 0.5 | 5.5556 | 0.0346 | 0.6750 |
| 0.5 | 1.0 | 1.0 | 5.2632 | 0.0346 | 0.7000 |

## Related Tools

- [ISEC Calculator](ISEC_README.md) - Main ISEC implementation
- [Parameter Sensitivity Analysis](PARAMETER_SENSITIVITY_README.md) - Semantic weight analysis
- [Levenshtein-Damerau Distance](COST_MATRIX_README.md) - Morphological distance calculator
- [Semantic Distance Calculator](SEMANTIC_DISTANCE_README.md) - Semantic similarity analyzer

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your analysis features
4. Submit a pull request