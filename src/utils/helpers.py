"""Helper utility functions."""

import os
import sys
from typing import Any, Optional, Dict

from utils import logger


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

def extract_date(elm1: str, elm2: str) -> str:
    """ Take the two elements from the parsed row and extract the start date

    Args:
        element1: string with the month and date
        element2: string with year and start time
    Returns:
        string with the full date
    """

    parts = elm2.strip().split(" ")
    return elm1.strip() + ", " + parts[0]

def extract_time(elm1: str) -> str:
    """ Take the element from the parsed row and extract the start time

    Args:
        element1: string with year and start time
    Returns:
        string with the start time
    """

    parts = elm1.strip().split(" ")

    if parts[2] == "PM":
        time_parts = parts[1].split(":")
        time = str(int(time_parts[0]) + 12) + ":" + time_parts[1]
        return str(time)
    else:
        return parts[1]

def extract_cost(elm1: str) -> str:
    """ Take the element from the parsed row and extract the cost of the field

    Args:
        element1: string with cost in it somewhere
    Returns:
        string with the cost
    """

    parts = elm1.strip().split(" ")
    return parts[4]

def parse_spreadsheet_row(row_data: str, issued_date: str) -> Dict[str, Any]:
    """Take the spreadhseet line and parse it into columns

    Args:
        row_data: string from the pdf file

    Returns:
        dictionary of the values to add
    """

    elements = row_data.split(",")
    #logger.get_logger().debug(elements)
    
    parse_row = {}
    parse_row["day"] = elements[0].strip()
    parse_row["date"] = extract_date(elements[1], elements[2])
    parse_row["start"] = extract_time(elements[2])
    parse_row["end"] = extract_time(elements[4])
    parse_row["cost"] = extract_cost(elements[4])
    parse_row["issued-date"] = issued_date

    #logger.get_logger().debug(parse_row)

    return parse_row
    