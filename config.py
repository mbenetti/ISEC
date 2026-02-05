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


def get_bool_env(key: str, default: bool) -> bool:
    """
    Get a boolean value from environment variables.

    Args:
        key: Environment variable name
        default: Default value if variable not found

    Returns:
        Boolean value from environment or default
    """
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


class Config:
    """Configuration class for operation costs."""

    # Default operation costs (loaded from .env)
    DEFAULT_SUBSTITUTION_COST = get_float_env("DEFAULT_SUBSTITUTION_COST", 1.0)
    DEFAULT_INSERTION_COST = get_float_env("DEFAULT_INSERTION_COST", 1.0)
    DEFAULT_DELETION_COST = get_float_env("DEFAULT_DELETION_COST", 1.0)
    DEFAULT_TRANSPOSITION_COST = get_float_env("DEFAULT_TRANSPOSITION_COST", 1.0)
    COST_FACTOR_PENALIZATION = get_float_env("COST_FACTOR_PENALIZATION", 0.1)

    # File paths (loaded from .env)
    SENTENCES_FILE = get_string_env("SENTENCES_FILE", "Clases.xlsx")
    CUSTOM_COSTS_FILE = get_string_env("CUSTOM_COSTS_FILE", "Custom_cost.xlsx")

    # Column names (loaded from .env)
    SENTENCES_NAME_COLUMN = get_string_env("SENTENCES_NAME_COLUMN", "Name")
    SENTENCES_FREQUENCY_COLUMN = get_string_env(
        "SENTENCES_FREQUENCY_COLUMN", "Frequency"
    )
    SENTENCES_GROUP_COLUMN = get_string_env("SENTENCES_GROUP_COLUMN", "Group")
    SENTENCES_SUBGROUP_COLUMN = get_string_env("SENTENCES_SUBGROUP_COLUMN", "Subgroup")
    COSTS_CHAR1_COLUMN = get_string_env("COSTS_CHAR1_COLUMN", "Character1")
    COSTS_CHAR2_COLUMN = get_string_env("COSTS_CHAR2_COLUMN", "Character2")
    COSTS_COST_COLUMN = get_string_env("COSTS_COST_COLUMN", "Cost")
    COSTS_OPERATION_COLUMN = get_string_env("COSTS_OPERATION_COLUMN", None)

    # ISEC weight configuration (loaded from .env)
    ISEC_SEMANTIC_WEIGHT = get_float_env("ISEC_SEMANTIC_WEIGHT", 0.4)
    ISEC_TOP_K_MATCHES = int(get_float_env("ISEC_TOP_K_MATCHES", 10))
    ISEC_OUTPUT_FILE = get_string_env("ISEC_OUTPUT_FILE", "ISEC_Results.xlsx")

    # Frequency scaling configuration
    ISEC_FREQUENCY_LOG_BASE = get_float_env("ISEC_FREQUENCY_LOG_BASE", 10.0)
    ISEC_FREQUENCY_SCALING_ENABLED = get_bool_env(
        "ISEC_FREQUENCY_SCALING_ENABLED", False
    )

    # Ollama configuration (loaded from .env)
    OLLAMA_HOST = get_string_env("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL = get_string_env("OLLAMA_EMBEDDING_MODEL", "embeddinggemma")

    # Group exclusion settings
    SAME_GROUP_EXCLUSION = get_bool_env("SAME_GROUP_EXCLUSION", False)
    SAME_SUBGROUP_EXCLUSION = get_bool_env("SAME_SUBGROUP_EXCLUSION", False)

    # Capitalization handling (loaded from .env)
    IGNORE_CAPITALIZATION = get_bool_env("IGNORE_CAPITALIZATION", False)

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
        print(f"  Same Group Exclusion: {cls.SAME_GROUP_EXCLUSION}")
        print(f"  Same Subgroup Exclusion: {cls.SAME_SUBGROUP_EXCLUSION}")
        print(f"\n  Frequency Log Base: {cls.ISEC_FREQUENCY_LOG_BASE}")
        print(f"  Frequency Scaling Enabled: {cls.ISEC_FREQUENCY_SCALING_ENABLED}")
        print("=" * 60 + "\n")
