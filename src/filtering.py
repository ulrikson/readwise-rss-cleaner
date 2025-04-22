from typing import Any, Dict, List, Optional


def filter_documents(
    documents: List[Dict[str, Any]],
    title_contains: Optional[str] = None,
    summary_contains: Optional[str] = None,
    url_contains: Optional[str] = None,
) -> List[str]:
    """Filters documents based on provided criteria.

    Args:
        documents: A list of document dictionaries from the Readwise API.
        title_contains: Substring to match in the document title (case-insensitive).
        summary_contains: Substring to match in the document summary (case-insensitive).
        url_contains: Substring to match in the document URL (case-sensitive).

    Returns:
        A list of document IDs that match the filter criteria.
    """
    matching_ids: List[str] = []
    # Normalize string filters for case-insensitive comparison
    title_filter = title_contains.lower() if title_contains else None
    summary_filter = summary_contains.lower() if summary_contains else None

    for doc in documents:
        doc_id = doc.get("id")
        if not doc_id:
            continue  # Skip documents without an ID

        title = doc.get("title", "")
        summary = doc.get("summary", "")  # Assuming 'summary' field exists
        url = doc.get("source_url", "")  # Assuming 'source_url' is the correct field

        matches = True  # Assume match initially

        if title_filter and title_filter not in title.lower():
            matches = False
        if summary_filter and summary_filter not in summary.lower():
            matches = False
        if url_contains and url_contains not in url:
            matches = False

        # Document should match *all* provided filters
        if matches and (title_contains or summary_contains or url_contains):
            # Ensure at least one filter was active
            matching_ids.append(doc_id)

    print(f"Found {len(matching_ids)} documents matching filter criteria.")
    return matching_ids
