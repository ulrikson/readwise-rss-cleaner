import os
import json
from typing import Optional, Dict, List, Any

from dotenv import load_dotenv
from rich.console import Console

load_dotenv(override=True)


def load_readwise_api_token() -> Optional[str]:
    """Loads the Readwise API token from environment variables."""
    return os.getenv("READWISE_API_TOKEN")


def load_openai_api_key() -> Optional[str]:
    """Loads the OpenAI API key from environment variables."""
    return os.getenv("OPENAI_API_KEY")


def load_filters_from_json(file_path: str) -> Dict[str, List[str]]:
    """Loads and validates filter criteria from a JSON file."""
    default_keys = [
        "title_contains",
        "summary_contains",
        "url_contains",
        "ai_topic_exclude",
    ]
    filters: Dict[str, List[str]] = {key: [] for key in default_keys}

    try:
        with open(file_path, "r", encoding="utf-8") as filters_file:
            loaded_data: Dict[str, Any] = json.load(filters_file)

        for key in default_keys:
            filter_list = loaded_data.get(key)
            if isinstance(filter_list, list) and all(
                isinstance(item, str) for item in filter_list
            ):
                filters[key] = filter_list
            elif filter_list is not None:
                Console().print(
                    f"[yellow]Warning:[/yellow] Invalid format for '{key}' in {file_path}. Expected list of strings. Using empty list instead."
                )
                filters[key] = []

    except FileNotFoundError:
        Console().print(
            f"[bold red]Error:[/bold red] Filters file not found at '{file_path}'. Using default empty filters."
        )
        return {key: [] for key in default_keys}
    except json.JSONDecodeError:
        Console().print(
            f"[bold red]Error:[/bold red] Failed to decode JSON from '{file_path}'. Using default empty filters."
        )
        return {key: [] for key in default_keys}
    except Exception as e:
        Console().print(
            f"[bold red]Error:[/bold red] An unexpected error occurred while loading filters: {e}. Using default empty filters."
        )
        return {key: [] for key in default_keys}

    return filters
