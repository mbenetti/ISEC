
import sys
import os
import pandas as pd
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

COLLECTIONS = {
    "Short Categories": "Clases.xlsx",
    "Long Sentences": "Sentences.xlsx",
    "Provincias": "provincias_small.xlsx"
}

class CalculationRequest(BaseModel):
    sentence: str
    params: Dict[str, float]
    override_frequency: Optional[int] = None

class CollectionRequest(BaseModel):
    collection_name: str

class ConfigResponse(BaseModel):
    substitution: float
    insertion: float
    deletion: float
    transposition: float
    cost_factor: float
    semantic_weight: float
    top_k: int

def load_data():
    """Load and merge data from all files into global structures"""
    global all_sentences_data, all_chars
    
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    all_sentences_data = []
    
    for friendly_name, fname in COLLECTIONS.items():
        fpath = os.path.join(root_dir, fname)
        if os.path.exists(fpath):
            try:
                df = pd.read_excel(fpath)
                # Determine columns
                col_name = Config.SENTENCES_NAME_COLUMN if Config.SENTENCES_NAME_COLUMN in df.columns else df.columns[0]
                col_freq = Config.SENTENCES_FREQUENCY_COLUMN if Config.SENTENCES_FREQUENCY_COLUMN in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
                col_group = Config.SENTENCES_GROUP_COLUMN if Config.SENTENCES_GROUP_COLUMN in df.columns else None
                
                for _, row in df.iterrows():
                    name = str(row[col_name])
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
                    
                    all_sentences_data.append({
                        "sentence": name,
                        "frequency": freq,
                        "source": fname, # This is our filter key!
                        "group": group_val
                    })
            except Exception as e:
                print(f"Error loading {fname}: {e}")
                
    # Unique characters for cost matrix
    unique_chars = set()
    for d in all_sentences_data:
        unique_chars.update(d["sentence"])
    all_chars = sorted(list(unique_chars))
    print(f"Loaded {len(all_sentences_data)} total sentences and {len(all_chars)} unique characters.")

def init_global_calculator():
    """Initialize the calculator ONCE with ALL data."""
    global global_calculator
    
    print("Initializing global ISECCalculator...")
    # Initialize empty, we will load manually
    global_calculator = ISECCalculator()
    
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
    
    # Clearing logic handled inside load_sentences? No, normally it appends.
    # But since we run this once at startup, it's fine.
    # Note: `ISECCalculator` creates a new collection "isec_sentences"
    # We should probably force clear it once here to be safe across restarts?
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
    
    # Update calculator's working set (for list iteration, etc)
    global_calculator.sentences = [d["sentence"] for d in filtered_data]
    global_calculator.frequencies = {d["sentence"]: d["frequency"] for d in filtered_data}
    
    # Update the semantic filter!
    global_calculator.source_filter = source_filter
    
@app.on_event("startup")
async def startup_event():
    load_data()
    init_global_calculator()
    # Default to Short Categories
    set_active_collection(COLLECTIONS["Short Categories"])

@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """Get current configuration"""
    return {
        "substitution": global_calculator.cost_calculator.default_substitution_cost,
        "insertion": global_calculator.cost_calculator.default_insertion_cost,
        "deletion": global_calculator.cost_calculator.default_deletion_cost,
        "transposition": global_calculator.cost_calculator.default_transposition_cost,
        "cost_factor": Config.COST_FACTOR_PENALIZATION,
        "semantic_weight": global_calculator.semantic_weight,
        "top_k": Config.ISEC_TOP_K_MATCHES
    }

@app.get("/api/collections")
async def get_collections():
    return [{"name": k, "file": v} for k, v in COLLECTIONS.items()]

@app.post("/api/collection")
async def set_collection_endpoint(req: CollectionRequest):
    if req.collection_name not in COLLECTIONS:
        raise HTTPException(status_code=400, detail="Invalid collection")
    
    target_file = COLLECTIONS[req.collection_name]
    set_active_collection(target_file)
    return {"status": "ok", "active": req.collection_name}

@app.get("/api/sentences")
async def get_sentences():
    """Get list of sentences for current collection"""
    return [d for d in all_sentences_data if d["source"] == active_collection]

@app.post("/api/calculate")
async def calculate(req: CalculationRequest):
    """Calculate ISEC for a sentence with given params"""
    
    # Update params
    params = req.params
    
    # Update Semantic Weight
    if "semantic_weight" in params:
        global_calculator.semantic_weight = params["semantic_weight"]
        global_calculator.morphologic_weight = 1.0 - params["semantic_weight"]
        
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
        freq = global_calculator.frequencies.get(req.sentence, 1)
    
    # Run calculation
    # Only calculate for specific sentence
    # Note: `calculate_isec` calls `find_top_k_semantic_sentences`, which uses `self.source_filter`
    result = global_calculator.calculate_isec(req.sentence, freq)
    
    # Format output
    top_matches = []
    for rank, (matched_sent, sem_dist, cost_dist, isec_score, metadata) in enumerate(result.top_k_matches, 1):
         top_matches.append({
             "rank": rank,
             "sentence": matched_sent,
             "semantic_distance": sem_dist,
             "cost_distance": cost_dist,
             "isec_score": isec_score if isec_score != float('inf') else 0,
             "group": metadata.get("group", "N/A")
         })
         
    return {
        "sentence": req.sentence,
        "frequency": result.frequency,
        "fmn": result.frequency_median_normalized,
        "top_matches": top_matches
    }

# Serve static files (Frontend)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
