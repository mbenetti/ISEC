
import sys
import os
import pickle
import pandas as pd
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Distancia_Semantica import SemanticDistanceCalculator
from config import Config

CACHE_FILE = os.path.join(os.path.dirname(__file__), "embeddings_cache.pkl")

def load_sentences_from_file(file_path: str, name_col: str, freq_col: str) -> tuple[List[str], List[Dict]]:
    """Simple loader for demo purposes"""
    try:
        if not os.path.exists(file_path):
             print(f"Warning: File not found {file_path}")
             return [], []

        df = pd.read_excel(file_path)
        sentences = df[name_col].astype(str).tolist()
        frequencies = df[freq_col].astype(int).tolist() if freq_col in df.columns else [1] * len(sentences)
        
        metadata = [{"frequency": f, "source": os.path.basename(file_path)} for f in frequencies]
        return sentences, metadata
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return [], []

def main():
    print("Pre-calculating embeddings...")
    
    # Load data
    clases_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Clases.xlsx")
    sentences_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Sentences.xlsx")
    provincias_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "provincias_small.xlsx")
    
    s1, m1 = load_sentences_from_file(clases_file, "Name", "Frequency")
    s2, m2 = load_sentences_from_file(sentences_file, "Name", "Frequency")
    s3, m3 = load_sentences_from_file(provincias_file, "Name", "Frequency")
    
    all_sentences = s1 + s2 + s3
    all_metadata = m1 + m2 + m3
    
    print(f"Total sentences: {len(all_sentences)}")
    
    # Initialize calculator
    # ensure we use the model from config
    calc = SemanticDistanceCalculator()
    
    # Check cache first if exists to append (optional, but let's just overwrite for freshness)
    
    # Load and embed
    # This calls ollama
    try:
        calc.load_sentences(all_sentences, all_metadata)
    except Exception as e:
        print(f"Error during embedding: {e}")
        return

    # Extract the cache
    # SemanticDistanceCalculator has self.embeddings_cache = {text: embedding}
    cache = calc.embeddings_cache
    
    print(f"Saving {len(cache)} embeddings to {CACHE_FILE}")
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)
        
    print("Done.")

if __name__ == "__main__":
    main()
