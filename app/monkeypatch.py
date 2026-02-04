
import os
import pickle
import sys

# Add parent directory to path to ensure we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Distancia_Semantica import SemanticDistanceCalculator

CACHE_FILE = os.path.join(os.path.dirname(__file__), "embeddings_cache.pkl")
loaded_cache = {}

if os.path.exists(CACHE_FILE):
    print(f"Loading embeddings cache from {CACHE_FILE}")
    with open(CACHE_FILE, "rb") as f:
        loaded_cache = pickle.load(f)
else:
    print("Warning: No embedding cache found. Run precalc.py first.")

# Original method
_original_get_embedding = SemanticDistanceCalculator.get_embedding

def cached_get_embedding(self, text: str) -> list[float]:
    if text in loaded_cache:
        # Normalize the embedding if necessary as stored embeddings might be raw
        # But Distancia_Semantica seems to use raw embeddings and normalize during calc
        return loaded_cache[text]
    
    # Fallback to original if not in cache (e.g. new sentence)
    # This might fail if Ollama is not actually running, but that's expected
    print(f"Cache miss for: {text}")
    return _original_get_embedding(self, text)

# Apply patch
SemanticDistanceCalculator.get_embedding = cached_get_embedding
print("Applied SemanticDistanceCalculator monkeypatch.")
