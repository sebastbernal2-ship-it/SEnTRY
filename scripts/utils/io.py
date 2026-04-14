"""
Utility functions for JSON I/O and file operations.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def read_json(file_path: str) -> Dict[str, Any]:
    """Read JSON file, return empty dict if not found."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json(file_path: str, data: Dict[str, Any], indent: int = 2) -> None:
    """Write data as formatted JSON, creating parent dirs as needed."""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent, sort_keys=True, default=str)


def get_utc_now() -> str:
    """Return current time in ISO 8601 UTC format."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def read_json_file(file_path: str, default: Any = None) -> Any:
    """Read JSON file with fallback to default value."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def append_to_json_array(file_path: str, item: Dict[str, Any]) -> None:
    """Append item to JSON array file."""
    data = read_json_file(file_path, [])
    if not isinstance(data, list):
        data = []
    data.append(item)
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
