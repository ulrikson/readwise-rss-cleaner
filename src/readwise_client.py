from typing import Any, Dict, List

import backoff
import requests


READWISE_API_BASE = "https://readwise.io/api/v3"

# Backoff parameters: max 5 attempts, max delay 60 seconds
MAX_TRIES = 5
MAX_DELAY = 60


def _get_auth_header(api_token: str) -> Dict[str, str]:
    """Constructs the authorization header."""
    return {"Authorization": f"Token {api_token}"}


def fetch_feed_documents(api_token: str) -> List[Dict[str, Any]]:
    """Fetches all documents from the Readwise Reader feed.

    Args:
        api_token: The Readwise API token.

    Returns:
        A list of documents from the feed.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    headers = _get_auth_header(api_token)
    documents: List[Dict[str, Any]] = []
    next_page_cursor = None

    while True:
        params = {"location": "feed"}
        if next_page_cursor:
            params["pageCursor"] = next_page_cursor

        try:
            response = requests.get(
                f"{READWISE_API_BASE}/list",
                headers=headers,
                params=params,
                timeout=30,  # Add a timeout
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            documents.extend(data.get("results", []))
            next_page_cursor = data.get("nextPageCursor")
            if not next_page_cursor:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching documents: {e}")
            raise  # Re-raise the exception after logging

    print(f"Fetched {len(documents)} documents from the feed.")
    return documents


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=MAX_TRIES,
    max_time=MAX_DELAY,
    on_giveup=lambda details: print(
        f"Giving up deleting {details['args'][1]} after {details['tries']} tries."
    ),
    on_backoff=lambda details: print(
        f"Retrying delete {details['args'][1]} in {details['wait']:.1f} seconds..."
    ),
)
def delete_document(api_token: str, document_id: str) -> bool:
    """Deletes a specific document using the Readwise API with exponential backoff.

    Args:
        api_token: The Readwise API token.
        document_id: The ID of the document to delete.

    Returns:
        True if deletion was successful. Raises RequestException if unsuccessful after retries.
    """
    headers = _get_auth_header(api_token)
    url = f"{READWISE_API_BASE}/delete/{document_id}/"

    response = requests.delete(url, headers=headers, timeout=15)
    response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

    print(f"Successfully deleted document {document_id}.")
    return True
