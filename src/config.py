#!/usr/bin/env python3
"""
src/config.py — Robust Configuration Loader & External Dataset Resolver

Provides safe, deterministic configuration loading for the Beyond Synthetic
Missingness pipeline:
- Parses `--config <path>` from command-line arguments or function calls.
- Prioritizes: explicit path > CLI --config > BSM_CONFIG env > configs/local.yaml > configs/default.yaml.
- Safe path resolution using pathlib.Path (properly handling paths with spaces).
- Strict READ-ONLY validation for raw dataset locations.
- Validates the authentic structure of the Honda Smart-Meter dataset without touching files.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import yaml
except ImportError:
    yaml = None


def find_repo_root() -> Path:
    """
    Safely determines repository root directory without hardcoding machine-specific paths.
    """
    # Check parent of 'src' or 'control'
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "TASK_PLAN.md").is_file() and (parent / "control").is_dir():
            return parent
    return Path.cwd().resolve()


def parse_cli_config_arg(args: Optional[List[str]] = None) -> Optional[Path]:
    """
    Extracts --config argument from command line safely.
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", type=str, default=None, help="Path to YAML configuration file")
    known, _ = parser.parse_known_args(args)
    if known.config:
        return Path(known.config).expanduser()
    return None


def get_default_config_path(repo_root: Optional[Path] = None) -> Path:
    """
    Resolves default configuration path by priority:
    1. CLI --config flag
    2. Environment variable BSM_CONFIG
    3. configs/local.yaml (if exists)
    4. configs/default.yaml
    """
    root = repo_root or find_repo_root()

    cli_path = parse_cli_config_arg()
    if cli_path:
        return cli_path if cli_path.is_absolute() else (root / cli_path).resolve()

    env_path = os.environ.get("BSM_CONFIG")
    if env_path:
        p = Path(env_path).expanduser()
        return p if p.is_absolute() else (root / p).resolve()

    local_path = root / "configs" / "local.yaml"
    if local_path.is_file():
        return local_path.resolve()

    default_path = root / "configs" / "default.yaml"
    return default_path.resolve()


def load_config(
    config_path: Optional[Union[str, Path]] = None,
    repo_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Loads YAML configuration and resolves directory paths.
    
    Args:
        config_path: Explicit path to YAML file, or None to auto-resolve.
        repo_root: Base repository root for relative path resolution.
        
    Returns:
        Dictionary containing configuration values with resolved Path objects.
    """
    if yaml is None:
        raise RuntimeError("PyYAML is required to load configuration files. Please install pyyaml.")

    root = repo_root or find_repo_root()

    if config_path is not None:
        target_path = Path(config_path).expanduser()
        if not target_path.is_absolute():
            target_path = (root / target_path).resolve()
    else:
        target_path = get_default_config_path(root)

    if not target_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f) or {}

    if not isinstance(config_data, dict):
        raise ValueError(f"Configuration file at {target_path} must be a YAML mapping/dictionary.")

    # Record the loaded config file path
    config_data["_config_path"] = str(target_path)
    config_data["_repo_root"] = str(root)

    # Resolve data paths safely using pathlib.Path
    if "data" in config_data and isinstance(config_data["data"], dict):
        data_cfg = config_data["data"]
        for key in ["raw_dir", "interim_dir", "processed_dir"]:
            if key in data_cfg and data_cfg[key]:
                raw_val = str(data_cfg[key])
                p = Path(raw_val).expanduser()
                if not p.is_absolute():
                    p = (root / p).resolve()
                # Store resolved Path object (handles spaces cleanly)
                data_cfg[key] = p

    return config_data


def get_raw_data_dir(
    config: Optional[Dict[str, Any]] = None,
    config_path: Optional[Union[str, Path]] = None,
    validate_exists: bool = True
) -> Path:
    """
    Extracts and validates the raw data directory from config.
    Ensures safe, read-only accessibility.
    """
    if config is None:
        config = load_config(config_path)

    data_cfg = config.get("data", {})
    if not isinstance(data_cfg, dict) or "raw_dir" not in data_cfg:
        raise KeyError("Config is missing required field 'data.raw_dir'.")

    raw_path = data_cfg["raw_dir"]
    if not isinstance(raw_path, Path):
        raw_path = Path(str(raw_path)).expanduser()
        if not raw_path.is_absolute():
            root = Path(config.get("_repo_root", find_repo_root()))
            raw_path = (root / raw_path).resolve()

    if validate_exists:
        if not raw_path.exists():
            raise FileNotFoundError(
                f"Raw data directory does not exist: '{raw_path}'. "
                "Check configs/local.yaml or specify --config <path>."
            )
        if not raw_path.is_dir():
            raise NotADirectoryError(f"Raw data path is not a directory: '{raw_path}'")
        if not os.access(raw_path, os.R_OK):
            raise PermissionError(f"Raw data directory is not readable: '{raw_path}'")

    return raw_path


def validate_honda_dataset(raw_dir: Path) -> Dict[str, Any]:
    """
    Verifies that the target raw_dir contains authentic Honda Research Institute
    Smart-Meter dataset structure without modifying any files.
    
    Expected structure:
    - data/ subdirectory with meter folders (e.g. H2.Z311, H1.K11) containing .csv.gz files
    - issues/ subdirectory with automatic_issues/ and/or manual_issues/
    """
    if not raw_dir.is_dir():
        raise NotADirectoryError(f"Target path is not a directory: {raw_dir}")

    data_subdir = raw_dir / "data"
    issues_subdir = raw_dir / "issues"

    if not data_subdir.is_dir():
        raise FileNotFoundError(
            f"Expected 'data' subdirectory in Honda raw dataset at '{raw_dir}', but it was not found."
        )

    # Meter inspection (read-only iterdir)
    meter_dirs = [p for p in data_subdir.iterdir() if p.is_dir()]
    if not meter_dirs:
        raise ValueError(f"No meter subdirectories found under '{data_subdir}'.")

    # Sample meter file check
    sample_meter = meter_dirs[0]
    meter_files = [f.name for f in sample_meter.iterdir() if f.is_file()]
    has_gz_csv = any(f.endswith(".csv.gz") for f in meter_files)
    has_raw_readings = any("_raw.csv.gz" in f for f in meter_files)

    if not has_gz_csv or not has_raw_readings:
        raise ValueError(
            f"Sample meter directory '{sample_meter.name}' does not contain expected Honda raw gz files."
        )

    auto_issues_count = 0
    manual_issues_count = 0
    if issues_subdir.is_dir():
        auto_dir = issues_subdir / "automatic_issues"
        if auto_dir.is_dir():
            auto_issues_count = len(list(auto_dir.glob("*.yaml")))
        manual_dir = issues_subdir / "manual_issues"
        if manual_dir.is_dir():
            manual_issues_count = len(list(manual_dir.glob("*.yaml")))

    return {
        "is_valid_honda_dataset": True,
        "raw_dir": str(raw_dir),
        "meter_count": len(meter_dirs),
        "sample_meters": sorted([m.name for m in meter_dirs])[:5],
        "auto_issues_count": auto_issues_count,
        "manual_issues_count": manual_issues_count,
        "sample_meter_file_count": len(meter_files),
    }


def main():
    """CLI utility to test and inspect configuration resolution."""
    parser = argparse.ArgumentParser(description="Inspect pipeline configuration and validate dataset path.")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config")
    parser.add_argument("--validate", action="store_true", help="Validate Honda dataset structure")
    args = parser.parse_args()

    cfg = load_config(args.config)
    print("============================================================")
    print(" Beyond Synthetic Missingness — Config Inspection")
    print("============================================================")
    print(f"Loaded config from: {cfg.get('_config_path')}")
    print(f"Repository root:    {cfg.get('_repo_root')}")
    
    raw_dir = get_raw_data_dir(cfg, validate_exists=False)
    print(f"Raw data dir:       '{raw_dir}'")
    print(f"Exists:             {raw_dir.exists()}")
    if raw_dir.exists():
        print(f"Is dir:             {raw_dir.is_dir()}")
        print(f"Readable:           {os.access(raw_dir, os.R_OK)}")

    if args.validate or raw_dir.exists():
        try:
            val_info = validate_honda_dataset(raw_dir)
            print("\n[DATASET VALIDATION]")
            print(f"  Valid Honda Dataset: {val_info['is_valid_honda_dataset']}")
            print(f"  Total meters:        {val_info['meter_count']}")
            print(f"  Sample meters:       {val_info['sample_meters']}")
            print(f"  Issue files:         automatic={val_info['auto_issues_count']}, manual={val_info['manual_issues_count']}")
        except Exception as e:
            print(f"\n[VALIDATION ERROR] {e}")
            sys.exit(1)

    print("\nConfig resolution check: SUCCESS")


if __name__ == "__main__":
    main()
