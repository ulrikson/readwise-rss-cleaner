import os
import json
from typing import Optional, Dict, List, Any

from dotenv import load_dotenv


def load_api_token() -> Optional[str]:
    """Loads the Readwise API token from environment variables."""
    load_dotenv()
    return os.getenv("READWISE_API_TOKEN")


def load_filters_from_json(file_path: str) -> Dict[str, List[str]]:
    """Loads and validates filter criteria from a JSON file."""
    default_keys = ["title_contains", "summary_contains", "url_contains"]
    filters: Dict[str, List[str]] = {key: [] for key in default_keys}

    try:
        with open(file_path, "r", encoding="utf-8") as filters_file:
            loaded_data: Dict[str, Any] = json.load(filters_file)

        for key in default_keys:
            filter_list = loaded_data.get(key)
            filters[key] = filter_list

    except Exception as e:
        print(
            f"Error: An unexpected error occurred while loading filters: {e}. Using default empty filters."
        )
        return {key: [] for key in default_keys}

    return filters
