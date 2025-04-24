import os
import json
from typing import Optional, Dict, List, Any

from dotenv import load_dotenv
from print_helpers import print_warning

load_dotenv(override=True)

DEFAULT_FILTERS = {
    "title_exclude": [],
    "url_exclude": [],
    "ai_topic_exclude": [],
}


def load_readwise_api_token() -> Optional[str]:
    """Loads the Readwise API token from environment variables."""
    return os.getenv("READWISE_API_TOKEN")


def load_openai_api_key() -> Optional[str]:
    """Loads the OpenAI API key from environment variables."""
    return os.getenv("OPENAI_API_KEY")


def _read_filters_file(file_path: str) -> Dict[str, List[str]]:
    with open(file_path, "r", encoding="utf-8") as filters_file:
        loaded_data: Dict[str, Any] = json.load(filters_file)

    return {key: loaded_data.get(key, []) for key in DEFAULT_FILTERS}


def load_filters_from_json(file_path: str) -> Dict[str, List[str]]:
    try:
        return _read_filters_file(file_path)
    except FileNotFoundError:
        print_warning(f"Filters file not found at '{file_path}'.")
    except json.JSONDecodeError:
        print_warning(f"Failed to decode JSON from '{file_path}'.")
    except Exception as e:
        print_warning(f"An unexpected error occurred while loading filters: {e}.")
    return DEFAULT_FILTERS
