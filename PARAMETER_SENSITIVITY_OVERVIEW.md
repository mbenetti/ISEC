# ISEC Parameter Sensitivity Analysis Overview

## Understanding How Parameters Affect Sentence Rankings

This overview explains how ISEC parameters influence sentence similarity rankings and provides practical guidance for parameter selection.

## Core Concept: Sentence Movement

The fundamental insight is that **sentences move relative to each other** as parameters change. What appears similar under one parameter setting may appear dissimilar under another.

### The ISEC Formula
```
ISEC = FMN / (semantic_weight × AvgSemanticDistance + morphologic_weight × AvgCostDistance)
```

Where:
- **FMN** = Frequency Median Normalized (higher = more frequent)
- **Semantic Distance** = Cosine distance between embeddings (0-1 scale)
- **Cost Distance** = Penalized edit distance (depends on operation costs)
- **Weights** = semantic_weight + morphologic_weight = 1.0

Note: While some alternative implementations might use a multiplicative approach like `ISEC = FMN / (SemanticDistance × Cost Median Penalized)`, the standard ISEC implementation uses the weighted average formula shown above, which provides better interpretability and parameter control.

## Key Parameters and Their Effects

### 1. Semantic Weight (ISEC_SEMANTIC_WEIGHT)
**Range**: 0.0 (100% morphologic) to 1.0 (100% semantic)

**Effect**: Controls the balance between meaning-based and structure-based similarity

**Movement Pattern**:
- **Low weights (0.0-0.3)**: Structure similarity dominates
  - Sentences with similar character patterns rank higher
  - Edit distance becomes the primary factor
- **Medium weights (0.4-0.6)**: Balanced analysis
  - Both semantic and morphologic factors contribute
  - Most stable parameter range
- **High weights (0.7-1.0)**: Meaning similarity dominates
  - Sentences with similar embeddings rank higher
  - Semantic distance becomes the primary factor

**Example Movement**:
```
Semantic Weight 0.0: XDKT11T3 (4.17) > XDKG11T3 (3.85) > LDKT11T3 (0.35)
Semantic Weight 1.0: XDKT11T3 (96.40) > XDKG11T3 (78.92) > LDKT11T3 (4.23)
```

### 2. Operation Costs (DEFAULT_*_COST)
**Range**: Typically 0.5-2.0 (default 1.0)

**Effect**: Changes the base cost of edit operations

**Movement Pattern**:
- **Lower costs (0.5)**: Less penalty for differences
  - More sentences appear similar
  - Higher ISEC scores overall
- **Higher costs (1.5+)**: More penalty for differences
  - Fewer sentences appear similar
  - Lower ISEC scores overall

### 3. Cost Factor (COST_FACTOR_PENALIZATION)
**Range**: Typically 0.0-1.0 (default 0.1)

**Effect**: Additional penalty for edit operations (insertion, deletion, and substitution)

**Movement Pattern**:
- **Low values (0.0-0.1)**: Minimal impact
- **High values (0.5+)**: Strongly penalizes structural changes

## Visualizing Parameter Effects

### 1. Trajectory Plots
Show how individual sentences move as parameters change:

- **Steep slopes**: High sensitivity to parameter changes
- **Flat lines**: Low sensitivity, stable results
- **Crossing lines**: Ranking changes between sentences

### 2. Heatmaps
Display ISEC scores for all sentences across parameter ranges:

- **Red areas**: High similarity (high ISEC scores)
- **Blue areas**: Low similarity (low ISEC scores)
- **Patterns**: Reveal which sentences respond similarly to parameters

### 3. Sensitivity Analysis Plots
Four-panel visualizations showing:

1. **Individual match scores**: How closest matches change
2. **Overall scores**: How final ISEC changes
3. **Distance components**: Semantic vs. cost distances
4. **Closest matches table**: Which sentences are selected at each parameter value

## Practical Parameter Selection Guide

### Step 1: Start with Balanced Settings
```
ISEC_SEMANTIC_WEIGHT=0.5        # Equal emphasis on meaning and structure
DEFAULT_SUBSTITUTION_COST=1.0   # Standard operation costs
DEFAULT_INSERTION_COST=1.0
DEFAULT_DELETION_COST=1.0
DEFAULT_TRANSPOSITION_COST=1.0
COST_FACTOR_PENALIZATION=0.1    # Light penalty for structural changes
```

### Step 2: Understand Your Domain Needs
- **Meaning-focused analysis**: Increase semantic weight (0.7-1.0)
- **Structure-focused analysis**: Decrease semantic weight (0.0-0.3)
- **Technical/structured data**: May need adjusted operation costs
- **Noisy data**: May benefit from higher cost factors

### Step 3: Validate Results
Run sensitivity analysis to ensure:
- Key findings are robust across parameter ranges
- No dramatic ranking changes in critical regions
- Results align with domain expertise

### Step 4: Fine-tune for Specific Goals
- **Finding common patterns**: Use higher semantic weights
- **Finding structural variants**: Use lower semantic weights
- **Balanced discovery**: Use medium semantic weights

## Common Patterns and Interpretations

### Pattern 1: Stable Rankings
**Indicators**:
- Parallel trajectory lines
- Consistent closest matches across parameters
- Small score variations

**Interpretation**:
- Robust results
- Clear similarity relationships
- Reliable for decision-making

### Pattern 2: Ranking Changes
**Indicators**:
- Crossing trajectory lines
- Changing closest matches
- Large score variations

**Interpretation**:
- Parameter-sensitive results
- Complex similarity relationships
- Need for careful parameter selection

### Pattern 3: Extreme Sensitivity
**Indicators**:
- Very steep trajectory slopes
- Dramatic score changes
- Unstable closest matches

**Interpretation**:
- Results highly dependent on parameters
- May indicate edge cases in data
- Requires domain expertise for interpretation

## Domain-Specific Recommendations

### Text/Document Analysis
- **Semantic weight**: 0.6-0.8 (meaning is important)
- **Operation costs**: Default (1.0)
- **Cost factor**: Default (0.1)

### Code/Structured Data
- **Semantic weight**: 0.3-0.5 (structure is important)
- **Operation costs**: May need adjustment for specific syntax
- **Cost factor**: 0.2-0.3 (structural changes are significant)

### Biological Sequences
- **Semantic weight**: 0.4-0.6 (both meaning and structure matter)
- **Operation costs**: Domain-specific (e.g., higher for rare mutations)
- **Cost factor**: 0.1-0.2 (some penalty for edit operations)

## Troubleshooting Common Issues

### Issue 1: All Scores Are Very High/Low
**Possible Causes**:
- Extreme parameter values
- Very similar/dissimilar dataset
- Incorrect cost settings

**Solutions**:
- Check parameter ranges
- Normalize operation costs
- Adjust semantic weight

### Issue 2: Rankings Change Dramatically
**Possible Causes**:
- High parameter sensitivity
- Conflicting similarity measures
- Insufficient data diversity

**Solutions**:
- Use sensitivity analysis to find stable regions
- Validate with domain expertise
- Consider ensemble approaches

### Issue 3: Unexpected Closest Matches
**Possible Causes**:
- Parameter settings don't match intuition
- Embedding model limitations
- Cost matrix issues

**Solutions**:
- Review parameter settings
- Check embedding quality
- Validate custom costs

## Best Practices

### 1. Always Run Sensitivity Analysis
- Understand parameter impact before final analysis
- Identify stable parameter ranges
- Validate key findings

### 2. Document Parameter Choices
- Record rationale for parameter selection
- Note domain-specific considerations
- Track changes over time

### 3. Validate with Domain Experts
- Ensure results align with expectations
- Get feedback on closest matches
- Confirm parameter interpretations

### 4. Consider Multiple Parameter Sets
- Run analysis with different parameter combinations
- Compare results across settings
- Look for consistent patterns

## Next Steps

### 1. Run Full Analysis
```bash
python parameter_sensitivity_analysis.py
```

### 2. Review Generated Files
- `semantic_weight_analysis.png`
- `cost_factor_analysis.png`
- `operation_cost_analysis.png`
- `isec_heatmap_all_sentences.png`
- `sentence_trajectories.png`
- `sensitivity_report.xlsx`

### 3. Apply Insights to Your Work
- Select appropriate parameters for your domain
- Validate results with sensitivity analysis
- Document your parameter selection process

## Related Documentation

- [ISEC Main Documentation](ISEC_README.md)
- [Parameter Sensitivity Analysis](PARAMETER_SENSITIVITY_README.md)
- [Semantic Distance Documentation](SEMANTIC_DISTANCE_README.md)
- [Edit Distance Documentation](COST_MATRIX_README.md)