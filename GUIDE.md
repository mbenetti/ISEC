# Levenshtein-Damerau Distance Calculator with Custom Operation Costs

A Python implementation of the **Levenshtein-Damerau distance** algorithm with full support for **customizable operation costs** for character pairs. Perfect for spell checking, approximate string matching, and linguistic analysis.

## Features

✨ **Core Features:**
- **Levenshtein-Damerau distance calculation** (supports transposition)
- **Configurable default costs** for all operation types
- **Custom character pair costs** for substitution and transposition
- **Symmetric cost handling** (A→B cost = B→A cost)
- **Character matrices** showing all pairwise costs
- **Batch distance calculation** between multiple sentences
- **Detailed operation tracking** with cost breakdown

## Installation

```bash
# Install required dependencies
pip install numpy pandas openpyxl
```

Note: `openpyxl` is needed for reading Excel files. If you only use programmatic API, you can skip it.

## Quick Start

### Basic Usage

```python
from matriz_costo_caracteres import EditCostCalculator

# Create calculator
calc = EditCostCalculator(
    default_substitution_cost=1.0,
    default_insertion_cost=1.0,
    default_deletion_cost=1.0,
    default_transposition_cost=1.0,
)

# Define custom costs for similar character pairs
custom_costs = {
    ("A", "S"): 0.5,  # A and S substitution costs 0.5
    ("E", "I"): 0.5,  # E and I substitution costs 0.5
}

calc.set_custom_costs(custom_costs, operation="substitution")

# Setup from sentences
sentences = ["CASE", "SASE"]
all_chars = set()
for s in sentences:
    all_chars.update(s)
calc.setup_characters(list(all_chars))

# Calculate distance
result = calc.calculate_edit_distance("CASE", "SASE")
print(f"Distance: {result.total_distance}")
print(f"Operations: {len(result.operations)}")
print(f"Average cost: {result.average_cost}")
```

### Loading from Excel Files

The main script (`matriz_costo_caracteres.py`) automatically loads data from Excel files:

1. **Sentences** from `Clases.xlsx`
   - Column names: `Name`, `Frequency`
   - The frequency is loaded but optional for distance calculation

2. **Custom costs** from `Custom_cost.xlsx`
   - Column names: `Character1`, `Character2`, `Cost`
   - Optionally specify operation type with an `Operation` column

```python
from matriz_costo_caracteres import load_sentences_from_excel, load_custom_costs_from_excel

# Load sentences and frequencies
sentences, frequencies = load_sentences_from_excel("Clases.xlsx")

# Load custom costs for substitution and transposition
sub_costs, trans_costs = load_custom_costs_from_excel("Custom_cost.xlsx")

# Create and configure calculator
calc = EditCostCalculator()
calc.set_custom_costs(sub_costs, operation="substitution")
calc.set_custom_costs(trans_costs, operation="transposition")

# Setup and calculate
all_chars = set("".join(sentences))
calc.setup_characters(list(all_chars))
results = calc.calculate_all_distances(sentences)
```

Run the main script to process files automatically:
```bash
python matriz_costo_caracteres.py
```

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
