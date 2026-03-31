# Semantic Distance Calculator

Measures semantic similarity between sentences using Ollama embeddings and Chroma vector database.

## Features

- **Ollama Embeddings**: Uses local `embeddinggemma` model for semantic embeddings
- **Chroma Vector DB**: Stores and queries embeddings efficiently
- **Similarity Metrics**: Calculates cosine similarity and distance
- **Metadata Support**: Supports frequency, group, and subgroup metadata for sentences
- **Metadata Filtering**: Exclude matches from same group or subgroup when finding closest sentences
- **Batch Analysis**: Calculates semantic distances for all sentence pairs

## Prerequisites

### 1. Install Ollama

[Download Ollama](https://ollama.ai) or install via homebrew:

```bash
brew install ollama
```

### 2. Pull the Embedding Model

```bash
ollama pull embeddinggemma
```

### 3. Start Ollama Service

```bash
ollama serve
```

This will start the Ollama service on `http://localhost:11434`

## Usage

### Run Semantic Distance Analysis

```bash
source .venv/bin/activate
python Distancia_Semantica.py
```

The script will:
1. Load sentences from `Clases.xlsx` (default file from config)
2. Generate embeddings using `embeddinggemma` model
3. Store embeddings in Chroma vector database
4. Calculate semantic distances for **all sentence pairs**
5. Display pairwise comparison results with similarity metrics
6. Find and display the **closest semantic match for each sentence** (excluding itself)

### Example Output

#### Pairwise Comparison:
```
'XDKT11T3' ↔ 'XDKG11T3'
--------------------------------------------------------------------------------
  Cosine Similarity: 0.9234
  Similarity Percentage: 96.17%
  Cosine Distance: 0.0766
  Distance Percentage: 3.83%
  Metadata (Sentence 1): {'frequency': 1, 'group': 'Group_A'}
  Metadata (Sentence 2): {'frequency': 2, 'group': 'Group_A'}
```

#### Closest Match for Each Sentence (No Filtering):
```
'XDKT11T3' ↔ 'XDKG11T3'
--------------------------------------------------------------------------------
  Cosine Similarity: 0.9234
  Similarity Percentage: 96.17%
  Cosine Distance: 0.0766
  Distance Percentage: 3.83%
  Metadata (Sentence 1): {'frequency': 1, 'group': 'Group_A'}
  Metadata (Sentence 2): {'frequency': 2, 'group': 'Group_A'}
```

#### Closest Match with Group Exclusion:
```
'XDKT11T3' ↔ 'LDKT11T3'
--------------------------------------------------------------------------------
  Cosine Similarity: 0.8912
  Similarity Percentage: 94.56%
  Cosine Distance: 0.1088
  Distance Percentage: 5.44%
  Metadata (Sentence 1): {'frequency': 1, 'group': 'Group_A'}
  Metadata (Sentence 2): {'frequency': 3, 'group': 'Group_B'}
```

## Semantic Distance Metrics

- **Cosine Similarity**: Range from -1 to 1 (1 = identical, 0 = orthogonal, -1 = opposite)
- **Similarity Percentage**: (cosine_similarity + 1) / 2 * 100 (0-100%)
- **Cosine Distance**: 1 - cosine_similarity (0 = identical, 2 = opposite)
- **Normalized Distance (0-1)**: (1 - cosine_similarity) / 2 (0 = identical, 1 = opposite)
- **Distance Percentage**: 100 - similarity_percentage (0-100%)

## Metadata and Filtering

The semantic distance calculator supports metadata filtering to exclude sentences from the same group or subgroup when finding closest matches. This is useful when you want to ensure that semantically similar sentences from different categories are matched.

### Configuration

Filtering behavior is controlled by environment variables in `.env` file:
- `SAME_GROUP_EXCLUSION=True/False`: Exclude matches from the same group
- `SAME_SUBGROUP_EXCLUSION=True/False`: Exclude matches from the same subgroup

### Excel File Format with Metadata

The sentences Excel file can include optional Group and Subgroup columns:

| Name | Frequency | Group | Subgroup |
|------|-----------|-------|----------|
| Sentence 1 | 1 | A | A1 |
| Sentence 2 | 1 | A | A2 |
| Sentence 3 | 1 | B | B1 |

### Using Metadata Filtering

When finding closest matches, you can exclude sentences from the same group or subgroup:

```python
# Exclude sentences from the same group
result = calculator.find_closest_sentence("Sentence 1", exclude_same_group=True)

# Exclude sentences from the same subgroup
result = calculator.find_closest_sentence("Sentence 1", exclude_same_subgroup=True)

# Exclude sentences from both same group and subgroup
result = calculator.find_closest_sentence("Sentence 1", exclude_same_group=True, exclude_same_subgroup=True)
```

### Automatic Filtering via Configuration

When using the calculator with ISEC or in batch mode, filtering is automatically applied based on `.env` configuration:

```python
# In main() function of Distancia_Semantica.py:
closest_results_filtered = calculator.find_closest_for_all(
    sentences, 
    exclude_same_group=Config.SAME_GROUP_EXCLUSION,
    exclude_same_subgroup=Config.SAME_SUBGROUP_EXCLUSION
)
```

### Filtering Behavior

1. **Group Exclusion**: When `exclude_same_group=True`, sentences with the same `group` value are excluded from matches
2. **Subgroup Exclusion**: When `exclude_same_subgroup=True`, sentences with the same `subgroup` value are excluded from matches
3. **Combined Exclusion**: Both filters can be applied simultaneously
4. **Missing Metadata**: If a sentence lacks group/subgroup metadata, it won't be excluded by that filter

## API

### SemanticDistanceCalculator

```python
calculator = SemanticDistanceCalculator(
    ollama_host="http://localhost:11434",
    embedding_model="embeddinggemma",
    collection_name="sentences"
)

# Load sentences and generate embeddings
# Metadata should include 'group' and/or 'subgroup' fields for filtering
calculator.load_sentences(sentences, metadata_list)

# Calculate distance between two sentences
result = calculator.calculate_semantic_distance(sent1, sent2)

# Calculate distances for all pairs
results = calculator.calculate_all_distances(sentences)

# Find closest match for a single sentence (excluding itself)
closest_result = calculator.find_closest_sentence(sentence)

# Find closest match for a single sentence (excluding same group)
closest_result = calculator.find_closest_sentence(sentence, exclude_same_group=True)

# Find closest match for a single sentence (excluding same subgroup)
closest_result = calculator.find_closest_sentence(sentence, exclude_same_subgroup=True)

# Find closest match for a single sentence (excluding both same group and subgroup)
closest_result = calculator.find_closest_sentence(sentence, exclude_same_group=True, exclude_same_subgroup=True)

# Find closest match for all sentences (excluding each from itself)
closest_results = calculator.find_closest_for_all(sentences)

# Find closest match for all sentences (excluding same group)
closest_results = calculator.find_closest_for_all(sentences, exclude_same_group=True)

# Find closest match for all sentences (excluding same subgroup)
closest_results = calculator.find_closest_for_all(sentences, exclude_same_subgroup=True)

# Find closest match for all sentences (excluding both same group and subgroup)
closest_results = calculator.find_closest_for_all(sentences, exclude_same_group=True, exclude_same_subgroup=True)

# Display results
calculator.print_result(result)  # Print single result
calculator.print_batch_results(results)  # Print all pairwise results
calculator.print_batch_results(closest_results)  # Print closest match results
```

### Methods

#### `find_closest_sentence(query_sentence, exclude_same_group=False, exclude_same_subgroup=False)`
Finds the closest semantic match for a single sentence in the collection.

**Args:**
- `query_sentence` (str): The sentence to find the closest match for
- `exclude_same_group` (bool): If True, exclude sentences from the same group (requires metadata with 'group' field)
- `exclude_same_subgroup` (bool): If True, exclude sentences from the same subgroup (requires metadata with 'subgroup' field)

**Returns:**
- `SemanticDistanceResult`: Result containing metrics and metadata for the closest match
- `None`: If no matches found (or only the query sentence exists, or all matches filtered out)

**Filtering Logic:**
1. Queries ChromaDB with a `where` clause to exclude documents with matching group/subgroup values
2. If no matches remain after filtering, returns `None`
3. If query sentence lacks group/subgroup metadata, that filter is not applied

**Example:**
```python
# Find closest match without filtering
result = calculator.find_closest_sentence("XDKT11T3")

# Find closest match excluding same group
result = calculator.find_closest_sentence("XDKT11T3", exclude_same_group=True)

# Find closest match excluding same subgroup
result = calculator.find_closest_sentence("XDKT11T3", exclude_same_subgroup=True)

# Find closest match excluding both same group and subgroup
result = calculator.find_closest_sentence("XDKT11T3", exclude_same_group=True, exclude_same_subgroup=True)

calculator.print_result(result)

# Example with configuration-based filtering
from config import Config
result = calculator.find_closest_sentence(
    "XDKT11T3", 
    exclude_same_group=Config.SAME_GROUP_EXCLUSION,
    exclude_same_subgroup=Config.SAME_SUBGROUP_EXCLUSION
)
```

#### `find_closest_for_all(sentences, exclude_same_group=False, exclude_same_subgroup=False)`
Finds the closest semantic match for each sentence in a list.

**Args:**
- `sentences` (List[str]): List of sentences to find closest matches for
- `exclude_same_group` (bool): If True, exclude sentences from the same group (requires metadata with 'group' field)
- `exclude_same_subgroup` (bool): If True, exclude sentences from the same subgroup (requires metadata with 'subgroup' field)

**Returns:**
- `List[SemanticDistanceResult]`: List of results for each sentence

**Note:** This method is used in the main function to demonstrate filtering when group metadata is available in the dataset.

**Returns:**
- `List[SemanticDistanceResult]`: Results for each sentence's closest match

**Example:**
```python
# Find closest matches without filtering
closest_results = calculator.find_closest_for_all(sentences)

# Find closest matches excluding same group
closest_results = calculator.find_closest_for_all(sentences, exclude_same_group=True)

# Find closest matches excluding same subgroup
closest_results = calculator.find_closest_for_all(sentences, exclude_same_subgroup=True)

# Find closest matches excluding both same group and subgroup
closest_results = calculator.find_closest_for_all(sentences, exclude_same_group=True, exclude_same_subgroup=True)

for result in closest_results:
    calculator.print_result(result)
```

#### `calculate_semantic_distance(str1, str2)`
Calculates semantic distance between two specific sentences.

**Args:**
- `str1` (str): First sentence
- `str2` (str): Second sentence

**Returns:**
- `SemanticDistanceResult`: Contains all metrics and metadata

#### `calculate_all_distances(sentences)`
Calculates semantic distances for all pairs of sentences.

**Args:**
- `sentences` (List[str]): List of sentences

**Returns:**
- `List[SemanticDistanceResult]`: Results for all pairs (excluding self-pairs)

### SemanticDistanceResult

Properties:
- `str1`, `str2`: The two sentences compared
- `cosine_similarity`: Similarity score (-1 to 1)
- `similarity_percentage`: Similarity as percentage (0-100%)
- `cosine_distance`: Distance score (0 to 2)
- `distance_percentage`: Distance as percentage (0-100%)
- `metadata1`, `metadata2`: Metadata for each sentence
- `embedding1`, `embedding2`: Raw embedding vectors

## Troubleshooting

### Connection Error: "Failed to connect to Ollama"

Make sure Ollama service is running:
```bash
ollama serve
```

In another terminal, verify the service:
```bash
curl http://localhost:11434/api/tags
```

### Model Not Found: "embeddinggemma"

Pull the model:
```bash
ollama pull embeddinggemma
```

Or use a different model:
```python
calculator = SemanticDistanceCalculator(
    embedding_model="nomic-embed-text"  # Alternative model
)
```

## Future Enhancements

- Custom similarity thresholds for clustering
- Export results to CSV
- Visualization of semantic similarity matrix
- Support for additional embedding models

## Algorithm Pseudocode

```
FUNCTION main()
    Load sentences and metadata from Excel file
    Create SemanticDistanceCalculator with Ollama and Chroma config
    
    FOR each sentence in sentences:
        embedding = call Ollama.embed(sentence, embedding_model)
        cache embedding and metadata
    
    Load all embeddings into Chroma vector database
    
    FOR each pair of sentences (i, j) where i < j:
        similarity = Chroma.query(embedding[i], find embedding[j])
        distance = 1 - similarity
        normalized_distance = (1 - similarity) / 2
        
        Create SemanticDistanceResult with metrics
        Display result with all metrics
    END FOR
END FUNCTION


CLASS SemanticDistanceCalculator
    
    FUNCTION __init__(ollama_host, embedding_model, collection_name)
        Initialize Ollama client
        Initialize Chroma client
        Create collection with cosine distance metric
    END FUNCTION
    
    FUNCTION get_embedding(text)
        IF text in cache:
            RETURN cached_embedding
        ELSE:
            embedding = Ollama.embed(text, embedding_model)
            cache(text, embedding)
            RETURN embedding
        END IF
    END FUNCTION
    
    FUNCTION load_sentences(sentences, metadata_list)
        FOR each (sentence, metadata) in zip(sentences, metadata_list):
            embedding = get_embedding(sentence)
            store in Chroma collection with metadata
            cache metadata
        END FOR
    END FUNCTION
    
    FUNCTION calculate_semantic_distance(str1, str2)
        embedding1 = get_embedding(str1)
        embedding2 = get_embedding(str2)
        
        // Query Chroma to find similarity
        results = Chroma.query(embedding1, include all embeddings)
        
        FOR each result:
            IF result.document == str2:
                cosine_distance = result.distance
                cosine_similarity = 1 - cosine_distance
                BREAK
            END IF
        END FOR
        
        IF not found:
            // Manual calculation
            normalize(embedding1, embedding2)
            cosine_similarity = dot_product(embedding1, embedding2)
            cosine_distance = 1 - cosine_similarity
        END IF
        
        RETURN SemanticDistanceResult(
            str1, str2,
            embedding1, embedding2,
            cosine_distance, cosine_similarity,
            metadata1, metadata2
        )
    END FUNCTION
    
    FUNCTION calculate_all_distances(sentences)
        results = empty list
        
        FOR i = 0 to len(sentences)-1:
            FOR j = i+1 to len(sentences)-1:
                result = calculate_semantic_distance(sentences[i], sentences[j])
                add result to results
            END FOR
        END FOR
        
        RETURN results
    END FUNCTION
    
    FUNCTION print_result(result)
        Display result.str1 ↔ result.str2
        Display cosine_similarity
        Display similarity_percentage
        Display cosine_distance
        Display normalized_distance (0-1 scale)
        Display distance_percentage
        Display metadata if available
    END FUNCTION
    
    FUNCTION print_batch_results(results)
        Display header
        FOR each result in results:
            print_result(result)
        END FOR
    END FUNCTION
    
END CLASS


CLASS SemanticDistanceResult
    PROPERTIES:
        str1, str2: Sentences compared
        embedding1, embedding2: Raw embedding vectors
        cosine_similarity: Range -1 to 1
        cosine_distance: 1 - cosine_similarity
        normalized_distance: (1 - cosine_similarity) / 2 [0-1 scale]
        similarity_percentage: (cosine_similarity + 1) / 2 * 100
        distance_percentage: 100 - similarity_percentage
        metadata1, metadata2: Metadata dicts
END CLASS
```

## Simplified Algorithm (Basic Functionality)

For quick reference or document inclusion, here is the simplified high-level pseudocode:

```
ALGORITHM: Semantic Distance with Ollama Embeddings and Chroma

INPUT:
    - sentences: List of text strings
    - metadata_list: Associated metadata (frequency, group, etc.)
    - embedding_model: Model name (e.g., "embeddinggemma")
    - ollama_host: URL to Ollama service

PROCESS:
    1. FOR each sentence in sentences:
           embedding = Ollama.embed(sentence, embedding_model)
           Store embedding in memory cache
           Add to Chroma collection with metadata
    
    2. FOR each pair of sentences (i, j) where i < j:
           embedding_i = get_cached_embedding(sentences[i])
           embedding_j = get_cached_embedding(sentences[j])
           
           // Calculate cosine similarity using Chroma
           similarity = Chroma.query(embedding_i, find embedding_j)
           distance = 1 - similarity
           
           // Normalize to 0-1 scale
           normalized_distance = (1 - similarity) / 2
           
           // Convert to percentages
           similarity_percentage = (similarity + 1) / 2 * 100
           distance_percentage = 100 - similarity_percentage
           
           Create SemanticDistanceResult with all metrics
           Display result
    
OUTPUT:
    - For each pair: similarity score, distance score
    - Normalized distance (0-1 scale)
    - Similarity and distance percentages
    - Associated metadata for each sentence
```
