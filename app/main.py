
import sys
import os
import math
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 1. Apply monkeypatch first
import app.monkeypatch

# 2. Import core modules from LOCAL app package
# Add parent dir to path to find config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ISEC import ISECCalculator
from config import Config
from app.matriz_costo_caracteres import EditCostCalculator

app = FastAPI()

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global calculator state
global_calculator = None
all_sentences_data = [] # List of dicts {name, frequency, source, group}
all_chars = [] # List of all unique characters across all datasets
active_collection = None # Current source filename

# Dynamic directory for data files
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
collections_map = {} # {friendly_name: filename}

class CalculationRequest(BaseModel):
    sentence: str
    params: Dict[str, float]
    override_frequency: Optional[int] = None

class CollectionRequest(BaseModel):
    collection_name: str

class CollectionOverviewRequest(BaseModel):
    k: int = 10
    params: Dict[str, float]

class PairDetailRequest(BaseModel):
    sentence1: str
    sentence2: str
    params: Dict[str, float]

class ConfigResponse(BaseModel):
    substitution: float
    insertion: float
    deletion: float
    transposition: float
    cost_factor: float
    alpha: float
    top_k: int
    scaling_enabled: bool
    log_base: float

def load_data():
    """Load and merge data from all files in DATA_DIR into global structures"""
    global all_sentences_data, all_chars, collections_map
    
    import glob
    
    all_sentences_data = []
    collections_map = {}
    merged_data = {}
    
    if not os.path.exists(DATA_DIR):
        print(f"Warning: Data directory {DATA_DIR} not found.")
        return

    excel_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.xlsx")))
    
    for fpath in excel_files:
        fname = os.path.basename(fpath)
        # Use filename without extension as friendly name
        friendly_name = os.path.splitext(fname)[0].replace("_", " ").title()
        collections_map[friendly_name] = fname
        
        try:
            df = pd.read_excel(fpath)
            # Determine columns
            col_name = Config.SENTENCES_NAME_COLUMN if Config.SENTENCES_NAME_COLUMN in df.columns else df.columns[0]
            col_freq = Config.SENTENCES_FREQUENCY_COLUMN if Config.SENTENCES_FREQUENCY_COLUMN in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
            col_group = Config.SENTENCES_GROUP_COLUMN if Config.SENTENCES_GROUP_COLUMN in df.columns else None
            
            for _, row in df.iterrows():
                name = str(row[col_name]).strip()
                
                # Apply capitalization config
                if Config.IGNORE_CAPITALIZATION:
                    name = name.lower()
                
                freq = 1
                if col_freq:
                    try:
                        freq = int(row[col_freq])
                    except:
                        pass
                
                group_val = None
                if col_group:
                    val = row[col_group]
                    if pd.notna(val):
                        group_val = str(val)
                
                key = (fname, name)
                if key in merged_data:
                    merged_data[key]["frequency"] += freq
                else:
                    merged_data[key] = {
                        "sentence": name,
                        "frequency": freq,
                        "source": fname, 
                        "group": group_val
                    }
        except Exception as e:
            print(f"Error loading {fname}: {e}")
            
    # Convert merged data to list
    all_sentences_data = list(merged_data.values())
                
    # Unique characters for cost matrix
    unique_chars = set()
    for d in all_sentences_data:
        unique_chars.update(d["sentence"])
    all_chars = sorted(list(unique_chars))
    print(f"Loaded {len(all_sentences_data)} total sentences from {len(collections_map)} files and {len(all_chars)} unique characters.")

def init_global_calculator():
    """Initialize the calculator ONCE with ALL data."""
    global global_calculator
    
    print("Initializing global ISECCalculator...")
    # Initialize empty, we will load manually
    global_calculator = ISECCalculator(sentences_file=False)
    
    # 1. Setup Cost Calculator with ALL characters
    global_calculator.cost_calculator.setup_characters(all_chars)
    
    # 2. Setup Semantic Calculator with ALL sentences + Metadata
    sentences = [d["sentence"] for d in all_sentences_data]
    
    # Filter out None values from metadata for Chroma compatibility
    metadata = []
    for d in all_sentences_data:
        m = {
            "frequency": d["frequency"],
            "source": d["source"]
        }
        if d["group"] is not None:
            m["group"] = d["group"]
        metadata.append(m)
    
    # Clearing logic: ISECCalculator creates a new collection "isec_sentences"
    # We force clear it once here to be safe across restarts.
    try:
        global_calculator.semantic_calculator.chroma_client.delete_collection("isec_sentences")
    except:
        pass
        
    global_calculator.semantic_calculator.load_sentences(sentences, metadata)
    print("Global calculator initialized.")

def set_active_collection(source_filter: str):
    """Switch the active view/filter."""
    global active_collection, global_calculator
    
    active_collection = source_filter
    print(f"Switching active collection to: {source_filter}")
    
    # Filter valid sentences for UI and internal cost calculations
    filtered_data = [d for d in all_sentences_data if d["source"] == source_filter]
    
    # Update calculator's working set
    global_calculator.sentences = [d["sentence"] for d in filtered_data]
    global_calculator.frequencies = {d["sentence"]: d["frequency"] for d in filtered_data}
    global_calculator.max_frequency = max(global_calculator.frequencies.values()) if global_calculator.frequencies else 1
    
    # Store localized metadata for group exclusion and UI
    global_calculator.metadata_map = {
        d["sentence"]: {
            "frequency": d["frequency"],
            "group": d["group"]
        } for d in filtered_data
    }
    
    # Update the semantic filter
    global_calculator.source_filter = source_filter
    
@app.on_event("startup")
async def startup_event():
    load_data()
    init_global_calculator()
    
    # Default to first available collection if exists
    if collections_map:
        first_friendly = list(collections_map.keys())[0]
        # Prefer "Short Categories" or "Clases" if available
        for target in ["Short Categories", "Clases"]:
            if target in collections_map:
                first_friendly = target
                break
        set_active_collection(collections_map[first_friendly])

@app.get("/api/config", response_model= ConfigResponse)
async def get_config():
    """Get current configuration"""
    return {
        "substitution": global_calculator.cost_calculator.default_substitution_cost,
        "insertion": global_calculator.cost_calculator.default_insertion_cost,
        "deletion": global_calculator.cost_calculator.default_deletion_cost,
        "transposition": global_calculator.cost_calculator.default_transposition_cost,
        "cost_factor": Config.COST_FACTOR_PENALIZATION,
        "alpha": global_calculator.alpha,
        "top_k": Config.ISEC_TOP_K_MATCHES,
        "scaling_enabled": Config.ISEC_FREQUENCY_SCALING_ENABLED,
        "log_base": Config.ISEC_FREQUENCY_LOG_BASE
    }

@app.get("/api/collections")
async def get_collections():
    return [{"name": k, "file": v} for k, v in collections_map.items()]

@app.post("/api/collection")
async def set_collection_endpoint(req: CollectionRequest):
    if req.collection_name not in collections_map:
        raise HTTPException(status_code=400, detail="Invalid collection")
    
    target_file = collections_map[req.collection_name]
    set_active_collection(target_file)
    return {"status": "ok", "active": req.collection_name}

@app.get("/api/sentences")
async def get_sentences():
    """Get list of sentences for current collection"""
    return [d for d in all_sentences_data if d["source"] == active_collection]

@app.post("/api/collection-overview")
async def get_collection_overview(req: CollectionOverviewRequest):
    """Calculate ISEC for all sentences in current collection"""
    
    # Update params (same as calculate parameters)
    params = req.params
    if "alpha" in params:
        global_calculator.alpha = params["alpha"]
    elif "semantic_weight" in params: # Backward compatibility
        global_calculator.alpha = params["semantic_weight"]
    
    cc = global_calculator.cost_calculator
    changed = False
    
    if "substitution" in params and params["substitution"] != cc.default_substitution_cost:
        cc.default_substitution_cost = params["substitution"]
        changed = True
    if "insertion" in params and params["insertion"] != cc.default_insertion_cost:
        cc.default_insertion_cost = params["insertion"]
        changed = True
    if "deletion" in params and params["deletion"] != cc.default_deletion_cost:
        cc.default_deletion_cost = params["deletion"]
        changed = True
    if "transposition" in params and params["transposition"] != cc.default_transposition_cost:
        cc.default_transposition_cost = params["transposition"]
        changed = True
        
    if changed:
        cc.setup_characters(all_chars)
        
    if "cost_factor" in params:
        Config.COST_FACTOR_PENALIZATION = params["cost_factor"]

    results = global_calculator.calculate_bulk_isec(k=req.k)
    return results

@app.post("/api/calculate")
async def calculate(req: CalculationRequest):
    """Calculate ISEC for a sentence with given params"""
    
    # Standardize input if config is on
    sentence = req.sentence
    if Config.IGNORE_CAPITALIZATION:
        sentence = sentence.lower()
    
    # Update params
    params = req.params
    
    # Update Alpha
    if "alpha" in params:
        global_calculator.alpha = params["alpha"]
    elif "semantic_weight" in params:
        global_calculator.alpha = params["semantic_weight"]
        
    # Update Cost Calculator params
    cc = global_calculator.cost_calculator
    changed = False
    
    if "substitution" in params and params["substitution"] != cc.default_substitution_cost:
        cc.default_substitution_cost = params["substitution"]
        changed = True
    if "insertion" in params and params["insertion"] != cc.default_insertion_cost:
        cc.default_insertion_cost = params["insertion"]
        changed = True
    if "deletion" in params and params["deletion"] != cc.default_deletion_cost:
        cc.default_deletion_cost = params["deletion"]
        changed = True
    if "transposition" in params and params["transposition"] != cc.default_transposition_cost:
        cc.default_transposition_cost = params["transposition"]
        changed = True
        
    # Rebuild matrix if defaults changed (using global all_chars!)
    if changed:
        cc.setup_characters(all_chars)
        
    # Update Penalization Factor
    if "cost_factor" in params:
        Config.COST_FACTOR_PENALIZATION = params["cost_factor"]
        
    # Also Top K
    if "top_k" in params:
        Config.ISEC_TOP_K_MATCHES = int(params["top_k"])
        
    # Perform calculation
    # Use overridden frequency if provided, else use the logical default
    if req.override_frequency is not None:
        freq = req.override_frequency
    else:
        freq = global_calculator.frequencies.get(sentence, 1)
    
    # Run calculation
    # Only calculate for specific sentence
    # Note: `calculate_isec` calls `find_top_k_semantic_sentences`, which uses `self.source_filter`
    result = global_calculator.calculate_isec(sentence, freq)
    
    # Format output
    top_matches = []
    for rank, (matched_sent, sem_dist, cost_dist, isec_score, metadata, pair_numerator) in enumerate(result.top_k_matches, 1):
         top_matches.append({
             "rank": rank,
             "sentence": matched_sent,
             "semantic_distance": sem_dist,
             "cost_distance": cost_dist,
             "isec_score": isec_score if isec_score != float('inf') else 0,
             "pair_numerator": pair_numerator,
             "group": metadata.get("group", "N/A")
         })
         
    return {
        "sentence": req.sentence,
        "frequency": result.frequency,
        "median_frequency": result.median_frequency,
        "max_frequency": result.max_frequency,
        "raw_fmn": result.raw_fmn,
        "fmn": result.frequency_median_normalized, # Scaled Numerator for source
        "group": global_calculator.metadata_map.get(req.sentence, {}).get("group", "N/A"),
        "top_matches": top_matches
    }

@app.post("/api/pair-detail")
async def get_pair_detail(req: PairDetailRequest):
    """Get detailed transformation analysis for a specific sentence pair"""
    
    # Standardize input if config is on
    s1 = req.sentence1
    s2 = req.sentence2
    if Config.IGNORE_CAPITALIZATION:
        s1 = s1.lower()
        s2 = s2.lower()
    
    # Update params (same as calculate endpoint)
    params = req.params
    
    if "alpha" in params:
        global_calculator.alpha = params["alpha"]
    elif "semantic_weight" in params:
        global_calculator.alpha = params["semantic_weight"]
        
    cc = global_calculator.cost_calculator
    changed = False
    
    if "substitution" in params and params["substitution"] != cc.default_substitution_cost:
        cc.default_substitution_cost = params["substitution"]
        changed = True
    if "insertion" in params and params["insertion"] != cc.default_insertion_cost:
        cc.default_insertion_cost = params["insertion"]
        changed = True
    if "deletion" in params and params["deletion"] != cc.default_deletion_cost:
        cc.default_deletion_cost = params["deletion"]
        changed = True
    if "transposition" in params and params["transposition"] != cc.default_transposition_cost:
        cc.default_transposition_cost = params["transposition"]
        changed = True
        
    if changed:
        cc.setup_characters(all_chars)
        
    if "cost_factor" in params:
        Config.COST_FACTOR_PENALIZATION = params["cost_factor"]
    
    # Calculate edit distance with operations
    cost_result = global_calculator.cost_calculator.calculate_edit_distance(s1, s2)
    
    # Calculate semantic distance
    semantic_matches = global_calculator.semantic_calculator.find_top_k_semantic_matches(
        s1, k=1, exclude_same_group=False, exclude_same_subgroup=False
    )
    
    # Find the semantic distance for sentence2
    semantic_distance = 0.0
    found_match = False
    
    for sent, dist, _ in semantic_matches:
        if sent == s2:
            semantic_distance = dist
            found_match = True
            break
            
    # If not found in top matches, calculate directly specifically for this pair
    if not found_match:
        try:
            # We must use the same method as find_similar but for a specific pair
            # Calculate embedding only if needed (assuming cache handles it)
            result = global_calculator.semantic_calculator.calculate_semantic_distance(s1, s2)
            semantic_distance = result.normalized_distance
        except Exception as e:
            print(f"Error calculating direct distance: {e}")
            semantic_distance = 1.0 # Worst case fallback
    
    # Get frequencies
    freq1 = global_calculator.frequencies.get(s1, 1)
    freq2 = global_calculator.frequencies.get(s2, 1)
    
    # Calculate ISEC score for this individual pair using calculator logic if possible
    # For pair-detail, we re-run the core logic to get all values
    # Calculate pair-based numerator: 1 + log10(mean_freq_pair)
    log_f1 = math.log10(max(freq1, 1.0))
    pair_mean_freq = (freq1 + freq2) / 2.0
    log_pair = math.log10(max(pair_mean_freq, 1.0))
    
    fmn_ratio_self = log_f1
    fmn_ratio_pair = log_pair
    
    numerator_self = 1.0 + log_f1
    match_numerator = 1.0 + log_pair
    
    # Calculate ISEC score specifically for this pair (ds, dm)
    ds = max(semantic_distance, 1e-6)
    dm = max(cost_result.penalized_distance, 1e-6)
    denominator = pow(ds, global_calculator.alpha) * pow(dm, 1.0 - global_calculator.alpha)
    
    isec_score = match_numerator / denominator if denominator > 0 else float('inf')
    
    # Format operations
    operations = []
    for op in cost_result.operations:
        operations.append({
            "type": op.op_type,
            "from_char": op.from_char,
            "to_char": op.to_char,
            "cost": op.cost
        })
    
    # Count operations by type
    op_counts = {
        "match": sum(1 for op in cost_result.operations if op.op_type == "match"),
        "substitute": sum(1 for op in cost_result.operations if op.op_type == "substitute"),
        "insert": sum(1 for op in cost_result.operations if op.op_type == "insert"),
        "delete": sum(1 for op in cost_result.operations if op.op_type == "delete"),
        "transpose": sum(1 for op in cost_result.operations if op.op_type == "transpose")
    }
    
    return {
        "sentence1": s1,
        "sentence2": s2,
        "frequency1": freq1,
        "frequency2": freq2,
        "group1": global_calculator.metadata_map.get(req.sentence1, {}).get("group", "N/A"),
        "group2": global_calculator.metadata_map.get(req.sentence2, {}).get("group", "N/A"),
        "semantic_distance": semantic_distance,
        "cost_distance": {
            "total": cost_result.total_distance,
            "average": cost_result.average_cost,
            "sum_edit_costs": cost_result.sum_edit_costs,
            "penalized": cost_result.penalized_distance
        },
        "median_frequency": global_calculator.get_median_frequency(),
        "max_frequency": global_calculator.max_frequency,
        "raw_fmn": fmn_ratio_self, # For the source sentence
        "raw_fmn_pair": fmn_ratio_pair, # For the pair
        "fmn": numerator_self, # Scaled Numerator for source
        "fmn_pair": match_numerator, # Scaled Numerator for pair
        "fmn_config": {
            "log_base": 10,
            "scaling_enabled": True
        },
        "isec_score": isec_score if isec_score != float('inf') else 0,
        "operations": operations,
        "operation_counts": op_counts,
        "num_operations": cost_result.num_operations
    }
# Serve static files (Frontend)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
