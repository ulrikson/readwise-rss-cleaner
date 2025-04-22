from typing import Any, Dict, List


def _check_match(text: str, filters: List[str], case_sensitive: bool = False) -> bool:
    """Checks if the text contains any of the filter strings."""
    if (
        not filters
    ):  # No filters of this type, always counts as no match for this criterion
        return False
    if not case_sensitive:
        text = text.lower()
        filters = [f.lower() for f in filters]
    return any(f in text for f in filters)


def filter_documents(
    documents: List[Dict[str, Any]],
    filters: Dict[str, List[str]],  # Changed signature to accept filters dictionary
) -> List[str]:
    """Filters documents based on criteria defined in the filters dictionary.

    The document is marked for deletion if it matches *any* of the criteria
    defined in the corresponding filter list (e.g., any title_contains string).
    Currently, this implements an OR logic *within* each filter type, and documents
    matching *any* active filter type are returned.
    TODO: Revisit if AND logic across filter types is needed (e.g., title AND url).

    Args:
        documents: A list of document dictionaries from the Readwise API.
        filters: A dictionary with keys like 'title_contains', 'summary_contains',
                 'url_contains', where each value is a list of strings to filter by.

    Returns:
        A list of document IDs that match any of the filter criteria.
    """
    matching_ids: List[str] = []
    # Extract filter lists from the dictionary
    title_filters = filters.get("title_contains", [])
    summary_filters = filters.get("summary_contains", [])
    url_filters = filters.get("url_contains", [])

    if not any([title_filters, summary_filters, url_filters]):
        print("Warning: No filter values provided in the configuration.")
        return []

    for doc in documents:
        doc_id = doc.get("id")
        if not doc_id:
            continue  # Skip documents without an ID

        title = doc.get("title", "")
        summary = doc.get("summary", "")  # Assuming field exists
        url = doc.get("source_url", "")  # Assuming field exists

        # Check if the document matches *any* of the filters for each type
        # This is OR logic: delete if title matches OR summary matches OR url matches
        # any of the respective filter strings.
        title_match = _check_match(title, title_filters, case_sensitive=False)
        summary_match = _check_match(summary, summary_filters, case_sensitive=False)
        url_match = _check_match(
            url, url_filters, case_sensitive=True
        )  # URLs are often case-sensitive

        if title_match or summary_match or url_match:
            matching_ids.append(doc_id)

    print(f"Found {len(matching_ids)} documents matching filter criteria.")
    return matching_ids
