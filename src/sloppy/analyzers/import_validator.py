"""Import validation for detecting hallucinated packages."""

import importlib.util
from typing import Optional


def module_exists(module_name: str) -> bool:
    """Check if a module/package exists in the Python environment."""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ModuleNotFoundError, ValueError, ImportError):
        return False


def validate_import(module_name: str, name: str) -> Optional[str]:
    """
    Validate that an import is correct.
    
    Returns an error message if the import is invalid, None otherwise.
    """
    # Check if base module exists
    base_module = module_name.split('.')[0]
    if not module_exists(base_module):
        return f"Module '{module_name}' does not exist"
    
    # For now, just check the base module exists
    # More sophisticated checking could verify the specific name exists
    return None


# Common hallucinated imports (known bad patterns)
KNOWN_HALLUCINATIONS = {
    # Wrong module for import
    ('requests', 'JSONResponse'): "JSONResponse is from starlette/fastapi, not requests",
    ('flask', 'Query'): "Query is from fastapi, not flask", 
    ('django', 'FastAPI'): "FastAPI is its own package, not part of django",
    ('typing', 'Required'): "Required is from typing_extensions (Python <3.11)",
    ('collections', 'dataclass'): "dataclass is from dataclasses, not collections",
    ('json', 'JSONEncoder'): None,  # This one is actually valid
    
    # Non-existent methods/classes
    ('os', 'makedirectory'): "Use os.makedirs() not os.makedirectory()",
    ('pathlib', 'Path.mkdirs'): "Use Path.mkdir(parents=True) not Path.mkdirs()",
}


def check_known_hallucination(module: str, name: str) -> Optional[str]:
    """Check if this is a known hallucinated import pattern."""
    return KNOWN_HALLUCINATIONS.get((module, name))
