"""Helper utility functions."""

import os
import sys
from typing import Any, Optional


def ensure_directory_exists(path: str) -> None:
    """Ensure that a directory exists, creating it if necessary.

    Args:
        path: Path to the directory
    """
    os.makedirs(path, exist_ok=True)


def get_project_root() -> str:
    """Get the root directory of the project.

    Returns:
        Path to the project root directory
    """
    # This assumes the utils module is in src/utils/
    current_file = os.path.abspath(__file__)
    src_dir = os.path.dirname(os.path.dirname(current_file))
    project_root = os.path.dirname(src_dir)
    return project_root


def safe_get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Safely get an environment variable.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Value of the environment variable or default
    """
    return os.getenv(key, default)


def print_debug_info(*args: Any, **kwargs: Any) -> None:
    """Print debug information if DEBUG environment variable is set.

    Args:
        *args: Arguments to print
        **kwargs: Keyword arguments for print function
    """
    if safe_get_env_var("DEBUG"):
        print("[DEBUG]", *args, **kwargs)
