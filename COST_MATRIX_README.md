# ISEC - Levenshtein-Damerau Distance Calculator with Custom Operation Costs and Metadata Filtering

This project implements a Levenshtein-Damerau edit distance calculator that supports custom costs for character pair substitutions and transpositions. Load sentences and custom costs from Excel files, and get detailed operation breakdowns with individual and average costs.

## Features

- **Levenshtein-Damerau Algorithm**: Full implementation with transposition support
- **Custom Operation Costs**: Configurable default costs for substitution, insertion, deletion, and transposition
- **Custom Character Pair Costs**: Define specific costs for character pair substitutions and transpositions
- **Penalized Distance Metric**: Calculate a regularized distance that combines average cost with total operation cost
- **Excel Integration**: Load sentences and custom costs from Excel files
- **Detailed Operation Tracking**: See individual operations, character pairs involved, and costs
- **Batch Analysis**: Calculate distances for all sentence pairs with statistics
- **Metadata Filtering**: Exclude comparisons within same group or subgroup when calculating distances
- **Configuration Management**: Externalized configuration via `.env` file for easy adjustments
- **Symmetric Cost Matrices**: Cost matrices respect symmetry (cost(A,B) = cost(B,A))

## Configuration

This project uses environment variables for configuration management. Settings are defined in the `.env` file and loaded automatically when the script runs.

### Default Configuration (.env)

```
DEFAULT_SUBSTITUTION_COST=1.0
DEFAULT_INSERTION_COST=1.0
DEFAULT_DELETION_COST=1.0
DEFAULT_TRANSPOSITION_COST=1.0

OPERATION_COST_FACTOR=0.1

SENTENCES_FILE=Clases.xlsx
CUSTOM_COSTS_FILE=Custom_cost.xlsx

SENTENCES_NAME_COLUMN=Name
SENTENCES_FREQUENCY_COLUMN=Frequency
SENTENCES_GROUP_COLUMN=Group
SENTENCES_SUBGROUP_COLUMN=Subgroup

COSTS_CHAR1_COLUMN=Character1
COSTS_CHAR2_COLUMN=Character2
COSTS_COST_COLUMN=Cost
COSTS_OPERATION_COLUMN=Operation

SAME_GROUP_EXCLUSION=False
SAME_SUBGROUP_EXCLUSION=False
```

### Penalized Distance Metric

The calculator provides a **Penalized Distance** metric that combines average cost with edit operation penalties:

$$\text{penalized-distance} = \text{average-cost} + (k \times \text{sum-edit-costs})$$

Where:
- `average_cost` = total_cost / number_of_operations (average per-operation cost)
- `k` = OPERATION_COST_FACTOR (default 0.1)
- `sum_edit_costs` = sum of insertion, deletion, and substitution operation costs (excluding transpositions)

**Example**: For distance between "XDKT11T3" and "XDKG11T3":
- Total Cost: 0.5 (1 substitution of cost 0.5)
- Num Operations: 1
- Average Cost: 0.5 / 1 = 0.5
- Sum Edit Costs: 0.5 (substitution cost)
- Penalized Distance: 0.5 + (0.1 × 0.5) = 0.55

**Example with insertions/deletions**: For "ABC" vs "AXBC":
- Total Cost: 1.0 (1 insertion of cost 1.0)
- Num Operations: 1
- Average Cost: 1.0 / 1 = 1.0
- Sum Edit Costs: 1.0 (insertion cost)
- Penalized Distance: 1.0 + (0.1 × 1.0) = 1.1

This metric penalizes all edit operations (insertions, deletions, and substitutions), useful for analyzing character-level transformations. Custom substitution costs from `Costo_Personalizado.xlsx` are included in the penalization.

### Modifying Costs

To change operation costs, edit the `.env` file. For example:
```
DEFAULT_SUBSTITUTION_COST=0.8
DEFAULT_INSERTION_COST=1.2
OPERATION_COST_FACTOR=0.15
```

Changes take effect immediately on the next script run.

## Installation with uv

This project uses [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver.

### Prerequisites

1. Install uv (if not already installed):
   ```bash
   # On macOS/Linux:
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows:
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Verify installation:
   ```bash
   uv --version
   ```

### Metadata Filtering

The calculator supports metadata-based filtering to exclude comparisons within the same group or subgroup. This is useful when you want to analyze distances only between sentences from different categories.

#### Filtering Configuration

Set these in your `.env` file:
- `SAME_GROUP_EXCLUSION=True/False`: When True, excludes comparisons between sentences in the same group
- `SAME_SUBGROUP_EXCLUSION=True/False`: When True, excludes comparisons between sentences in the same subgroup

#### Filtering Methods

```python
# Calculate distances with group exclusion
results_no_same_group = calculator.calculate_distances_with_filtering(
    sentences,
    metadata_list,
    exclude_same_group=True,
    exclude_same_subgroup=False,
)

# Calculate distances with subgroup exclusion
results_no_same_subgroup = calculator.calculate_distances_with_filtering(
    sentences,
    metadata_list,
    exclude_same_group=False,
    exclude_same_subgroup=True,
)

# Calculate distances with both group and subgroup exclusion
results_no_same_group_subgroup = calculator.calculate_distances_with_filtering(
    sentences,
    metadata_list,
    exclude_same_group=True,
    exclude_same_subgroup=True,
)
```

#### Example Output with Filtering

```
Metadata Filtering Demonstration
================================================================================

Metadata available:
  - Group data: YES
  - Same Group Exclusion (from config): True
  - Subgroup data: YES
  - Same Subgroup Exclusion (from config): False

Calculating distances with metadata filtering...

1. All comparisons (no filtering):
   Total comparisons: 6

2. Comparisons excluding same group:
   Total comparisons: 4
   Excluded comparisons: 2

3. Comparisons excluding same subgroup:
   Total comparisons: 5
   Excluded comparisons: 1

4. Comparisons excluding same group AND same subgroup:
   Total comparisons: 3
   Excluded comparisons: 3
```

### Quick Setup

1. **Create a virtual environment with uv:**
   ```bash
   uv venv
   ```

2. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

3. **Install dependencies:**
   ```bash
   uv pip install python-dotenv numpy pandas openpyxl
   ```

## Usage

### Running the Calculator

```bash
# Activate the environment
source .venv/bin/activate

# Run the calculator
python matriz_costo_caracteres.py
```

The script will:
1. Display the current configuration from `.env`
2. Load sentences and metadata (group, subgroup) from `Clases.xlsx`
3. Load custom costs from `Custom_cost.xlsx`
4. Display substitution and transposition cost matrices
5. Calculate Levenshtein-Damerau distances for all sentence pairs
6. Show detailed operation breakdowns and statistics
7. Demonstrate metadata filtering functionality when group/subgroup data is available

## Excel File Formats

### Clases.xlsx (Sentences File)

The sentences file should have at least two columns, with optional group and subgroup columns for metadata filtering:

| Name | Frequency | Group | Subgroup |
|------|-----------|-------|----------|
| XDKT11T3 | 1 | A | A1 |
| XDKG11T3 | 1 | A | A2 |
| LDKT11T3 | 1 | B | B1 |

- **Name**: The sentence or string to analyze
- **Frequency**: How many times this sentence appears (used for statistics and ISEC calculations)
- **Group**: Optional group identifier for filtering (used with `exclude_same_group` parameter)
- **Subgroup**: Optional subgroup identifier for filtering (used with `exclude_same_subgroup` parameter)

**Note on Metadata Filtering:**
- When `SAME_GROUP_EXCLUSION=True` in `.env`, comparisons between sentences with the same `Group` value are excluded
- When `SAME_SUBGROUP_EXCLUSION=True` in `.env`, comparisons between sentences with the same `Subgroup` value are excluded
- Both filters can be applied simultaneously
- If a sentence lacks group/subgroup metadata, it won't be excluded by that filter

Column names are configurable via `.env` file (default: "Name", "Frequency", "Group", "Subgroup").

### Custom_cost.xlsx (Custom Costs File)

The custom costs file should have three or four columns:

| Character1 | Character2 | Cost | Operation |
|-----------|-----------|------|-----------|
| D | X | 0.5 | substitution |
| G | T | 0.5 | substitution |
| K | L | 0.5 | substitution |

- **Character1**: First character in the pair
- **Character2**: Second character in the pair
- **Cost**: The custom cost for this operation (0.5 is cheaper than default 1.0)
- **Operation**: Type of operation - "substitution" or "transposition" (optional, defaults to substitution)

Column names are configurable via `.env` file (see Configuration section).

## Project Structure

```
ISEC/
├── pyproject.toml                  # Project configuration
├── README.md                       # This file
├── .env                           # Configuration file (externalized costs and filtering)
├── config.py                      # Configuration loader
├── matriz_costo_caracteres.py     # Main implementation with metadata filtering
├── test_basic.py                  # Basic tests
├── test_filtering.py              # Metadata filtering tests
├── test_matched_frequency.py      # Frequency display tests
├── Clases.xlsx                    # Sentences to analyze (optional)
├── Custom_cost.xlsx               # Custom character pair costs (optional)
└── .venv/                        # Virtual environment
```

## Dependencies

- **python-dotenv**: Load environment variables from `.env` file
- **numpy** (>=1.24.0): Numerical computing for matrix operations
- **pandas** (>=2.0.0): Data manipulation and cost matrix representation
- **openpyxl** (>=3.0.0): Read Excel files

## Related Documentation

- [ISEC_README.md](ISEC_README.md) - Complete ISEC calculator documentation with per-pair calculations
- [SEMANTIC_DISTANCE_README.md](SEMANTIC_DISTANCE_README.md) - Semantic distance calculator with metadata filtering
- [GUIDE.md](GUIDE.md) - Comprehensive user guide

## Testing Metadata Filtering

Test scripts are available to verify metadata filtering functionality:
```bash
# Test basic filtering functionality
python test_filtering.py

# Test matched frequency display
python test_matched_frequency.py

# Test parameter sensitivity with filtering
python test_parameter_sensitivity.py
```

### Development Dependencies

- **pytest**: Testing framework
- **black**: Code formatting
- **isort**: Import sorting

## API Reference

### EditCostCalculator Class

Main class for calculating Levenshtein-Damerau distances with custom costs.

```python
class EditCostCalculator:
    def __init__(self, default_substitution_cost=1.0, 
                 default_insertion_cost=1.0,
                 default_deletion_cost=1.0,
                 default_transposition_cost=1.0)
    
    def setup_characters(self, characters: List[str])
    def set_custom_costs(self, costs: Dict[Tuple[str, str], float], 
                        operation: str = "substitution")
    def calculate_edit_distance_ld(self, str1: str, str2: str) -> DistanceResult
    def calculate_all_distances(self, sentences: List[str]) -> List[DistanceResult]
    def display_matrix(self, title: str = "Cost Matrix")
    def display_transposition_matrix(self, title: str = "Transposition Cost Matrix")
    def show_custom_costs()
    def print_batch_results(self, results: List[DistanceResult])
```

### Data Classes

#### Operation
Represents a single edit operation:
```python
@dataclass
class Operation:
    type: str  # "match", "substitution", "insertion", "deletion", "transposition"
    char1: str
    char2: str
    cost: float
    position: int
```

#### DistanceResult
Result of distance calculation:
```python
@dataclass
class DistanceResult:
    str1: str
    str2: str
    distance: float
    operations: List[Operation]
    total_cost: float
    num_operations: int
    average_cost_per_operation: float
```

### Utility Functions

```python
def load_sentences_from_excel(filename: str, 
                             name_column: str = "Name",
                             frequency_column: str = "Frequency") 
    -> Tuple[List[str], Dict[str, int]]
    # Load sentences and frequencies from Excel file

def load_custom_costs_from_excel(filename: str,
                                char1_column: str = "Character1",
                                char2_column: str = "Character2",
                                cost_column: str = "Cost",
                                operation_column: str = "Operation")
    -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], float]]
    # Load custom substitution and transposition costs from Excel file
```

## Algorithm Pseudocode

### Detailed Algorithm: Levenshtein-Damerau Distance with Custom Costs

```latex
\begin{algorithm}
\caption{Levenshtein-Damerau Distance with Custom Operation Costs}
\begin{algorithmic}[1]
\Require{strings $s_1, s_2$; cost matrices $C_{sub}, C_{trans}$; default costs $c_{del}, c_{ins}, c_{sub}, c_{trans}$}
\Ensure{distance $d$ and list of operations $\text{ops}$}

\State $m \gets \text{length}(s_1)$
\State $n \gets \text{length}(s_2)$
\State $\text{max\_dist} \gets m + n$

\State Initialize dictionary $H$ with $H[-1,-1] \gets \text{max\_dist}$
\State Initialize dictionary $\text{da}$ (character last occurrence)

\Comment{Base case initialization}
\For{$i \gets 0$ to $m$}
    \State $H[i, -1] \gets \text{max\_dist}$
    \State $H[i, 0] \gets i \cdot c_{del}$
\EndFor

\For{$j \gets 0$ to $n$}
    \State $H[-1, j] \gets \text{max\_dist}$
    \State $H[0, j] \gets j \cdot c_{ins}$
\EndFor

\Comment{Dynamic programming computation}
\For{$i \gets 1$ to $m$}
    \State $DB \gets 0$
    \For{$j \gets 1$ to $n$}
        \State $k \gets \text{da}[s_2[j-1]]$
        \State $l \gets DB$
        
        \If{$s_1[i-1] = s_2[j-1]$}
            \State $DB \gets j$
            \State $H[i, j] \gets H[i-1, j-1]$
        \Else
            \State $c_{s} \gets C_{sub}[s_1[i-1], s_2[j-1]]$
            \State $H[i, j] \gets \min \begin{cases}
                H[i-1, j] + c_{del} & \text{(deletion)} \\
                H[i, j-1] + c_{ins} & \text{(insertion)} \\
                H[i-1, j-1] + c_s & \text{(substitution)}
            \end{cases}$
        \EndIf
        
        \Comment{Check transposition}
        \If{$k > 0 \land l > 0$}
            \State $c_t \gets C_{trans}[s_1[i-1], s_2[j-1]]$
            \State $\text{trans\_cost} \gets H[k-1, l-1] + (i - k - 1) \cdot c_{del} + c_t + (j - l - 1) \cdot c_{ins}$
            \State $H[i, j] \gets \min(H[i, j], \text{trans\_cost})$
        \EndIf
    \EndFor
    \State $\text{da}[s_1[i-1]] \gets i$
\EndFor

\State $\text{ops} \gets \text{Backtrack}(s_1, s_2, H)$
\State $d \gets H[m, n]$

\Return $(\text{ops}, d)$
\end{algorithmic}
\end{algorithm}
```

### Backtracking: Operation Reconstruction

```latex
\begin{algorithm}
\caption{Backtracking to Find Operations}
\begin{algorithmic}[1]
\Require{strings $s_1, s_2$; DP table $H$}
\Ensure{list of operations $\text{ops}$}

\State $i \gets \text{length}(s_1)$
\State $j \gets \text{length}(s_2)$
\State $\text{ops} \gets \emptyset$

\While{$i > 0 \lor j > 0$}
    \If{$i > 0 \land j > 0 \land s_1[i-1] = s_2[j-1]$}
        \State Append MATCH$(s_1[i-1])$ to $\text{ops}$
        \State $i \gets i - 1$; $j \gets j - 1$
    \ElsIf{$i > 1 \land j > 1 \land \text{CanTranspose}(s_1, s_2, i, j)$}
        \State $c_t \gets C_{trans}[s_1[i-1], s_2[j-1]]$
        \State Append TRANSPOSE$(s_1[i-1], s_2[j-1], c_t)$ to $\text{ops}$
        \State $i \gets i - 2$; $j \gets j - 2$
    \Else
        \State Find minimum of $\{H[i-1,j], H[i,j-1], H[i-1,j-1]\}$
        \If{minimum is $H[i-1,j]$}
            \State Append DELETE$(s_1[i-1])$ to $\text{ops}$
            \State $i \gets i - 1$
        \ElsIf{minimum is $H[i,j-1]$}
            \State Append INSERT$(s_2[j-1])$ to $\text{ops}$
            \State $j \gets j - 1$
        \Else
            \State $c_s \gets C_{sub}[s_1[i-1], s_2[j-1]]$
            \State Append SUBSTITUTE$(s_1[i-1], s_2[j-1], c_s)$ to $\text{ops}$
            \State $i \gets i - 1$; $j \gets j - 1$
        \EndIf
    \EndIf
\EndWhile

\State Reverse $\text{ops}$
\Return $\text{ops}$
\end{algorithmic}
\end{algorithm}
```

### Data Structures

**DistanceResult** class:
- $\text{str1}, \text{str2}$: Input strings
- $\text{operations}$: List of Operation objects
- $\text{total\_distance}$: Sum of all operation costs
- $\text{operation\_cost\_factor}$: $k$ value for penalized distance

**Operation** class:
- $\text{op\_type}$: Type of operation (match, insert, delete, substitute, transpose)
- $\text{from\_char}$: Character from $s_1$
- $\text{to\_char}$: Character to $s_2$
- $\text{cost}$: Cost of this operation

## Simplified Algorithm (Basic Functionality)

For quick reference or document inclusion, here is the simplified high-level pseudocode:

```
ALGORITHM: Levenshtein-Damerau Distance with Custom Costs

INPUT:
    - str1, str2: Two strings to compare
    - substitution_costs: Custom costs for character substitutions
    - transposition_costs: Custom costs for character transpositions
    - default_substitution_cost
    - default_insertion_cost
    - default_deletion_cost
    - default_transposition_cost

PROCESS:
    1. Initialize DP table H with base cases
    
    2. FOR each position i in str1:
           FOR each position j in str2:
               IF str1[i] == str2[j]:
                   H[i,j] = H[i-1,j-1]  // Match (no cost)
               ELSE:
                   // Consider three operations:
                   sub_cost = get_cost(str1[i], str2[j], "substitution")
                   H[i,j] = min(
                       H[i-1,j] + deletion_cost,      // Delete str1[i]
                       H[i,j-1] + insertion_cost,     // Insert str2[j]
                       H[i-1,j-1] + sub_cost          // Substitute
                   )
                   
                   // Also consider transposition if applicable
                   IF can_transpose(str1, str2, i, j):
                       trans_cost = get_cost(str1[i], str2[j], "transposition")
                       H[i,j] = min(H[i,j], transposition_cost)
    
    3. Backtrack from H[len(str1), len(str2)] to find operations
    
    4. Calculate metrics:
        total_distance = H[len(str1), len(str2)]
        num_operations = count of non-match operations
        average_cost = total_distance / num_operations
        penalized_distance = average_cost + (k × total_distance)

OUTPUT:
    - List of operations with individual costs
    - Total distance
    - Average cost per operation
    - Penalized distance metric
```

## License

MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request
