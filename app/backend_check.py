
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
import statistics
import math
from dataclasses import dataclass

# Import existing logic (assuming we can import them from parent dir if needed, 
# but for now I'll assume they are available or I'll mock the parts I can't reuse easily without modifying)
# The user said "use ISEC.py" and "Distancia_Semantica.py"
import sys
import os

# Ensure we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from matriz_costo_caracteres import EditCostCalculator
from Distancia_Semantica import SemanticDistanceCalculator, load_sentences_from_excel
from config import Config

# demo_backend.py
