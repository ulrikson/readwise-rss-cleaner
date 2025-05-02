from typing import Dict, List
import json

import requests

from config import load_gist_id, DEFAULT_FILTERS
from print_helpers import print_warning

BASE_URL = "https://api.github.com/gists"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def load_filters() -> Dict[str, List[str]]:
    """Loads filters from the GitHub gist."""
    try:
        gist_id = load_gist_id()

        api_url = f"{BASE_URL}/{gist_id}"

        response = requests.get(api_url, headers=HEADERS)
        response.raise_for_status()

        gist_data = response.json()

        # Get the first file in the gist
        file_content = next(iter(gist_data["files"].values()))["content"]
        loaded_data = json.loads(file_content)

        return {key: loaded_data.get(key, []) for key in DEFAULT_FILTERS}
    except Exception as e:
        print_warning(f"Failed to fetch filters from gist: {e}")
        return DEFAULT_FILTERS
