# ISEC Project

This repo introduces the Index of Sensitivity to Categorical Error (ISEC), a novel metric designed to proactively detect vulnerable category pairs in datasets dominated by user‑generated text, a common challenge for small and medium‑sized enterprises (SMEs). ISEC integrates semantic similarity, morphological distance with customizable cost matrices, and normalized frequency to quantify the risk of confusion between categorical values. A reproducible methodology is proposed and validated through three heterogeneous case studies: over one million public administration records (CAJ), a retail product catalog with more than 25,000 items, and a synthetic dataset of ISO technical codes. Results demonstrate that ISEC effectively identifies high‑risk category pairs, supports early detection of data quality issues, and scales efficiently through a hybrid semantic and morphological approach. The metric proves practical for SMEs by operating on standard hardware using open‑source tools, while enabling improvements in data governance, normalization, and decision‑making reliability. 

---
# ISEC - Índice de Sensibilidad al Error Categórico Calculator

Combined metric that merges semantic similarity and morphological edit distance to evaluate sentences with frequency normalization.

## Overview

ISEC (Índice de Sensibilidad al Error Categórico / Index of Sensitivity to Categorical Error) is a hybrid metric designed to measure the structural and semantic distance of sentences relative to their frequency distribution. It combines:

1. **Semantic Distance** - Measures semantic similarity using Ollama embeddings and Chroma vector database
2. **Morphological Distance** - Measures character-level edit distance using Levenshtein-Damerau algorithm with custom costs
3. **Frequency Normalization** - Normalizes by frequency median to account for usage frequency
4. **Top-K Matching** - Compares against top k closest semantic neighbors for robust analysis

## Formula

ISEC is calculated for each unique sentence-match pair (no aggregation across matches):

$$\text{ISEC}_{\text{pair}} = \frac{1 + \log_{10}(FM_{pair})}{DS^\alpha \cdot DM^{1-\alpha}}$$

Where:
- **Numerator** = $1 + \log_{10}(\text{Mean}(Freq_{source}, Freq_{match}))$
- **DS (SemanticDistance)** = Semantic distance (0.0-1.0)
- **DM (CostDistance)** = Penalized edit distance (normalized)
- **$\alpha$ (Alpha)** = Exponent controlling balance (0.0-1.0)
- **Denominator** = Geometric Mean of DS and DM weighted by $\alpha$

**Note:** ISEC is applied to different categories only. Each sentence is unique within its category, so there is no chance of zero values in any component.

## Configuration

All parameters are defined in `.env` file and loaded automatically.

### Default Configuration (.env)

```dotenv
# ISEC Alpha Configuration
ISEC_ALPHA=0.2                    # Geometric Mean exponent (0.2 = heavy morphologic bias)
ISEC_TOP_K_MATCHES=3              # Number of top semantic matches to compare
ISEC_OUTPUT_FILE=ISEC_Results.xlsx # Output Excel filename

# File Paths
SENTENCES_FILE=Clases.xlsx
CUSTOM_COSTS_FILE=Costo_Personalizado.xlsx

# Column Names
SENTENCES_NAME_COLUMN=Name
SENTENCES_FREQUENCY_COLUMN=Frequency
SENTENCES_GROUP_COLUMN=Group              # Column name for group classification (optional)
SENTENCES_SUBGROUP_COLUMN=Subgroup        # Column name for subgroup classification (optional)
COSTS_CHAR1_COLUMN=Character1
COSTS_CHAR2_COLUMN=Character2
COSTS_COST_COLUMN=Cost
COSTS_OPERATION_COLUMN=Operation

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=embeddinggemma

# Edit Distance Costs
DEFAULT_SUBSTITUTION_COST=1.0
DEFAULT_INSERTION_COST=1.0
DEFAULT_DELETION_COST=1.0
DEFAULT_TRANSPOSITION_COST=1.0
COST_FACTOR_PENALIZATION=0.1

# Metadata Filtering Options
SAME_GROUP_EXCLUSION=False        # Set to True to exclude matches within the same group
SAME_SUBGROUP_EXCLUSION=False     # Set to True to exclude matches within the same subgroup
```

### Key Parameters

- **ISEC_ALPHA** - Geometric Mean exponent (0.0 to 1.0)
  - **$\alpha = 0.5$**: Equal sensitivity to Semantic and Morphological distance.
  - **$\alpha > 0.5$**: Higher sensitivity to Semantic Distance (DS). Small changes in meaning cause larger score drops.
  - **$\alpha < 0.5$**: Higher sensitivity to Morphological Distance (DM). Small typos cause larger score drops.
  - **Example**: `0.2` puts more emphasis on morphological exactness (typos matter more).

- **ISEC_TOP_K_MATCHES** - Number of closest semantic neighbors to compare
  - Higher values → more matches analyzed but slower computation
  - Lower values → faster but fewer comparisons
  - Each match gets its own Excel row with independent ISEC score

- **ISEC_OUTPUT_FILE** - Output Excel filename
  - Default: `ISEC_Results.xlsx`
  - Customize the output filename without code changes

- **COST_FACTOR_PENALIZATION** - Penalty factor for edit operations (insertion, deletion, substitution) in edit distance (default: 0.1)
  - Higher values → edits are penalized more heavily
  - Lower values → edits have less impact on the final distance
  - Applied as: `penalized_distance = avg_cost + factor × (insertion_cost + deletion_cost + substitution_cost)`
  - Note: Transposition costs are not included in the penalization

- **SAME_GROUP_EXCLUSION** - When set to `True`, excludes matches that belong to the same group as the query sentence
  - Useful for analyzing cross-group similarities only
  - Default: `False`

- **SAME_SUBGROUP_EXCLUSION** - When set to `True`, excludes matches that belong to the same subgroup as the query sentence
  - Provides finer-grained filtering than group exclusion
  - Default: `False`

- **SENTENCES_GROUP_COLUMN** - Excel column name containing group classification data (optional)
  - Used for group-based filtering and included in output
  - If not present in Excel, group fields will be empty

- **SENTENCES_SUBGROUP_COLUMN** - Excel column name containing subgroup classification data (optional)
  - Used for subgroup-based filtering and included in output
  - If not present in Excel, subgroup fields will be empty

## Prerequisites

### Python Environment
- Python 3.12+
- uv package manager (recommended)

### Required Services
- **Ollama** running locally with embedding model
  - Default: `http://localhost:11434`
  - Model: `embeddinggemma`

### Python Dependencies
```bash
numpy
pandas
openpyxl
python-dotenv
chromadb
ollama
```

## Installation & Setup

### 1. Ensure Ollama is Running
```bash
# Start Ollama service (if not already running)
ollama serve

# In another terminal, verify the model is available
ollama pull embeddinggemma
```

### 2. Prepare Excel Files

#### Clases.xlsx (Sentences File)
Required columns: `Name`, `Frequency`
Optional columns: `Group`, `Subgroup` (for filtering and analysis)

| Name     | Frequency | Group   | Subgroup |
| -------- | --------- | ------- | -------- |
| XDKT11T3 | 1         | Group_A | Sub_A1   |
| XDKG11T3 | 2         | Group_A | Sub_A2   |
| LDKT11T3 | 1         | Group_B | Sub_B1   |

**Column descriptions:**
- **Name** - The sentence/identifier to analyze
- **Frequency** - How often this sentence appears in the dataset
- **Group** (optional) - Broad classification category for the sentence
- **Subgroup** (optional) - Sub-classification within the group

#### Costo_Personalizado.xlsx (Custom Costs File - Optional)
Required columns: `Character1`, `Character2`, `Cost`, (optional) `Operation`

| Character1 | Character2 | Cost | Operation    |
| ---------- | ---------- | ---- | ------------ |
| D          | X          | 0.5  | substitution |
| G          | T          | 0.5  | substitution |

### 3. Run the Calculator

```bash
# Activate environment
source .venv/bin/activate

# Run ISEC calculator
python ISEC.py
```

The script will:
1. Display configuration (alpha, top k matches, output file)
2. Load sentences and frequencies from Excel
3. Initialize semantic and cost calculators
4. Calculate ISEC metrics for each sentence-match pair
5. Generate report with detailed statistics
6. Export results to Excel file with one row per match

## Usage

### Basic Usage
```python
from ISEC import ISECCalculator

# Create calculator (loads from .env)
calculator = ISECCalculator()

# Calculate ISEC for all sentences
results = calculator.calculate_all_isec()

# Display results
calculator.print_batch_results(results)

# Export to Excel
calculator.export_to_excel(results, "ISEC_Results.xlsx")
```

## Web Interface (App)

The project includes a web interface to explore the models and visualize the ISEC calculations.

### Running the App

```bash
# Using uv (recommended)
uv run python app/main.py

# Or using uvicorn directly
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Once running, you can access the interface at `http://localhost:8000`.

The app allows you to:
- Browse different collections of sentences.
- Adjust parameters (Alpha, Costs) in real-time.
- Visualize semantic and morphological distances for specific pairs.
- Export results for the entire collection.

### Custom Configuration
```python
# Override configuration
calculator = ISECCalculator(
    sentences_file="MyData.xlsx",
    alpha=0.5,  # 0.5 = Balanced Geometric Mean

)

# Calculate for single sentence
result = calculator.calculate_isec("XDKT11T3", frequency=1)
calculator.print_result(result)
```

## Output Format

### Console Output

```
==============================================================================================
ISEC (Índice de Sensibilidad al Error Categórico) Analysis
==============================================================================================

'XDKT11T3'
----------------------------------------------------------------------------------------------------
  Frequency: 1
  Numerator (1 + log10): 1.0000
  Group: Group_A

  Top 2 Semantic Matches with ISEC Scores:
    1. 'XDKG11T3'
       Semantic Distance: 0.2345  |  Cost Distance: 0.5000  |  ISEC: 1.2500  |  Group: Group_A  |  Frequency: 2
    2. 'LDKT11T3'
       Semantic Distance: 0.4567  |  Cost Distance: 1.5000  |  ISEC: 0.8750  |  Group: Group_B  |  Frequency: 3

  Weights: semantic=40.0%, morphologic=60.0%

============================================================================================== 
Summary Statistics
==============================================================================================

  Total sentences analyzed: 3
  Total match pairs analyzed: 6
  Pair Numerator (1 + log10):
    Average: 1.1111
    Min: 1.0000
    Max: 1.2500
  ISEC Scores (per match pair):
    Average: 1.0842
    Min: 0.8750
    Max: 1.2500
    Median: 1.1850
```

### Excel Export

**ISEC_Results.xlsx** - One row per top k match for detailed analysis:

| Sentence | Sentence_Group | Frequency | FMN  | Match_Rank | Matched_Sentence | Matched_Sentence_Group | Matched_Frequency | Semantic_Distance | Cost_Distance | ISEC_Score |
| -------- | -------------- | --------- | ---- | ---------- | ---------------- | ---------------------- | ----------------- | ----------------- | ------------- | ---------- |
| XDKT11T3 | Group_A        | 1         | 1.0  | 1          | XDKG11T3         | Group_A                | 2                 | 0.2345            | 0.5000        | 1.2500     |
| XDKT11T3 | Group_A        | 1         | 1.0  | 2          | LDKT11T3         | Group_B                | 3                 | 0.4567            | 1.5000        | 0.8750     |
| XDKG11T3 | Group_A        | 2         | 1.25 | 1          | XDKT11T3         | Group_A                | 1                 | 0.2345            | 0.5000        | 1.5625     |
| XDKG11T3 | Group_A        | 2         | 1.25 | 2          | LDKT11T3         | Group_B                | 3                 | 0.3456            | 1.0000        | 1.3750     |

**Key features:**
- Each row represents one independent ISEC calculation for a specific sentence-match pair
- Original sentence and matched sentence information shown separately
- Match_Rank shows position (1st, 2nd, 3rd closest)
- Both source and matched sentence frequencies are included
- Group information for both sentences when available
- Individual ISEC score calculated per pair (no aggregated metrics)
- Total rows = (number of sentences) × (top k matches)

**Metadata Filtering:** When `SAME_GROUP_EXCLUSION=True` or `SAME_SUBGROUP_EXCLUSION=True` in `.env`, matches within the same group/subgroup are excluded from results.

## API Reference

### ISECCalculator Class

```python
class ISECCalculator:
    def __init__(
        self,
        sentences_file: str = None,
        custom_costs_file: str = None,
        ollama_host: str = None,
        embedding_model: str = None,
        alpha: float = None,
    )
```

**Methods:**

#### `calculate_isec(sentence: str, frequency: int) -> ISECResult`
Calculate ISEC metric for a single sentence.

```python
result = calculator.calculate_isec("XDKT11T3", frequency=1)
print(f"ISEC Score: {result.isec_score:.4f}")
```

#### `calculate_all_isec() -> List[ISECResult]`
Calculate ISEC metric for all loaded sentences.

```python
results = calculator.calculate_all_isec()
for result in results:
    print(f"{result.sentence}: {result.isec_score:.4f}")
```

#### `find_top_k_semantic_sentences(query_sentence: str, k: int = 3) -> List[Tuple[str, float]]`
Find top k closest semantic matches for a sentence.

```python
matches = calculator.find_top_k_semantic_sentences("XDKT11T3", k=3)
for sentence, distance in matches:
    print(f"{sentence}: {distance:.4f}")
```

#### `print_result(result: ISECResult) -> None`
Print formatted output for a single result.

```python
calculator.print_result(result)
```

#### `print_batch_results(results: List[ISECResult]) -> None`
Print formatted output with summary statistics for all results.

```python
calculator.print_batch_results(results)
```

#### `export_to_excel(results: List[ISECResult], output_file: str = "ISEC_Results.xlsx") -> None`
Export results to Excel file.

```python
calculator.export_to_excel(results, "my_analysis.xlsx")
```

### ISECResult Dataclass

```python
@dataclass
class ISECResult:
    sentence: str                                              # Input sentence
    frequency: int                                             # Frequency of sentence
    frequency_median_normalized: float                         # FMN value
    top_k_matches: List[Tuple[str, float, float, float, Dict]]  # (sentence, semantic_dist, cost_dist, isec_score, metadata)
```

## Interpretation

### ISEC Score Components

The Excel export provides individual ISEC scores for each sentence-match pair:

- **ISEC_Score** - Individual ISEC for each specific sentence-match pair
  - Calculated independently for each match using the formula above
  - Each row in the Excel represents one unique pair calculation
  - No averaging is performed across matches

### ISEC Score Meaning

**Formula: ISEC = (1 + log10(MeanFreq)) / (DS^α × DM^(1-α))**

ISEC measures the **sensitivity to categorical error** for each unique sentence-match pair:

**Higher ISEC scores indicate HIGHER sensitivity to error:**
- **High frequency** → High numerator (FMN) → More opportunities for error
- **Small semantic distance** → Semantically similar to neighbors → Easy to confuse
- **Small morphological distance** → Structurally similar → Typing errors likely to produce this neighbor
- **High risk of misinterpretation** → An error in typing may result in this similar sentence being selected instead

**Why similarity is BAD for sensitivity:**
When two sentences are very similar (semantically and morphologically), a typing error or auto-correction may inadvertently change one into the other. This is particularly dangerous when:
- The sentences have different meanings but similar structure
- Users frequently type one when they mean the other
- The system may auto-correct to the wrong sentence

**Lower ISEC scores indicate LOWER sensitivity to error:**
- **Low frequency** → Fewer occurrences, less exposure to potential errors
- **Large semantic distance** → Semantically distinct, unlikely to be confused
- **Large morphological distance** → Structurally different, typing errors won't easily produce this
- **Low risk of misinterpretation** → Errors are unlikely to result in this sentence

### Practical Examples

- **ISEC = 0.5** → Low sensitivity (rare, unique sentence very different from others)
- **ISEC = 1.0** → Moderate sensitivity (some distinctiveness but moderate frequency)
- **ISEC = 2.0** → High sensitivity (common sentence with close neighbors - error-prone)
- **ISEC = 5.0+** → Very high sensitivity (very common, highly similar to neighbors - high error risk)

### Comparative Analysis

Use Excel columns to analyze:
- **Match_Rank 1 vs Match_Rank 2 vs Match_Rank 3** - Increasing dissimilarity (decreasing similarity)
- **Match_ISEC variations** - Which matches show highest error sensitivity
- **Semantic_Distance trends** - Semantic similarity patterns
- **Cost_Distance trends** - Morphological similarity patterns
- **High ISEC sentences** - Common structural patterns with high error risk
- **Low ISEC sentences** - Unique/rare structural patterns with low error risk

### Frequency Calculation Example
The numerator is calculated using the Base-10 Logarithm of the **pair's mean frequency**:
$$Numerator = 1 + \log_{10}\left(\frac{F_{source} + F_{match}}{2}\right)$$

**Examples:**
1. **Rare Pair:**
   - Source Freq = 1, Match Freq = 1
   - Mean = 1.0
   - $\log_{10}(1) = 0$
   - **Numerator = 1.0**

2. **Mixed Pair:**
   - Source Freq = 1, Match Freq = 100
   - Mean = 50.5
   - $\log_{10}(50.5) \approx 1.703$
   - **Numerator = 2.703**

3. **High Frequency Pair:**
   - Source Freq = 1000, Match Freq = 1000
   - Mean = 1000
   - $\log_{10}(1000) = 3$
   - **Numerator = 4.0**

## Performance Considerations

### Computation Time
- Scales with number of sentences (O(n × k))
- Semantic matching: ~0.1-0.5s per sentence
- Cost distance calculation: ~0.01s per match
- For 100 sentences with k=3: ~10-50 seconds total

### Memory Usage
- Chroma vector database in-memory: ~10MB per 1000 embeddings
- Cost matrices: Negligible (~1MB)

### Optimization Tips
1. Reduce `ISEC_TOP_K_MATCHES` for faster execution (3-5 recommended)
2. Use smaller sentences for faster semantic matching
3. Pre-load Ollama embeddings if processing multiple batches
4. Use batch Excel export instead of individual queries

## Troubleshooting

### "No custom costs declared"
- Check that `CUSTOM_COSTS_FILE` exists and is readable
- Verify Excel file has columns: `Character1`, `Character2`, `Cost`
- Ensure column names match `.env` configuration

### "Ollama connection refused"
- Verify Ollama is running: `ollama serve`
- Check `OLLAMA_HOST` in `.env` is correct (default: `http://localhost:11434`)
- Verify embedding model exists: `ollama list`

### "ImportError: No module named 'chromadb'"
- Install dependencies: `uv pip install chromadb ollama`
- Or: `pip install -r requirements.txt`

## Project Structure

```
ISEC/
├── app/                          # Web interface and API
│   ├── main.py                   # FastAPI server
│   ├── static/                   # Frontend assets
│   ├── data/                     # Data files for the app
│   └── ...
├── datasets/                     # Example datasets (Excel files)
├── resultados/                   # Analysis results and exports
├── matriz_costo_caracteres.py     # Levenshtein-Damerau calculator
├── Distancia_Semantica.py         # Semantic distance calculator
├── ISEC.py                        # Main ISEC calculator
├── config.py                      # Configuration loader
├── .env                           # Configuration file
├── pyproject.toml                 # Project configuration and dependencies
├── verify_setup.py                # Setup verification script
├── quickstart.py                  # Quick start example
├── setup_demo.sh                  # Setup demonstration script
└── README.md                      # This file
```

## Dependencies

- **numpy** (≥1.24.0) - Numerical computing
- **pandas** (≥2.0.0) - Data manipulation and Excel I/O
- **openpyxl** (≥3.0.0) - Excel file reading/writing
- **chromadb** - Vector database for embeddings
- **ollama** - Ollama API client
- **python-dotenv** - Environment variable loading

## License

MIT License - See LICENSE file for details

## Citation

If you use ISEC in academic research, please cite:

```bibtex
@software{isec2026,
  title={ISEC: Índice de Sensibilidad al Error Categórico},
  author={Mauro A. Benetti},
  year={2026},
  url={https://github.com/mbenetti/ISEC}
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Make your changes
4. Run tests and validation
5. Submit a pull request

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section above
- Review configuration in `.env`
- Check Ollama and Chroma setup
- Verify Excel file formats

## Related Projects documentation

- [Levenshtein-Damerau Distance Calculator](COST_MATRIX_README.md)
- [Semantic Distance Calculator](SEMANTIC_DISTANCE_README.md)

## Algorithm Pseudocode

### Detailed Algorithm: ISEC Calculation

```
ALGORITHM: ISEC (Índice de Sensibilidad al Error Categórico) Calculation

INPUT:
    - sentence: The target sentence to analyze
    - frequency: How often this sentence appears
    - top_k: Number of closest semantic neighbors to compare
    - alpha: Geometric Mean exponent (0.0-1.0)

PROCESS:
    1. Calculate Pair Numerator
       mean_freq = (frequency + match_frequency) / 2
       Numerator = 1 + log10(mean_freq)
    
    2. Find top K closest semantic matches (by embedding similarity)
       top_k_matches = []
       FOR each other_sentence in sentences (excluding query):
           embedding_distance = semantic_distance(sentence, other_sentence)
           IF embedding_distance is in top K:
               top_k_matches.append((other_sentence, embedding_distance))
    
    3. FOR each match in top_k_matches:
           a. Calculate morphological (edit) distance
              cost_distance = penalized_levenshtein_distance(sentence, match)
           
           b. Calculate ISEC for this specific pair
              denominator = pow(semantic_dist, alpha) * pow(cost_distance, 1-alpha)
              isec_score = Numerator / denominator
           
           c. Store match data: (matched_sentence, semantic_dist, cost_dist, isec_score)
           d. Output individual ISEC score for this pair (no aggregation)

OUTPUT:
    - ISECResult containing:
        * Original sentence and frequency
        * FMN value
        * Top K matches with individual ISEC scores (one per pair)
```

### Simplified Algorithm (For Papers)

```
ALGORITHM: ISEC - Índice de Sensibilidad al Error Categórico

INPUT:
    - S: set of sentences with frequencies
    - s: target sentence
    - freq(s): frequency of sentence s
    - k: number of top matches
    - α: Alpha bias (0 ≤ α ≤ 1)

OUTPUT:
    - List of ISEC scores, one per match

BEGIN:
    1. M ← FindTopKSemanticMatches(s, S, k)
    
    2. FOR each match m ∈ M:
           mean_freq ← (freq(s) + freq(m)) / 2
           numerator ← 1 + log10(mean_freq)
           
           d_sem(m) ← SemanticDistance(s, m)
           d_cost(m) ← PenalizedEditDistance(s, m)
           
           denominator ← (d_sem(m)^α) * (d_cost(m)^(1-α))
           isec_m ← numerator / denominator
           OUTPUT isec_m
       END FOR
END
```

### LaTeX Algorithm (for Academic Papers)

```latex
\begin{algorithm}
\caption{ISEC: Índice de Sensibilidad al Error Categórico Calculator}
\begin{algorithmic}[1]
\Require{sentences $S = \{s_1, s_2, \ldots, s_n\}$ with frequencies $\text{freq}(s_i)$; target sentence $s$; top-k matches $k$; Alpha bias $\alpha \in [0,1]$}
\Ensure{List of ISEC scores, one per sentence-match pair}

\State $\text{median\_freq} \gets \text{median}(\{\text{freq}(s') \mid s' \in S\})$
\State $\text{FMN} \gets \text{freq}(s) / \text{median\_freq}$

\State $\mathcal{M} \gets \text{FindTopKSemanticMatches}(s, S, k)$

\For{each match $m \in \mathcal{M}$}
    \State $\text{num} \gets 1 + \log_{10}((\text{freq}(s) + \text{freq}(m))/2)$
    \State $d_{\text{sem}}(m) \gets \text{SemanticDistance}(s, m)$
    \State $d_{\text{cost}}(m) \gets \text{PenalizedEditDistance}(s, m)$
    \State $d_{\text{geom}} \gets d_{\text{sem}}(m)^{\alpha} \cdot d_{\text{cost}}(m)^{1-\alpha}$
    \State $\text{ISEC}(s, m) \gets \text{num} / d_{\text{geom}}$
    \State \textbf{output} $\text{ISEC}(s, m)$
\EndFor

\end{algorithmic}
\end{algorithm}
```

### Sub-algorithms

#### FindTopKSemanticMatches

```latex
\begin{algorithm}
\caption{FindTopKSemanticMatches}
\begin{algorithmic}[1]
\Require{target sentence $s$; all sentences $S$; number of matches $k$}
\Ensure{list of top-$k$ closest matches $\mathcal{M}$}

\State $\mathcal{M} \gets \emptyset$
\State $\text{embedding}_s \gets \text{GetEmbedding}(s)$

\For{each $s' \in S \setminus \{s\}$}
    \State $\text{embedding}_{s'} \gets \text{GetEmbedding}(s')$
    \State $d \gets \text{CosineSimilarity}(\text{embedding}_s, \text{embedding}_{s'})$
    \State Insert $(s', d)$ into $\mathcal{M}$ (sorted by distance)
    \If{$|\mathcal{M}| > k$}
        \State Remove element with largest distance from $\mathcal{M}$
    \EndIf
\EndFor

\Return $\mathcal{M}$ (sorted by distance, ascending)
\end{algorithmic}
\end{algorithm}
```

#### PenalizedEditDistance

```latex
\begin{algorithm}
\caption{PenalizedEditDistance}
\begin{algorithmic}[1]
\Require{strings $s_1, s_2$; operation costs}
\Ensure{penalized distance $d_p$}

\State $d_{\text{total}} \gets \text{LevenshteinDamerau}(s_1, s_2)$
\State $\text{ops} \gets \text{GetOperations}(s_1, s_2)$

\State $d_{\text{edit}} \gets \sum_{\text{op} \in \text{ops}} \text{cost(op)} \mid \text{op} \in \{\text{INSERT}, \text{DELETE}, \text{SUBSTITUTE}\}$

\State $d_{\text{avg}} \gets d_{\text{total}} / \text{NumOperations(ops)}$

\State $k \gets \text{OperationCostFactor}$ \Comment{typically 0.1}

\State $d_p \gets d_{\text{avg}} + k \cdot d_{\text{edit}}$

\Return $d_p$
\end{algorithmic}
\end{algorithm}
```

## Data Structures

### ISECResult

```
STRUCTURE: ISECResult
    sentence: str                                           // Input sentence
    frequency: int                                          // Frequency of sentence
    top_k_matches: List[Tuple[str, float, float, float]]   // (sentence, semantic_dist, cost_dist, isec_score)
    // Note: Each match has its own independent ISEC score
    // No averaging is performed across matches
END STRUCTURE
```

### Performance Characteristics

- **Time Complexity**: O(n × k × m) where:
  - n = number of sentences
  - k = top-k matches
  - m = average sentence length
  
- **Space Complexity**: O(n × d) where:
  - n = number of sentences
  - d = embedding dimension (typically 384-1024)

## Related Projects

- [Levenshtein-Damerau Distance Calculator](COST_MATRIX_README.md)
- [Semantic Distance Calculator](SEMANTIC_DISTANCE_README.md)

---

# ISEC System: Levenshtein-Damerau Distance Calculator with Custom Operation Costs and Metadata Filtering

A comprehensive Python system for calculating **Levenshtein-Damerau distance** with customizable operation costs and **metadata filtering**. Includes semantic distance calculation with Ollama embeddings and ISEC (Índice de Sensibilidad al Error Categórico) metric calculation. Perfect for linguistic analysis, semantic similarity, and structural edit cost analysis.

## System Components

### 1. **Levenshtein-Damerau Distance Calculator** (`matriz_costo_caracteres.py`)
### 2. **Semantic Distance Calculator** (`Distancia_Semantica.py`) 
### 3. **ISEC Calculator** (`ISEC.py`)

## Features

✨ **Core Features:**

### Levenshtein-Damerau Calculator:
- **Levenshtein-Damerau distance calculation** (supports transposition)
- **Configurable default costs** for all operation types
- **Custom character pair costs** for substitution and transposition
- **Symmetric cost handling** (A→B cost = B→A cost)
- **Character matrices** showing all pairwise costs
- **Batch distance calculation** between multiple sentences
- **Metadata filtering** to exclude comparisons within same group/subgroup
- **Detailed operation tracking** with cost breakdown

### Semantic Distance Calculator:
- **Ollama embeddings** for semantic similarity
- **Chroma vector database** for efficient similarity search
- **Cosine similarity and distance** metrics
- **Metadata filtering** for group/subgroup exclusion
- **Top-k semantic matches** with filtering support

### ISEC Calculator:
- **Índice de Sensibilidad al Error Categórico** metric calculation
- **Per-pair ISEC scores** (no aggregated metrics)
- **Per-pair ISEC scores** (no aggregated metrics)
- **Simplified Frequency Log-Scaling** ($1 + \log_{10}$)
- **Complete frequency information** for both source and matched sentences
- **Excel export** with independent per-pair calculations
- **Metadata filtering** integrated with semantic matching

## Installation with uv

This project uses [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver.

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
uv pip install python-dotenv numpy pandas openpyxl chromadb ollama
```

### Prerequisites

1. **Install Ollama** for semantic embeddings:
   ```bash
   # On macOS/Linux
   brew install ollama
   
   # Or download from https://ollama.ai
   ```

2. **Pull the embedding model**:
   ```bash
   ollama pull embeddinggemma
   ```

3. **Start Ollama service**:
   ```bash
   ollama serve
   ```

## Configuration

The system uses a `.env` file for configuration. Key settings include:

### Operation Costs:
```
DEFAULT_SUBSTITUTION_COST=1.0
DEFAULT_INSERTION_COST=1.0
DEFAULT_DELETION_COST=1.0
DEFAULT_TRANSPOSITION_COST=1.0
COST_FACTOR_PENALIZATION=0.1
```

### File Paths:
```
SENTENCES_FILE=Clases.xlsx
CUSTOM_COSTS_FILE=Custom_cost.xlsx
ISEC_OUTPUT_FILE=ISEC_Results.xlsx
```

### Column Names:
```
SENTENCES_NAME_COLUMN=Name
SENTENCES_FREQUENCY_COLUMN=Frequency
SENTENCES_GROUP_COLUMN=Group
SENTENCES_SUBGROUP_COLUMN=Subgroup
```

### Metadata Filtering:
```
SAME_GROUP_EXCLUSION=False
SAME_SUBGROUP_EXCLUSION=False
```

### Ollama Settings:
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=embeddinggemma
```

### ISEC Settings:
```
ISEC_ALPHA=0.2  # Geometric Mean exponent
ISEC_TOP_K_MATCHES=3
```

## Quick Start

## Quick Start Examples

### 1. Basic Levenshtein-Damerau Distance

```python
from matriz_costo_caracteres import EditCostCalculator, load_sentences_from_excel

# Create calculator with default costs
calc = EditCostCalculator()

# Define custom costs for similar character pairs
calc.set_custom_substitution_cost("A", "S", 0.5)  # A and S substitution costs 0.5
calc.set_custom_substitution_cost("E", "I", 0.5)  # E and I substitution costs 0.5

# Setup from sentences
sentences = ["CASE", "SASE", "CISE"]
all_chars = set("".join(sentences))
calc.setup_characters(list(all_chars))

# Calculate distance
result = calc.calculate_edit_distance("CASE", "SASE")
print(f"Distance: {result.total_distance}")
print(f"Operations: {result.num_operations}")
print(f"Average cost: {result.average_cost:.4f}")
print(f"Penalized distance: {result.penalized_distance:.4f}")

# Calculate all pairwise distances
results = calc.calculate_all_distances(sentences)
calc.print_batch_results(results)
```

### 2. Metadata Filtering with Group/Subgroup Exclusion

```python
from matriz_costo_caracteres import EditCostCalculator, load_sentences_from_excel

# Load sentences with metadata (group, subgroup)
sentences, metadata_list = load_sentences_from_excel(
    "Clases.xlsx",
    name_column="Name",
    frequency_column="Frequency",
    group_column="Group",      # Optional
    subgroup_column="Subgroup" # Optional
)

calc = EditCostCalculator()

# Calculate distances with group exclusion
results_no_same_group = calc.calculate_distances_with_filtering(
    sentences,
    metadata_list,
    exclude_same_group=True,      # Exclude comparisons within same group
    exclude_same_subgroup=False   # Keep comparisons within same subgroup
)

print(f"Total comparisons without filtering: {len(sentences)*(len(sentences)-1)//2}")
print(f"Comparisons with group exclusion: {len(results_no_same_group)}")
```

### 3. Semantic Distance with Ollama
```python
from Distancia_Semantica import SemanticDistanceCalculator

# Create semantic calculator
semantic_calc = SemanticDistanceCalculator(
    ollama_host="http://localhost:11434",
    embedding_model="embeddinggemma"
)

# Load sentences and metadata
sentences = ["The cat sat on the mat", "A feline rested on the rug"]
metadata_list = [
    {"frequency": 100, "group": "cats"},
    {"frequency": 50, "group": "cats"}
]

semantic_calc.load_sentences(sentences, metadata_list)

# Find closest match excluding same group
result = semantic_calc.find_closest_sentence(
    "The cat sat on the mat",
    exclude_same_group=True  # Will return None since only cats group exists
)

# Find top k matches with filtering
top_matches = semantic_calc.find_top_k_semantic_matches(
    "The cat sat on the mat",
    k=3,
    exclude_same_group=False,
    exclude_same_subgroup=False
)
```

### 4. ISEC Calculation with Per-Pair Results
```python
from ISEC import ISECCalculator

# Create ISEC calculator
isec_calc = ISECCalculator(
    sentences_file="Clases.xlsx",
    alpha=0.2  # Bias towards morphological (0.2) or semantic (0.8)
)

# Calculate ISEC for all sentences
results = isec_calc.calculate_all_isec()

# Print results (shows matched sentence frequency)
isec_calc.print_batch_results(results)

# Export to Excel (includes Matched_Frequency column)
isec_calc.export_to_excel(results, "ISEC_Results.xlsx")
```

### 5. Loading from Excel Files

The main scripts automatically load data from Excel files:

1. **Sentences** from `Clases.xlsx`
   - Required columns: `Name`, `Frequency`
   - Optional columns: `Group`, `Subgroup` (for metadata filtering)
   - The frequency is used for ISEC calculations and display

2. **Custom costs** from `Custom_cost.xlsx`
   - Required columns: `Character1`, `Character2`, `Cost`
   - Optional column: `Operation` ("substitution" or "transposition")
   - Defaults to "substitution" if not specified

```python
from matriz_costo_caracteres import load_sentences_from_excel, load_custom_costs_from_excel
from config import Config

# Load sentences with metadata
sentences, metadata_list = load_sentences_from_excel(
    Config.SENTENCES_FILE,
    name_column=Config.SENTENCES_NAME_COLUMN,
    frequency_column=Config.SENTENCES_FREQUENCY_COLUMN,
    group_column=Config.SENTENCES_GROUP_COLUMN,
    subgroup_column=Config.SENTENCES_SUBGROUP_COLUMN
)

# Load custom costs for substitution and transposition
sub_costs, trans_costs = load_custom_costs_from_excel(
    Config.CUSTOM_COSTS_FILE,
    char1_column=Config.COSTS_CHAR1_COLUMN,
    char2_column=Config.COSTS_CHAR2_COLUMN,
    cost_column=Config.COSTS_COST_COLUMN,
    operation_column=Config.COSTS_OPERATION_COLUMN
)

# Create and configure calculator with config defaults
calc = EditCostCalculator(
    default_substitution_cost=Config.DEFAULT_SUBSTITUTION_COST,
    default_insertion_cost=Config.DEFAULT_INSERTION_COST,
    default_deletion_cost=Config.DEFAULT_DELETION_COST,
    default_transposition_cost=Config.DEFAULT_TRANSPOSITION_COST,
)

if sub_costs:
    calc.set_custom_costs(sub_costs, operation="substitution")
if trans_costs:
    calc.set_custom_costs(trans_costs, operation="transposition")

# Setup and calculate
all_chars = set("".join(sentences))
calc.setup_characters(list(all_chars))

# Calculate all distances (without filtering)
results_all = calc.calculate_all_distances(sentences)

# Calculate distances with metadata filtering
if any("group" in metadata for metadata in metadata_list):
    results_filtered = calc.calculate_distances_with_filtering(
        sentences,
        metadata_list,
        exclude_same_group=Config.SAME_GROUP_EXCLUSION,
        exclude_same_subgroup=Config.SAME_SUBGROUP_EXCLUSION
    )
    print(f"All comparisons: {len(results_all)}")
    print(f"Filtered comparisons: {len(results_filtered)}")
```

## Running the Complete System

Run each component separately:

```bash
# 1. Levenshtein-Damerau distance calculator
python matriz_costo_caracteres.py

# 2. Semantic distance calculator (requires Ollama)
python Distancia_Semantica.py

# 3. ISEC calculator (requires both above)
python ISEC.py
```

## Excel Output Format

The ISEC calculator exports to Excel with the following columns:

| Column                   | Description                         |
| ------------------------ | ----------------------------------- |
| `Sentence`               | Source sentence                     |
| `Sentence_Group`         | Group of source sentence            |
| `Frequency`              | Frequency of source sentence        |
| `FMN`                    | Frequency Median Normalized         |
| `Match_Rank`             | Rank of this match (1 to k)         |
| `Matched_Sentence`       | The matched sentence                |
| `Matched_Sentence_Group` | Group of matched sentence           |
| `Matched_Frequency`      | Frequency of matched sentence       |
| `Semantic_Distance`      | Semantic distance between the pair  |
| `Cost_Distance`          | Edit cost distance between the pair |
| `ISEC_Score`             | ISEC score for this specific pair   |

**Key Features:**
- Each row shows independent ISEC calculation for a specific sentence-match pair
- Both source and matched sentence frequencies are included
- No aggregated metrics - only per-pair calculations
- Group information for metadata filtering

## Key Concepts

### Metadata Filtering
- **Group Exclusion**: When `SAME_GROUP_EXCLUSION=True`, exclude comparisons within same group
- **Subgroup Exclusion**: When `SAME_SUBGROUP_EXCLUSION=True`, exclude comparisons within same subgroup
- **Configuration**: Controlled via `.env` file settings
- **Excel Columns**: Use `Group` and `Subgroup` columns in your sentences file

### ISEC Calculation
- **Per-Pair Calculation**: Each match gets its own ISEC score
- **Frequency Display**: Both source and matched sentence frequencies shown
- **No Aggregation**: No average distances or overall scores
- **Independent Rows**: Each Excel row contains complete information for one pair

### File Integration
- **Consistent Metadata**: All three scripts use the same metadata format
- **Configuration-Driven**: All settings in `.env` file
- **Excel Compatibility**: Standard Excel file formats

## API Reference

### Class: `EditCostCalculator`

#### Constructor

```python
EditCostCalculator(
    default_substitution_cost: float = 1.0,
    default_insertion_cost: float = 1.0,
    default_deletion_cost: float = 1.0,
    default_transposition_cost: float = 1.0,
)
```

**Parameters:**
- `default_substitution_cost`: Cost for replacing one character with another
- `default_insertion_cost`: Cost for inserting a character
- `default_deletion_cost`: Cost for deleting a character
- `default_transposition_cost`: Cost for swapping two adjacent characters

#### Methods

##### `set_custom_substitution_cost(char1: str, char2: str, cost: float)`
Set custom cost for substituting between two characters. Automatically handles both directions (symmetric).

```python
calc.set_custom_substitution_cost("A", "S", 0.5)
# Now both A→S and S→A cost 0.5
```

##### `set_custom_transposition_cost(char1: str, char2: str, cost: float)`
Set custom cost for transposing two characters.

```python
calc.set_custom_transposition_cost("A", "B", 0.3)
# Transposing AB→BA costs 0.3
```

##### `set_custom_costs(cost_dict: Dict[Tuple[str, str], float], operation: str)`
Set multiple custom costs at once.

**Parameters:**
- `cost_dict`: Dictionary with format `{(char1, char2): cost}`
- `operation`: Either `"substitution"` or `"transposition"`

```python
costs = {
    ("A", "S"): 0.5,
    ("E", "I"): 0.5,
}
calc.set_custom_costs(costs, operation="substitution")
```

##### `setup_characters(characters: List[str])`
Initialize the cost matrices with the character set.

```python
calc.setup_characters(['A', 'B', 'C', 'S'])
```

##### `calculate_edit_distance(str1: str, str2: str) -> DistanceResult`
Calculate Levenshtein-Damerau distance between two strings.

**Returns:** `DistanceResult` object containing:
- `total_distance`: float - Total edit distance
- `operations`: List[Operation] - List of operations performed
- `num_operations`: int - Number of operations (excluding matches)
- `average_cost`: float - Average cost per operation

```python
result = calc.calculate_edit_distance("HELLO", "HALLO")
print(result.total_distance)
print(result.average_cost)
for op in result.operations:
    print(f"{op.op_type}: {op.from_char} → {op.to_char} (cost: {op.cost})")
```

##### `calculate_all_distances(sentences: List[str]) -> List[DistanceResult]`
Calculate distances between all pairs of sentences.

```python
sentences = ["CAT", "CAR", "BAT"]
results = calc.calculate_all_distances(sentences)
# Returns distances for all pairs: CAT→CAR, CAT→BAT, CAR→CAT, CAR→BAT, etc.
```

##### Display Methods

```python
# Show substitution cost matrix
calc.display_matrix(title="Substitution Costs")

# Show transposition cost matrix
calc.display_transposition_matrix(title="Transposition Costs")

# Show all custom costs
calc.show_custom_costs()

# Print formatted result
calc.print_result(result)

# Print batch results with statistics
calc.print_batch_results(results)
```

### Class: `DistanceResult`

Result object from distance calculation.

**Attributes:**
- `str1: str` - First string
- `str2: str` - Second string
- `total_distance: float` - Total edit distance
- `operations: List[Operation]` - List of operations
- `num_operations: int` - Count of actual operations (property)
- `average_cost: float` - Average cost per operation (property)

### Class: `Operation`

Represents a single edit operation.

**Attributes:**
- `op_type: str` - Operation type: 'match', 'substitute', 'delete', 'insert', 'transpose'
- `from_char: str` - Character being changed
- `to_char: str` - Character it becomes
- `cost: float` - Cost of this operation

## Examples

### Example 1: OCR Error Correction

```python
calc = EditCostCalculator()

# Define common OCR confusions
ocr_confusions = {
    ("L", "I"): 0.3,      # L/I confusion
    ("O", "0"): 0.2,      # O/zero confusion
    ("1", "I"): 0.2,      # 1/I confusion
}

calc.set_custom_costs(ocr_confusions, operation="substitution")

# Characters from words
all_chars = set("HELLOHEI10OI")
calc.setup_characters(list(all_chars))

# Compare original vs OCR result
result = calc.calculate_edit_distance("HELLO", "HE1LO")
print(f"Distance: {result.total_distance}")  # Lower due to custom cost
```

### Example 2: Phonetic Similarity

```python
calc = EditCostCalculator()

# Define phonetically similar pairs
phonetic = {
    ("C", "K"): 0.3,      # Both /k/ sound
    ("S", "Z"): 0.4,      # Similar sibilants
    ("T", "D"): 0.3,      # Both stop consonants
}

calc.set_custom_costs(phonetic, operation="substitution")

# Test words
words = ["CAT", "KATZ", "CATS"]
all_chars = set("".join(words))
calc.setup_characters(list(all_chars))

results = calc.calculate_all_distances(words)
calc.print_batch_results(results)
```

### Example 3: Configurable Operation Costs

```python
# Scenario: Substitution is cheap, insertion/deletion are expensive
calc = EditCostCalculator(
    default_substitution_cost=0.5,   # Cheap
    default_insertion_cost=2.0,       # Expensive
    default_deletion_cost=2.0,        # Expensive
    default_transposition_cost=1.0,
)

# This favors substitution over adding/removing characters
result1 = calc.calculate_edit_distance("CAT", "AT")   # Deletion
result2 = calc.calculate_edit_distance("CAT", "CAR")  # Substitution
```

### Example 4: Batch Analysis with Statistics

```python
calc = EditCostCalculator()

calc.set_custom_costs({
    ("A", "O"): 0.4,
    ("E", "I"): 0.3,
}, operation="substitution")

sentences = ["HELLO", "HALLO", "HIOLO", "HOLLO"]
all_chars = set("".join(sentences))
calc.setup_characters(list(all_chars))

# Calculate all distances
results = calc.calculate_all_distances(sentences)

# Print comprehensive report with statistics
calc.print_batch_results(results)
```

## Matrix Structure

The character cost matrices are square matrices where:
- **Rows** represent the first character
- **Columns** represent the second character
- **Diagonal** (where row == column) always has cost 0.0
- **Off-diagonal** contains the substitution/transposition costs

Example:
```
     A    B    C
A  0.0  0.5  1.0
B  0.5  0.0  1.0
C  1.0  1.0  0.0
```

## Properties of Custom Costs

### Symmetry
When you set a custom cost between two characters, it applies in both directions:
```python
calc.set_custom_substitution_cost("A", "B", 0.5)
# A→B costs 0.5
# B→A also costs 0.5
```

### Character Set
Custom costs are only meaningful for characters included in your sentences. Use `setup_characters()` to define the character set before calculating distances.

### Override Behavior
Custom costs override default costs for specific character pairs:
```python
calc = EditCostCalculator(default_substitution_cost=1.0)
calc.set_custom_substitution_cost("A", "B", 0.5)

calc.get_substitution_cost("A", "B")  # Returns 0.5 (custom)
calc.get_substitution_cost("A", "C")  # Returns 1.0 (default)
```

## Operations Explained

### Match
Characters are identical - no cost.

### Substitute
Replace one character with another. Cost depends on:
- Custom cost if defined for the pair
- Default substitution cost otherwise

### Insert
Add a character. Costs `default_insertion_cost`.

### Delete
Remove a character. Costs `default_deletion_cost`.

### Transpose
Swap two adjacent characters (Damerau extension). Cost depends on:
- Custom cost if defined for the pair
- Default transposition cost otherwise

## Output Format

### Print Result
```
'STRING1' → 'STRING2'
----------------
  Total Distance: 1.5000
  Number of Operations: 2
  Average Cost per Operation: 0.7500

  Operations:
    1. Substitute 'X' → 'L' (cost: 1.0000)
    2. Substitute 'G' → 'T' (cost: 0.5000)
```

### Print Batch Results
Includes:
- Individual pair results
- Summary statistics (average, min, max distances)
- Average cost per operation across all pairs

## Performance Considerations

- **Time Complexity**: O(m × n) where m, n are string lengths
- **Space Complexity**: O(m × n) for the DP table
- **Character Matrix Size**: O(k²) where k is the number of unique characters

## Tips

1. **Extract characters from your sentences**: Let the tool discover the character set automatically
   ```python
   all_chars = set()
   for sentence in sentences:
       all_chars.update(sentence)
   calc.setup_characters(list(all_chars))
   ```

2. **Use meaningful custom costs**: Base them on:
   - Phonetic similarity
   - Visual similarity (for OCR)
   - Keyboard proximity (for typos)
   - Common errors in your domain

3. **Verify symmetry**: Check that your distances work the same in both directions
   ```python
   dist_ab = calc.calculate_edit_distance("A", "B")
   dist_ba = calc.calculate_edit_distance("B", "A")
   assert dist_ab.total_distance == dist_ba.total_distance
   ```

4. **Use batch analysis for comparison**: When analyzing multiple strings, batch analysis provides statistics and easy comparison

## Excel File Formats

### Clases.xlsx (Sentences)
Load sentences and their frequencies from this file.

| Name     | Frequency |
| -------- | --------- |
| XDKT11T3 | 1         |
| XDKG11T3 | 1         |
| LDKT11T3 | 1         |

**Required columns:**
- `Name`: The sentence or sequence string
- `Frequency`: Integer or float indicating how often this sequence appears

### Custom_cost.xlsx (Substitution and Transposition Costs)
Define custom costs for character pair operations.

| Character1 | Character2 | Cost | Operation     |
| ---------- | ---------- | ---- | ------------- |
| A          | S          | 0.5  | substitution  |
| E          | I          | 0.3  | substitution  |
| T          | D          | 0.4  | transposition |

**Required columns:**
- `Character1`: First character
- `Character2`: Second character
- `Cost`: Cost value (float)

**Optional column:**
- `Operation`: Either "substitution" (default) or "transposition"

If the `Operation` column is omitted, all rows default to substitution costs.


## License MIT

This project is part of PhD research at DI3 - DOCTORADO EN INGENIERÍA INDUSTRIAL - Delegacion UNC Universidad Nacional de Cuyo, Argentina.

Copyright (c) 2026 Mauro A. Benetti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

If you use ISEC in academic research, please cite:

```bibtex
@software{isec2026,
  title={ISEC: Índice de Sensibilidad al Error Categórico},
  author={Mauro A. Benetti},
  year={2026},
  url={https://github.com/mbenetti/ISEC}
}
```