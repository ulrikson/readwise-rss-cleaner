from typing import Any, Dict, List

import backoff
import requests

from config import load_readwise_api_token
from print_helpers import print_warning, print_error

READWISE_API_BASE = "https://readwise.io/api/v3"
MAX_TRIES = 5
MAX_DELAY = 60


def _get_auth_header() -> Dict[str, str]:
    """Constructs the authorization header."""
    api_token = load_readwise_api_token()
    if not api_token:
        print_error("Readwise API token not found.")
        return None
    return {"Authorization": f"Token {api_token}"}


def fetch_feed_documents(updated_after: str) -> List[Dict[str, Any]]:
    """Fetches all documents from the Readwise Reader feed, optionally filtering by updatedAfter (ISO 8601)."""
    headers = _get_auth_header()
    documents: List[Dict[str, Any]] = []
    next_page_cursor = None

    while True:
        params = {"location": "feed"}
        if updated_after:
            params["updatedAfter"] = updated_after
        if next_page_cursor:
            params["pageCursor"] = next_page_cursor

        try:
            response = requests.get(
                f"{READWISE_API_BASE}/list",
                headers=headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            documents.extend(data.get("results", []))
            next_page_cursor = data.get("nextPageCursor")

            if not next_page_cursor:
                break
        except requests.exceptions.RequestException as e:
            print_error(f"Error fetching documents: {e}")
            raise

    print_warning(f"Fetched {len(documents)} documents from the feed.")
    return documents


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=MAX_TRIES,
    max_time=MAX_DELAY,
    on_giveup=lambda details: print_error(
        f"Giving up deleting {details['args'][1]} after {details['tries']} tries."
    ),
    on_backoff=lambda details: print_warning(
        f"Retrying delete {details['args'][1]} in {details['wait']:.1f} seconds..."
    ),
)
def delete_document(document_id: str) -> bool:
    """Deletes a specific document using the Readwise API with exponential backoff."""
    headers = _get_auth_header()
    url = f"{READWISE_API_BASE}/delete/{document_id}/"

    response = requests.delete(url, headers=headers, timeout=15)
    response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
    return True
