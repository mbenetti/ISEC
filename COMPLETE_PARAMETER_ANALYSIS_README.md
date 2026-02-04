# Complete ISEC Parameter Analysis Suite

Comprehensive toolkit for analyzing how all ISEC parameters affect structural sentence analysis.

## Overview

This suite provides three complementary tools to understand parameter sensitivity:

1. **[Parameter Sensitivity Analysis](PARAMETER_SENSITIVITY_README.md)** - Semantic weight impact
2. **[Cost Sensitivity Analysis](COST_SENSITIVITY_README.md)** - Operation cost impact  
3. **[Comprehensive Analysis](#comprehensive-parameter-analysis)** - Multi-parameter interactions

## Analysis Tools

### 1. Parameter Sensitivity Analysis (`parameter_sensitivity_analysis.py`)
Analyzes how **semantic weight** affects ISEC scores and sentence rankings.

**Key Features:**
- Trajectory plots showing sentence movement
- Heatmaps of all sentences across weights
- Excel reports for detailed analysis

### 2. Cost Sensitivity Analysis (`cost_sensitivity_analysis.py`)
Analyzes how **operation costs** affect ISEC scores.

**Key Features:**
- Substitution/insertion/deletion cost sweeps
- 3D visualization of cost interactions
- Cost factor (penalization) analysis

### 3. Comprehensive Analysis (`comprehensive_parameter_analysis.py`)
Analyzes **interactions between all parameters**.

**Key Features:**
- Multi-parameter interaction heatmaps
- 3D visualization of parameter spaces
- Sensitivity comparison across all parameters

## Installation

```bash
# Install all dependencies
uv pip install matplotlib seaborn openpyxl

# Or with pip
pip install matplotlib seaborn openpyxl
```

## Quick Start

Run all analyses sequentially:

```bash
# 1. Semantic weight analysis
python parameter_sensitivity_analysis.py

# 2. Operation cost analysis
python cost_sensitivity_analysis.py

# 3. Comprehensive multi-parameter analysis
python comprehensive_parameter_analysis.py
```

## Understanding Parameter Impact

### Semantic Weight (0.0 to 1.0)
- **0.0**: 100% morphological similarity, 0% semantic similarity
- **0.5**: Balanced morphological and semantic similarity
- **1.0**: 0% morphological similarity, 100% semantic similarity

**High values** emphasize semantic meaning over character structure.
**Low values** emphasize exact character matching over meaning.

### Operation Costs
- **Substitution Cost**: Cost to replace one character with another
- **Insertion Cost**: Cost to add a character
- **Deletion Cost**: Cost to remove a character
- **Transposition Cost**: Cost to swap adjacent characters

**High costs** make character differences more pronounced.
**Low costs** make sentences with differences still appear similar.

### Cost Factor (Penalization)
- **Range**: 0.0 (no penalization) to 1.0+ (heavy penalization)
- **Effect**: Additional weight for insertion/deletion operations

**High values** penalize structural changes more heavily.
**Low values** treat all operations more equally.

## Interpreting Results

### ISEC Score Meaning (Remember: Higher = More Similar!)
Since ISEC = FMN / (weighted distances):

- **High ISEC scores** = Small distances = High similarity = Common patterns
- **Low ISEC scores** = Large distances = Low similarity = Unique patterns

### Parameter Sensitivity Indicators

1. **Steep Trajectories**: High sensitivity to parameter changes
2. **Flat Lines**: Low sensitivity, stable results
3. **Crossing Lines**: Ranking changes with parameters
4. **Hot Spots in Heatmaps**: Parameter combinations that maximize similarity
5. **Cool Spots in Heatmaps**: Parameter combinations that minimize similarity

## Practical Applications

### 1. Finding Optimal Parameters
Use heatmaps and contour plots to identify parameter combinations that:
- Maximize differentiation between similar sentences
- Minimize noise from irrelevant variations
- Balance semantic and structural considerations

### 2. Validating Analysis Robustness
Use trajectory plots to check if:
- Sentence rankings are stable across parameter ranges
- Results are sensitive to small parameter changes
- Analysis is robust to parameter uncertainty

### 3. Understanding Model Behavior
Use 3D visualizations to see how:
- Parameters interact with each other
- Different sentence types respond to parameters
- Trade-offs between semantic and morphological similarity

## Sample Workflow

### Step 1: Initial Exploration
```bash
# Run comprehensive analysis to understand parameter space
python comprehensive_parameter_analysis.py
```

Look at:
- `parameter_sensitivity_comparison.png` to see which parameters have most impact
- `3d_parameter_interaction.png` to understand parameter interactions

### Step 2: Detailed Analysis
Based on Step 1 results, run detailed analysis on most sensitive parameters:

```bash
# If semantic weight is most sensitive
python parameter_sensitivity_analysis.py

# If operation costs are most sensitive  
python cost_sensitivity_analysis.py
```

### Step 3: Parameter Optimization
Use visualizations to find optimal parameter combinations:
- Look for "sweet spots" in heatmaps
- Identify stable regions in trajectory plots
- Find balance points in contour plots

## Generated Files

### Visualization Files
- `semantic_weight_analysis.png` - 4-panel semantic weight analysis
- `isec_heatmap_all_sentences.png` - Heatmap of all sentences vs semantic weight
- `sentence_trajectories.png` - How sentences move with semantic weight changes
- `substitution_cost_analysis.png` - Substitution cost sensitivity
- `cost_factor_analysis.png` - Cost factor impact
- `3d_cost_analysis.png` - 3D cost parameter interactions
- `parameter_interaction_heatmap.png` - Semantic weight vs substitution cost
- `3d_parameter_interaction.png` - 3D parameter space visualization
- `parameter_contour_plot.png` - Contour lines of equal ISEC scores
- `parameter_sensitivity_comparison.png` - Comparison across all parameters

### Data Files
- `sensitivity_report.xlsx` - Detailed semantic weight analysis data
- `cost_sensitivity_report.xlsx` - Detailed cost parameter analysis data
- `comprehensive_parameter_report.xlsx` - Multi-parameter interaction data

## Customization

### Adjusting Parameter Ranges
Modify analysis granularity in each script:

```python
# More granular analysis
weights = np.linspace(0.0, 1.0, 21)  # Instead of default 11 points
costs = np.linspace(0.1, 3.0, 30)    # Finer cost resolution
```

### Focusing on Specific Sentences
Analyze particular sentences of interest:

```python
# Analyze specific sentence
analysis = ParameterSensitivityAnalysis(query_sentence="YOUR_SENTENCE")
```

### Custom Visualization
Adjust plot appearance:

```python
# Change color schemes
sns.heatmap(data, cmap='viridis')  # Different color palette

# Modify figure sizes
plt.figure(figsize=(16, 12))       # Larger plots
```

## Troubleshooting

### Common Issues

1. **"No module named 'matplotlib'"**
   ```bash
   uv pip install matplotlib seaborn
   ```

2. **"Connection refused" for Ollama**
   - Ensure Ollama service is running: `ollama serve`
   - Check `OLLAMA_HOST` in `.env` file

3. **Empty or incomplete visualizations**
   - Verify Excel files have sufficient data
   - Check that sentences have varying structures
   - Ensure custom costs file is properly formatted

### Performance Tips

1. **Reduce parameter ranges** for faster analysis:
   ```python
   # Coarser analysis for quick exploration
   weights = np.linspace(0.0, 1.0, 6)    # Instead of 11 or 21
   costs = np.linspace(0.5, 2.0, 4)      # Instead of 16 or 30
   ```

2. **Focus on most sensitive parameters** first

3. **Use smaller datasets** for initial exploration

## API Reference

### Main Classes

```python
# Parameter Sensitivity Analysis
class ParameterSensitivityAnalysis:
    def analyze_semantic_weight_sweep(self, weights) -> pd.DataFrame
    def plot_sentence_trajectories(self, df) -> None

# Cost Sensitivity Analysis  
class CostSensitivityAnalysis:
    def analyze_substitution_cost_sweep(self, costs) -> pd.DataFrame
    def plot_3d_cost_analysis(self, df) -> None

# Comprehensive Analysis
class ComprehensiveParameterAnalysis:
    def analyze_parameter_interactions(self) -> pd.DataFrame
    def plot_parameter_interaction_heatmap(self, df) -> None
```

## Related Documentation

- [ISEC Main Calculator](ISEC_README.md) - Core ISEC implementation
- [Levenshtein-Damerau Distance](COST_MATRIX_README.md) - Morphological distance
- [Semantic Distance Calculator](SEMANTIC_DISTANCE_README.md) - Semantic similarity

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your analysis improvements
4. Submit a pull request