"""Configuration loading from pyproject.toml and .sloppyrc."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib
except ImportError:
    tomllib = None  # type: ignore


def load_config(start_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from pyproject.toml or .sloppyrc files."""
    if start_path is None:
        start_path = Path.cwd()
    
    config: Dict[str, Any] = {}
    
    # Try pyproject.toml first
    pyproject = find_file_upward(start_path, "pyproject.toml")
    if pyproject:
        config = load_pyproject_config(pyproject)
    
    # Override with .sloppyrc if present
    sloppyrc = find_file_upward(start_path, ".sloppyrc.json")
    if sloppyrc:
        config.update(load_json_config(sloppyrc))
    
    sloppyrc_toml = find_file_upward(start_path, ".sloppyrc.toml")
    if sloppyrc_toml:
        config.update(load_toml_config(sloppyrc_toml))
    
    return config


def find_file_upward(start: Path, filename: str) -> Optional[Path]:
    """Find a file by walking up the directory tree."""
    current = start.resolve()
    
    while current != current.parent:
        candidate = current / filename
        if candidate.exists():
            return candidate
        current = current.parent
    
    return None


def load_pyproject_config(path: Path) -> Dict[str, Any]:
    """Load [tool.sloppy] from pyproject.toml."""
    if tomllib is None:
        return {}
    
    try:
        content = path.read_text(encoding="utf-8")
        data = tomllib.loads(content)
        return data.get("tool", {}).get("sloppy", {})
    except Exception:
        return {}


def load_json_config(path: Path) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        content = path.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        return {}


def load_toml_config(path: Path) -> Dict[str, Any]:
    """Load configuration from a TOML file."""
    if tomllib is None:
        return {}
    
    try:
        content = path.read_text(encoding="utf-8")
        return tomllib.loads(content)
    except Exception:
        return {}
