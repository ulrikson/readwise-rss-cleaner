import os
import json
from typing import Optional, Dict, List, Any
import requests

from dotenv import load_dotenv
from print_helpers import print_warning

load_dotenv(override=True)

DEFAULT_FILTERS = {
    "title_exclude": [],
    "url_exclude": [],
    "ai_topic_exclude": [],
}


def load_readwise_api_token() -> str:
    """Loads the Readwise API token from environment variables."""
    token = os.getenv("READWISE_API_TOKEN")
    if not token:
        raise ValueError("READWISE_API_TOKEN environment variable is not set")
    return token


def load_openai_api_key() -> Optional[str]:
    """Loads the OpenAI API key from environment variables."""
    return os.getenv("OPENAI_API_TOKEN")


def load_gist_id() -> str:
    """Loads the GitHub Gist ID from environment variables."""
    gist_id = os.getenv("GIST_ID")
    if not gist_id:
        raise ValueError("GIST_ID environment variable is not set")
    return gist_id


def load_filters() -> Dict[str, List[str]]:
    """Loads filters from the GitHub gist."""
    try:
        gist_id = load_gist_id()

        api_url = f"https://api.github.com/gists/{gist_id}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        gist_data = response.json()

        # Get the first file in the gist
        file_content = next(iter(gist_data["files"].values()))["content"]
        loaded_data = json.loads(file_content)

        return {key: loaded_data.get(key, []) for key in DEFAULT_FILTERS}
    except Exception as e:
        print_warning(f"Failed to fetch filters from gist: {e}")
        return DEFAULT_FILTERS


if __name__ == "__main__":
    filters = load_filters()
    print(filters)
