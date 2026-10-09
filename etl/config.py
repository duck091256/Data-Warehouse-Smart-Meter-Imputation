"""
etl/config.py — Configuration accessor for ETL modules.
Re-exports core config functions from src.config.
"""

from src.config import (
    load_config,
    get_raw_data_dir,
    validate_honda_dataset,
    find_repo_root,
)

__all__ = [
    "load_config",
    "get_raw_data_dir",
    "validate_honda_dataset",
    "find_repo_root",
]
