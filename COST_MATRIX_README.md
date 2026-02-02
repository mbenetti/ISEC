# ISEC - Levenshtein-Damerau Distance Calculator with Custom Operation Costs

This project implements a Levenshtein-Damerau edit distance calculator that supports custom costs for character pair substitutions and transpositions. Load sentences and custom costs from Excel files, and get detailed operation breakdowns with individual and average costs.

## Features

- **Levenshtein-Damerau Algorithm**: Full implementation with transposition support
- **Custom Operation Costs**: Configurable default costs for substitution, insertion, deletion, and transposition
- **Custom Character Pair Costs**: Define specific costs for character pair substitutions and transpositions
- **Penalized Distance Metric**: Calculate a regularized distance that combines average cost with total operation cost
- **Excel Integration**: Load sentences and custom costs from Excel files
- **Detailed Operation Tracking**: See individual operations, character pairs involved, and costs
- **Batch Analysis**: Calculate distances for all sentence pairs with statistics
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

COSTS_CHAR1_COLUMN=Character1
COSTS_CHAR2_COLUMN=Character2
COSTS_COST_COLUMN=Cost
COSTS_OPERATION_COLUMN=Operation
```

### Penalized Distance Metric

The calculator provides a **Penalized Distance** metric that combines two perspectives:

$$\text{penalized\_distance} = \text{average\_cost} + (k \times \text{total\_cost})$$

Where:
- `average_cost` = total_cost / number_of_operations (average per-operation cost)
- `k` = OPERATION_COST_FACTOR (default 0.1)
- `total_cost` = sum of all operation costs

**Example**: For distance between "XDKT11T3" and "XDKG11T3":
- Total Cost: 0.5 (1 substitution of cost 0.5)
- Num Operations: 1
- Average Cost: 0.5 / 1 = 0.5
- Penalized Distance: 0.5 + (0.1 × 0.5) = 0.55

This metric provides a regularized view that penalizes sequences requiring many operations.

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
2. Load sentences from `Clases.xlsx`
3. Load custom costs from `Custom_cost.xlsx`
4. Display substitution and transposition cost matrices
5. Calculate Levenshtein-Damerau distances for all sentence pairs
6. Show detailed operation breakdowns and statistics

## Excel File Formats

### Clases.xlsx (Sentences File)

The sentences file should have at least two columns:

| Name | Frequency |
|------|-----------|
| XDKT11T3 | 1 |
| XDKG11T3 | 1 |
| LDKT11T3 | 1 |

- **Name**: The sentence or string to analyze
- **Frequency**: How many times this sentence appears (used for statistics)

Column names are configurable via `.env` file (default: "Name" and "Frequency").

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
├── .env                           # Configuration file (externalized costs)
├── config.py                      # Configuration loader
├── matriz_costo_caracteres.py     # Main implementation
├── test_basic.py                  # Basic tests
├── Clases.xlsx                    # Sentences to analyze (optional)
├── Custom_cost.xlsx               # Custom character pair costs (optional)
└── .venv/                        # Virtual environment
```

## Dependencies

- **python-dotenv**: Load environment variables from `.env` file
- **numpy** (>=1.24.0): Numerical computing for matrix operations
- **pandas** (>=2.0.0): Data manipulation and cost matrix representation
- **openpyxl** (>=3.0.0): Read Excel files

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

```
FUNCTION main()
    Display configuration from .env
    Load sentences from Excel file
    
    Create EditCostCalculator with configured default costs
    Load custom costs from Excel file
    
    FOR each sentence pair (i, j) where i < j:
        result = calculate_edit_distance_ld(sentences[i], sentences[j])
        Display operation breakdown and metrics
    END FOR
END FUNCTION


CLASS EditCostCalculator
    
    FUNCTION __init__(default costs)
        Store all default operation costs
        Initialize empty custom cost dictionaries
        Initialize character list and matrices
    END FUNCTION
    
    FUNCTION setup_characters(characters)
        Store character set
        Create substitution cost matrix (all default costs)
        Create transposition cost matrix (all default costs)
    END FUNCTION
    
    FUNCTION set_custom_costs(costs, operation_type)
        IF operation_type == "substitution":
            FOR each (char1, char2): cost in costs:
                Store cost bidirectionally (symmetric)
                Update substitution matrix
        ELSE IF operation_type == "transposition":
            FOR each (char1, char2): cost in costs:
                Store cost bidirectionally (symmetric)
                Update transposition matrix
    END FUNCTION
    
    FUNCTION calculate_edit_distance_ld(str1, str2)
        len1 = length(str1)
        len2 = length(str2)
        
        // Initialize DP table
        H = dictionary
        da = defaultdict (last occurrence of each char)
        max_dist = len1 + len2
        
        // Base cases
        H[-1, -1] = max_dist
        FOR i = 0 to len1:
            H[i, -1] = max_dist
            H[i, 0] = i * DEFAULT_DELETION_COST
        FOR j = 0 to len2:
            H[-1, j] = max_dist
            H[0, j] = j * DEFAULT_INSERTION_COST
        
        // DP computation
        FOR i = 1 to len1:
            DB = 0
            FOR j = 1 to len2:
                k = da[str2[j-1]]
                l = DB
                
                IF str1[i-1] == str2[j-1]:
                    cost = 0
                    DB = j
                ELSE:
                    cost = 1
                    sub_cost = get_substitution_cost(str1[i-1], str2[j-1])
                    H[i, j] = min(
                        H[i-1, j] + DEFAULT_DELETION_COST,
                        H[i, j-1] + DEFAULT_INSERTION_COST,
                        H[i-1, j-1] + sub_cost
                    )
                
                // Check transposition
                IF k > 0 AND l > 0:
                    trans_cost = get_transposition_cost(str1[i-1], str2[j-1])
                    H[i, j] = min(
                        H[i, j],
                        H[k-1, l-1] + 
                        (i - k - 1) * DEFAULT_DELETION_COST +
                        trans_cost +
                        (j - l - 1) * DEFAULT_INSERTION_COST
                    )
                
                IF str1[i-1] == str2[j-1]:
                    H[i, j] = H[i-1, j-1]
            END FOR
            
            da[str1[i-1]] = i
        END FOR
        
        // Backtrack to find operations
        operations = backtrack_ld(str1, str2, H)
        total_distance = H[len1, len2]
        
        RETURN DistanceResult(
            str1, str2, total_distance, operations,
            operation_cost_factor=OPERATION_COST_FACTOR
        )
    END FUNCTION
    
    FUNCTION _backtrack_ld(str1, str2, H)
        operations = empty list
        i = length(str1)
        j = length(str2)
        
        WHILE i > 0 OR j > 0:
            IF i > 0 AND j > 0 AND str1[i-1] == str2[j-1]:
                Add match operation
                i = i - 1
                j = j - 1
            ELSE IF i > 0 AND j > 0 AND can_transpose:
                Add transposition operation
                i = i - 2
                j = j - 2
            ELSE IF i > 0 AND j > 0:
                Add substitution operation (cheaper path)
                i = i - 1
                j = j - 1
            ELSE IF i > 0:
                Add deletion operation
                i = i - 1
            ELSE IF j > 0:
                Add insertion operation
                j = j - 1
        END WHILE
        
        REVERSE operations (they were built backwards)
        RETURN operations
    END FUNCTION
    
    FUNCTION calculate_all_distances(sentences)
        results = empty list
        
        FOR i = 0 to len(sentences)-1:
            FOR j = i+1 to len(sentences)-1:
                result = calculate_edit_distance_ld(sentences[i], sentences[j])
                Add result to results
            END FOR
        END FOR
        
        RETURN results
    END FUNCTION
    
END CLASS


CLASS DistanceResult
    PROPERTIES:
        str1, str2: Strings compared
        total_distance: Sum of all operation costs
        operations: List of Operation objects
        operation_cost_factor: k value for penalized distance
    
    COMPUTED PROPERTIES:
        num_operations: Count of non-match operations
        average_cost: total_distance / num_operations
        penalized_distance: average_cost + (operation_cost_factor * total_distance)
END CLASS


CLASS Operation
    PROPERTIES:
        op_type: "match", "substitute", "insert", "delete", "transpose"
        from_char: Character from str1
        to_char: Character to str2
        cost: Cost of this operation
END CLASS
```

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