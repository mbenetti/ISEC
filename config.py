"""
Configuration management for Levenshtein-Damerau Distance Calculator.
Loads default operation costs from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_float_env(key: str, default: float) -> float:
    """
    Get a float value from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if variable not found
        
    Returns:
        Float value from environment or default
    """
    try:
        value = os.getenv(key)
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        print(f"Warning: Invalid value for {key}, using default: {default}")
        return default


def get_string_env(key: str, default: str) -> str:
    """
    Get a string value from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if variable not found
        
    Returns:
        String value from environment or default
    """
    value = os.getenv(key)
    return value if value is not None else default


class Config:
    """Configuration class for operation costs."""
    
    # Default operation costs (loaded from .env)
    DEFAULT_SUBSTITUTION_COST = get_float_env("DEFAULT_SUBSTITUTION_COST", 1.0)
    DEFAULT_INSERTION_COST = get_float_env("DEFAULT_INSERTION_COST", 1.0)
    DEFAULT_DELETION_COST = get_float_env("DEFAULT_DELETION_COST", 1.0)
    DEFAULT_TRANSPOSITION_COST = get_float_env("DEFAULT_TRANSPOSITION_COST", 1.0)
    OPERATION_COST_FACTOR = get_float_env('OPERATION_COST_FACTOR', 0.1)
    
    # File paths (loaded from .env)
    SENTENCES_FILE = get_string_env("SENTENCES_FILE", "Clases.xlsx")
    CUSTOM_COSTS_FILE = get_string_env("CUSTOM_COSTS_FILE", "Custom_cost.xlsx")
    
    # Column names (loaded from .env)
    SENTENCES_NAME_COLUMN = get_string_env("SENTENCES_NAME_COLUMN", "Name")
    SENTENCES_FREQUENCY_COLUMN = get_string_env("SENTENCES_FREQUENCY_COLUMN", "Frequency")
    COSTS_CHAR1_COLUMN = get_string_env("COSTS_CHAR1_COLUMN", "Character1")
    COSTS_CHAR2_COLUMN = get_string_env("COSTS_CHAR2_COLUMN", "Character2")
    COSTS_COST_COLUMN = get_string_env("COSTS_COST_COLUMN", "Cost")
    COSTS_OPERATION_COLUMN = get_string_env("COSTS_OPERATION_COLUMN", None)
    
    # Ollama configuration (loaded from .env)
    OLLAMA_HOST = get_string_env("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL = get_string_env("OLLAMA_EMBEDDING_MODEL", "embeddinggemma")
    
    @classmethod
    def display(cls) -> None:
        """Display current configuration."""
        print("\n" + "=" * 60)
        print("Configuration")
        print("=" * 60)
        print(f"  Default Substitution Cost: {cls.DEFAULT_SUBSTITUTION_COST}")
        print(f"  Default Insertion Cost: {cls.DEFAULT_INSERTION_COST}")
        print(f"  Default Deletion Cost: {cls.DEFAULT_DELETION_COST}")
        print(f"  Default Transposition Cost: {cls.DEFAULT_TRANSPOSITION_COST}")
        print(f"\n  Sentences File: {cls.SENTENCES_FILE}")
        print(f"  Custom Costs File: {cls.CUSTOM_COSTS_FILE}")
        print("=" * 60 + "\n")
