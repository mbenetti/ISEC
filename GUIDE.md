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
- **Frequency Median Normalized** (FMN) calculation
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
ISEC_SEMANTIC_WEIGHT=0.4
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
    semantic_weight=0.4  # 40% semantic, 60% morphological
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

# 4. Test metadata filtering
python test_filtering.py

# 5. Test matched frequency functionality
python test_matched_frequency.py
```

## Excel Output Format

The ISEC calculator exports to Excel with the following columns:

| Column | Description |
|--------|-------------|
| `Sentence` | Source sentence |
| `Sentence_Group` | Group of source sentence |
| `Frequency` | Frequency of source sentence |
| `FMN` | Frequency Median Normalized |
| `Match_Rank` | Rank of this match (1 to k) |
| `Matched_Sentence` | The matched sentence |
| `Matched_Sentence_Group` | Group of matched sentence |
| `Matched_Frequency` | Frequency of matched sentence |
| `Semantic_Distance` | Semantic distance between the pair |
| `Cost_Distance` | Edit cost distance between the pair |
| `ISEC_Score` | ISEC score for this specific pair |

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

| Name | Frequency |
|------|-----------|
| XDKT11T3 | 1 |
| XDKG11T3 | 1 |
| LDKT11T3 | 1 |

**Required columns:**
- `Name`: The sentence or sequence string
- `Frequency`: Integer or float indicating how often this sequence appears

### Custom_cost.xlsx (Substitution and Transposition Costs)
Define custom costs for character pair operations.

| Character1 | Character2 | Cost | Operation |
|------------|-----------|------|-----------|
| A | S | 0.5 | substitution |
| E | I | 0.3 | substitution |
| T | D | 0.4 | transposition |

**Required columns:**
- `Character1`: First character
- `Character2`: Second character
- `Cost`: Cost value (float)

**Optional column:**
- `Operation`: Either "substitution" (default) or "transposition"

If the `Operation` column is omitted, all rows default to substitution costs.

## Files

- `matriz_costo_caracteres.py` - Main implementation
- `example_usage.py` - Comprehensive examples
- `test_basic.py` - Unit tests
- `GUIDE.md` - Full documentation
- `quickstart.py` - Quick start examples
- `Clases.xlsx` - Sample sentences file (edit with your data)
- `Custom_cost.xlsx` - Sample custom costs file (edit with your costs)

## License

This project is part of PhD research at ISEC.
