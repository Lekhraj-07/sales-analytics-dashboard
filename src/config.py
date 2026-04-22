"""Configuration loader."""
from pathlib import Path
from typing import Any, Dict
import yaml


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.yaml"


def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """Load YAML config file."""
    if not path.exists():
        raise FileNotFoundError(f"Config not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
