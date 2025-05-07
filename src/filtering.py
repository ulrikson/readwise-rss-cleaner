from typing import Any, Dict, List, Optional
from print_helpers import print_warning


def _check_match(text: str, filters: List[str]) -> bool:
    """Checks if the text contains any of the filter strings."""
    if not filters:
        return False

    text = text.lower()
    return any(f.lower() in text for f in filters)


def filter_documents(
    documents: List[Dict[str, Any]],
    filters: Dict[str, List[str]],
) -> List[str]:
    """Filters documents based on criteria defined in the filters dictionary."""
    title_filters = filters.get("title_exclude", [])
    url_filters = filters.get("url_exclude", [])
    author_filters = filters.get("author_exclude", [])

    if not any([title_filters, url_filters, author_filters]):
        print_warning("No filter values provided in the configuration.")
        return []

    matching_ids = []
    for doc in documents:
        if doc_id := doc.get("id"):
            title = doc.get("title", "")
            url = doc.get("source_url", "")
            author = doc.get("author", "")

            if (
                _check_match(title, title_filters)
                or _check_match(url, url_filters)
                or _check_match(author, author_filters)
            ):
                matching_ids.append(doc_id)

    return matching_ids


def determine_save_location(
    document: Dict[str, Any],
    filters: Dict[str, List[str]],
) -> Optional[str]:
    """Determines if a document should be saved and to what location."""
    author = document.get("author", "")
    if not author:
        return None

    # Check "later" filters first (they take precedence)
    if later_filters := filters.get("author_save_later", []):
        if _check_match(author, later_filters):
            return "later"

    # Then check "inbox" filters
    if inbox_filters := filters.get("author_save_inbox", []):
        if _check_match(author, inbox_filters):
            return "new"  # "new" corresponds to inbox in Readwise

    return None
