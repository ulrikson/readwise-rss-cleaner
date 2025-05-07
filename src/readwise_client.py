from typing import Any, Dict, List

import backoff
import requests

from config import load_readwise_api_token
from print_helpers import print_warning, print_error, print_info

BASE_URL = "https://readwise.io/api/v3"
MAX_TRIES = 5
MAX_DELAY = 60
REQUEST_TIMEOUT = 30


def _get_auth_header() -> Dict[str, str]:
    """Constructs the authorization header."""
    api_token = load_readwise_api_token()
    return {"Authorization": f"Token {api_token}"}


def _build_fetch_params(updated_after: str, next_page_cursor: str) -> Dict[str, str]:
    """Builds the parameters for the fetch API request."""
    params = {"location": "feed"}
    if updated_after:
        params["updatedAfter"] = updated_after
    if next_page_cursor:
        params["pageCursor"] = next_page_cursor
    return params


def fetch_feed_documents(updated_after: str = "") -> List[Dict[str, Any]]:
    """Fetches all documents from the Readwise Reader feed, optionally filtering by updatedAfter (ISO 8601)."""
    headers = _get_auth_header()
    documents = []
    next_page_cursor = None
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/list",
                headers=headers,
                params=_build_fetch_params(updated_after, next_page_cursor),
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            documents.extend(data.get("results", []))
            next_page_cursor = data.get("nextPageCursor")

            if not next_page_cursor:
                break

        except Exception as e:
            raise e

    print_info(f"Fetched {len(documents)} documents from the feed.")
    return documents


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=MAX_TRIES,
    max_time=MAX_DELAY,
    on_giveup=lambda details: print_error(
        f"Giving up deleting document after {details['tries']} tries."
    ),
    on_backoff=lambda details: print_warning(
        f"Rate limited. Retrying in {details['wait']:.1f} seconds..."
    ),
)
def delete_document(document_id: str) -> bool:
    headers = _get_auth_header()
    response = requests.delete(
        f"{BASE_URL}/delete/{document_id}/", headers=headers, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return True


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=MAX_TRIES,
    max_time=MAX_DELAY,
    on_giveup=lambda details: print_error(
        f"Giving up updating document after {details['tries']} tries."
    ),
    on_backoff=lambda details: print_warning(
        f"Rate limited. Retrying in {details['wait']:.1f} seconds..."
    ),
)
def update_document(document_id: str, location: str) -> Dict[str, Any]:
    """Updates a document's location in Readwise Reader."""
    headers = _get_auth_header()
    payload = {"location": location}
    response = requests.patch(
        f"{BASE_URL}/update/{document_id}/",
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()
