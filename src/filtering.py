from typing import Any, Dict, List
from print_helpers import print_warning


def _check_match(text: str, filters: List[str]) -> bool:
    """Checks if the text contains any of the filter strings."""
    if not filters:
        # No filters of this type, always counts as no match for this criterion
        return False

    text = text.lower()
    filters = [f.lower() for f in filters]
    return any(f in text for f in filters)


def filter_documents(
    documents: List[Dict[str, Any]],
    filters: Dict[str, List[str]],
) -> List[str]:
    """Filters documents based on criteria defined in the filters dictionary."""

    matching_ids: List[str] = []
    title_filters = filters.get("title_exclude", [])
    url_filters = filters.get("url_exclude", [])

    if not any([title_filters, url_filters]):
        print_warning("No filter values provided in the configuration.")
        return []

    for doc in documents:
        doc_id = doc.get("id")
        if not doc_id:
            # Skip documents without an ID
            continue

        title = doc.get("title", "")
        url = doc.get("source_url", "")

        title_match = _check_match(title, title_filters)
        url_match = _check_match(url, url_filters)

        if title_match or url_match:
            matching_ids.append(doc_id)

    return matching_ids
