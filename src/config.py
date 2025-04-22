import os
import json
from typing import Optional, Dict, List, Any

from dotenv import load_dotenv


def load_api_token() -> Optional[str]:
    """Loads the Readwise API token from environment variables.

    Returns:
        The API token if found, otherwise None.
    """
    load_dotenv()  # Load variables from .env file
    return os.getenv("READWISE_API_TOKEN")


def load_filters_from_json(file_path: str) -> Dict[str, List[str]]:
    """Loads filter criteria from a JSON file.

    Args:
        file_path: The path to the JSON file containing filters.

    Returns:
        A dictionary containing filter lists for 'title_contains',
        'summary_contains', and 'url_contains'. Returns empty lists
        if the file is not found or contains invalid JSON.
    """
    default_filters: Dict[str, List[str]] = {
        "title_contains": [],
        "summary_contains": [],
        "url_contains": [],
    }
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            loaded_filters = json.load(f)
            # Basic validation - ensure keys exist and values are lists of strings
            for key in default_filters:
                if key in loaded_filters and isinstance(loaded_filters[key], list):
                    # Ensure all items in the list are strings
                    if all(isinstance(item, str) for item in loaded_filters[key]):
                        default_filters[key] = loaded_filters[key]
                    else:
                        print(
                            f"Warning: Non-string item found in '{key}' list in {file_path}. Ignoring this filter key."
                        )
                elif key in loaded_filters:
                    print(
                        f"Warning: Invalid type for '{key}' in {file_path}. Expected a list of strings. Ignoring this filter key."
                    )
            # Check for unexpected keys
            extra_keys = set(loaded_filters.keys()) - set(default_filters.keys())
            if extra_keys:
                print(
                    f"Warning: Unexpected keys found in {file_path}: {', '.join(extra_keys)}. These will be ignored."
                )
            return default_filters
    except FileNotFoundError:
        print(
            f"Warning: Filters file '{file_path}' not found. Using default empty filters."
        )
        return default_filters
    except json.JSONDecodeError:
        print(
            f"Error: Could not decode JSON from '{file_path}'. Using default empty filters."
        )
        return default_filters
    except Exception as e:
        print(
            f"An unexpected error occurred while loading filters from '{file_path}': {e}. Using default empty filters."
        )
        return default_filters
