# ISEC Demo Application

A web-based demonstration environment for the **ISEC (Índice de Sensibilidad al Error Categórico)** metric, which measures the sensitivity of categorical data to classification errors using a combination of semantic and morphological distance.

## Overview

The ISEC Demo provides an interactive interface to:
- Calculate ISEC scores for sentence pairs
- View dataset overviews with ranked sentence pairs
- Explore semantic and morphological relationships
- Adjust calculation parameters in real-time

## Architecture

### Backend (FastAPI)

**File**: `main.py`

The backend provides RESTful API endpoints for:
- Configuration management
- Dataset (collection) switching
- ISEC calculation
- Dataset overview generation

### Core Calculation Engine

**File**: `ISEC.py`

Implements the ISEC calculation logic:
- `ISECCalculator`: Main calculator class
- `calculate_isec()`: Calculate ISEC for a single sentence
- `calculate_bulk_isec()`: Calculate ISEC for all sentences in a collection (returns sentence pairs)

**File**: `Distancia_Semantica.py`

Handles semantic distance calculations using:
- Ollama embeddings (embeddinggemma model)
- ChromaDB for vector storage
- Cosine similarity for distance measurement

**File**: `matriz_costo_caracteres.py`

Implements morphological distance using:
- Custom edit distance algorithm
- Character-level cost matrices
- Penalized distance calculation

### Frontend (Vue.js 3)

**File**: `static/index.html`

Single-page application with:
- Dataset and sentence selection
- Parameter controls (sliders)
- Dataset overview table (sentence pairs)
- Detailed ISEC results view
- Interactive UI with smooth transitions

## API Endpoints

### GET `/api/config`
Returns current configuration parameters.

**Response**:
```json
{
  "semantic_weight": 0.2,
  "cost_factor": 0.2,
  "substitution": 1.1,
  "insertion": 1.3,
  "deletion": 1.3,
  "transposition": 0.5,
  "top_k": 10
}
```

### GET `/api/collections`
Returns available datasets.

**Response**:
```json
[
  {"name": "Clases.xlsx", "count": 4},
  {"name": "Sentences.xlsx", "count": 10},
  {"name": "Tabla3.xlsx", "count": 4},
  {"name": "Provincias.xlsx", "count": 24}
]
```

### POST `/api/collection`
Switch to a different dataset.

**Request**:
```json
{
  "collection_name": "Provincias.xlsx"
}
```

### GET `/api/sentences`
Returns all sentences in the current collection.

**Response**:
```json
[
  {"sentence": "Buenos Aires", "frequency": 100},
  {"sentence": "CABA", "frequency": 50}
]
```

### POST `/api/calculate`
Calculate ISEC for a specific sentence.

**Request**:
```json
{
  "sentence": "Buenos Aires",
  "params": {
    "semantic_weight": 0.2,
    "cost_factor": 0.2,
    "substitution": 1.1,
    "insertion": 1.3,
    "deletion": 1.3,
    "transposition": 0.5,
    "top_k": 10
  },
  "override_frequency": 100
}
```

**Response**:
```json
{
  "sentence": "Buenos Aires",
  "frequency": 100,
  "group": "Provincias",
  "fmn": 5.61,
  "top_matches": [
    {
      "sentence": "BUENOS AIRES",
      "group": "Provincias",
      "semantic_distance": 0.023,
      "cost_distance": 2.5,
      "isec_score": 10.234
    }
  ]
}
```

### POST `/api/collection-overview`
Calculate ISEC scores for all sentences in the current collection, returning sentence pairs.

**Request**:
```json
{
  "k": 10,
  "params": { ... }
}
```

**Response**:
```json
[
  {
    "sentence": "Buenos Aires",
    "matched_sentence": "BUENOS AIRES",
    "frequency": 100,
    "group": "Provincias",
    "matched_group": "Provincias",
    "isec_score": 10.234
  },
  {
    "sentence": "CABA",
    "matched_sentence": "caba",
    "frequency": 50,
    "group": "Provincias",
    "matched_group": "Provincias",
    "isec_score": 8.567
  }
]
```

### POST `/api/pair-detail`
Get detailed transformation analysis for a specific sentence pair.

**Request**:
```json
{
  "sentence1": "Buenos Aires",
  "sentence2": "BUENOS AIRES",
  "params": { ... }
}
```

**Response**:
```json
{
  "sentence1": "Buenos Aires",
  "sentence2": "BUENOS AIRES",
  "isec_score": 10.234,
  "semantic_distance": 0.023,
  "cost_distance": {
    "total": 2.5,
    "average": 0.25,
    "penalized": 2.8
  },
  "operations": [
    {"type": "substitute", "from_char": "b", "to_char": "B", "cost": 1.0},
    {"type": "match", "from_char": "u", "to_char": "U", "cost": 0.0}
  ],
  "operation_counts": {"match": 8, "substitute": 2}
}
```

## Features

### 1. Dataset Overview

When a dataset is selected, the application automatically displays a ranked table of sentence pairs:

- **Sentence Pairs**: Each row shows:
  - Source sentence (clickable)
  - Best matching sentence (indented with ↳ symbol)
  - Both groups (source and matched)
  - Frequency of source sentence
  - ISEC score for the pair

- **Ranking**: Pairs are sorted by ISEC score (descending)
- **Calculation**: Uses k=10 for overview calculations

### 2. Detailed Analysis

Click any sentence in the overview to view:
- Top k semantic matches
- Semantic distance for each match
- Morphological (cost) distance for each match
- Individual ISEC scores for each match
- Frequency Median Normalized (FMN) value

### 3. Pair Detail Analysis

Clicking on any matched sentence in the results table opens a detailed analysis modal:
- **Transformations**: Complete list of edit operations (substitute, insert, delete, transpose)
- **Costs**: Individual operation costs and penalized distance breakdown
- **Metrics**: Detailed view of Semantic Distance, Cost Distance, and ISEC Score
- **Visualization**: Color-coded badges for operation types

### 4. Parameter Adjustment

Real-time parameter controls:
- **Semantic Weight**: Balance between semantic and morphological components
- **Penalization (k)**: Cost factor for edit distance
- **Operation Costs**: Substitution, insertion, deletion, transposition
- **Top Matches (k)**: Number of matches to display

### 5. Navigation

- **Back to Overview**: Button in detailed view returns to overview table
- **Dataset Switching**: Dropdown to change active dataset
- **Sentence Selection**: Dropdown or click in overview table

## Data Files

Located in `app/data/`:
- `Clases.xlsx`: Category classification examples
- `Sentences.xlsx`: Product description examples
- `Tabla3.xlsx`: Additional classification examples
- `Provincias.xlsx`: Argentine provinces dataset

Each file should have columns:
- `Nombre`: Sentence text
- `Frecuencia`: Frequency count
- `Grupo`: Group/category
- `Subgrupo`: Subcategory (optional)

## Configuration

Settings are defined in `config.py` (parent directory):
- Ollama host and model
- Default weights and costs
- Frequency scaling options
- Capitalization handling (`IGNORE_CAPITALIZATION`)
- Group exclusion settings

## Running the Application

```bash
# From the ISEC directory
source .venv/bin/activate
python app/main.py
```

Then open http://localhost:8000 in your browser.

## Key Concepts

### ISEC Score

The ISEC metric measures how sensitive a sentence is to categorical errors:

```
ISEC = FMN / (semantic_weight × SemanticDistance + morphologic_weight × CostDistance)
```

Where:
- **FMN**: Frequency Median Normalized (log-scaled frequency)
- **SemanticDistance**: Cosine distance between embeddings
- **CostDistance**: Penalized edit distance
- **Higher ISEC**: More sensitive to errors (important to classify correctly)

### Sentence Pairs

ISEC is calculated between **pairs** of sentences:
- Each sentence is paired with its best semantic match
- The ISEC score represents the relationship between the pair
- Overview table shows both sentences to illustrate the pairing

### Group Exclusion

When enabled, semantic matches exclude sentences from:
- Same group (if `SAME_GROUP_EXCLUSION=True`)
- Same subgroup (if `SAME_SUBGROUP_EXCLUSION=True`)

This ensures matches represent potential confusion between different categories.

## Technical Stack

- **Backend**: FastAPI, Python 3.10+
- **Frontend**: Vue.js 3, Vanilla CSS
- **Embeddings**: Ollama (embeddinggemma model)
- **Vector DB**: ChromaDB
- **Data**: Pandas, NumPy

## Performance Notes

- Embeddings are cached in `embeddings_cache.pkl`
- First load generates embeddings (may take time)
- Subsequent loads use cached embeddings
- Large datasets (1000+ sentences) may take several seconds for overview calculation
