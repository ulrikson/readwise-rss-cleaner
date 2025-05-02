from typing import Any, Dict, List
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

    if not any([title_filters, url_filters]):
        print_warning("No filter values provided in the configuration.")
        return []

    matching_ids = []
    for doc in documents:
        if doc_id := doc.get("id"):
            title = doc.get("title", "")
            url = doc.get("source_url", "")

            if _check_match(title, title_filters) or _check_match(url, url_filters):
                matching_ids.append(doc_id)

    return matching_ids
