import time
from typing import Any, Dict, List, Optional

import requests


READWISE_API_BASE = "https://readwise.io/api/v3"
# Rate limit: 20 requests per minute. Wait 3 seconds between deletes.
DELETE_DELAY_SECONDS = 3


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


def delete_document(api_token: str, document_id: str) -> bool:
    """Deletes a specific document using the Readwise API.

    Args:
        api_token: The Readwise API token.
        document_id: The ID of the document to delete.

    Returns:
        True if deletion was successful, False otherwise.
    """
    headers = _get_auth_header(api_token)
    url = f"{READWISE_API_BASE}/delete/{document_id}/"
    try:
        response = requests.post(
            url, headers=headers, timeout=15
        )  # Use POST as per PRD
        response.raise_for_status()
        print(f"Successfully deleted document {document_id}.")
        # Respect rate limit
        time.sleep(DELETE_DELAY_SECONDS)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error deleting document {document_id}: {e}")
        # Optional: add a small delay even on failure to avoid hammering the API
        time.sleep(1)
        return False
