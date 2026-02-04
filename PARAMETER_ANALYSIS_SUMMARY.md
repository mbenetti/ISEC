# ISEC Parameter Analysis Summary

## Key Findings from Parameter Sensitivity Analysis

### 1. Semantic Weight Impact
The semantic weight parameter (0.0 to 1.0) has the most dramatic effect on ISEC scores:

- **At 0.0 (100% morphologic)**: ISEC scores are lower because distances are dominated by edit operations
- **At 1.0 (100% semantic)**: ISEC scores are much higher because semantic similarity dominates

**Example from analysis**:
- Semantic Weight 0.0: ISEC = 4.17
- Semantic Weight 1.0: ISEC = 96.40

This shows how the balance between semantic and morphological components dramatically affects results.

### 2. Cost Factor Impact
The cost factor (penalization for edit operations) has minimal impact in this dataset:

- **At 0.0**: ISEC = 9.78
- **At 0.5**: ISEC = 9.78

This suggests that for these sentences, insertion/deletion operations are not the dominant factor.

### 3. Operation Cost Impact
Changing base operation costs (substitution, insertion, deletion, transposition) affects the morphological component:

- **At 0.5 cost**: ISEC = 15.10
- **At 1.0 cost**: ISEC = 9.78
- **At 1.5 cost**: ISEC = 6.42

Higher operation costs lead to lower ISEC scores (more distance = less similarity).

## How Sentences Move with Parameters

### Sentence Trajectory Analysis
The trajectory plots show how different sentences respond to parameter changes:

1. **High-frequency sentences** tend to have higher ISEC scores across all parameters
2. **Similar sentences** (like XDKT11T3 and XDKG11T3) maintain close rankings
3. **Dissimilar sentences** show more dramatic ranking changes

### Key Insights
- **XDKT11T3** consistently ranks highest in ISEC, indicating it's a common/typical pattern
- **LDKT11T3QET** consistently ranks lowest, indicating it's rare/unique
- **Semantic weight** is the most influential parameter for ranking changes

## Parameter Recommendations

### For Stable Results
- Use **semantic weight between 0.4-0.6** for balanced analysis
- Keep **operation costs at 1.0** unless domain-specific adjustments needed
- **Cost factor can be kept at default (0.1)** for most applications

### For Domain-Specific Tuning
- **High semantic weight (0.7-1.0)**: When semantic meaning is more important than structure
- **Low semantic weight (0.0-0.3)**: When exact structural matching is critical
- **Higher operation costs**: When you want to penalize structural differences more heavily

## Visualization Interpretation Guide

### 1. Semantic Weight Analysis Plot
- **Steep slope**: High sensitivity to semantic weight changes
- **Flat line**: Low sensitivity, stable results
- **Crossing lines**: Ranking changes between sentences

### 2. Heatmap Interpretation
- **Red cells**: High ISEC scores (more similar/common)
- **Blue cells**: Low ISEC scores (more different/rare)
- **Horizontal bands**: Sentences with similar behavior across weights

### 3. Trajectory Plots
- **Parallel lines**: Consistent relative rankings
- **Converging lines**: Sentences becoming more similar
- **Diverging lines**: Sentences becoming more different

## Practical Applications

### 1. Finding Optimal Parameters
Use the sensitivity analysis to:
1. Identify the parameter range where results are stable
2. Find the point where ranking changes stabilize
3. Select parameters that align with domain knowledge

### 2. Validating Results
Check that:
- Key sentences maintain consistent rankings across reasonable parameter ranges
- Results don't change dramatically with small parameter adjustments
- Findings align with intuitive expectations

### 3. Domain Adaptation
Adjust parameters based on:
- **Technical domains**: May need higher semantic weight
- **Structured data**: May need higher morphologic weight
- **Noisy data**: May need adjusted operation costs

## Next Steps

### 1. Domain-Specific Analysis
Run the analysis on your specific dataset to:
- Identify optimal parameter ranges
- Understand how sentences in your domain respond to parameters
- Validate results against domain expertise

### 2. Comparative Studies
Compare parameter sensitivity across:
- Different datasets
- Different domains
- Different sentence types

### 3. Automated Parameter Selection
Develop methods to automatically select optimal parameters based on:
- Dataset characteristics
- Domain requirements
- Performance metrics

## Files Generated

### Visualizations
1. **`semantic_weight_analysis.png`** - Shows how ISEC changes with semantic emphasis
2. **`cost_factor_analysis.png`** - Shows impact of edit operation penalties (insertion, deletion, and substitution)
3. **`operation_cost_analysis.png`** - Shows effect of base operation costs
4. **`isec_heatmap_all_sentences.png`** - Comprehensive view of all sentences
5. **`sentence_trajectories.png`** - How sentences move with parameter changes

### Data Export
**`sensitivity_report.xlsx`** - Contains raw data for custom analysis:
- **Semantic_Weight_Sweep**: Detailed results for semantic weight variations
- **Cost_Factor_Sweep**: Results for cost factor variations
- **Operation_Cost_Sweep**: Results for operation cost variations
- **All_Sentences**: Complete dataset for advanced analysis

## Conclusion

The parameter sensitivity analysis reveals that:
1. **Semantic weight** is the most influential parameter
2. **Operation costs** provide fine-grained control over morphological matching
3. **Cost factor** has minimal impact in most cases
4. Results are generally robust but can change significantly with extreme parameter values

This analysis provides the foundation for informed parameter selection and result validation in ISEC applications.