from typing import Any, Dict, List, Set, Tuple
from print_helpers import print_warning, print_error
from openai_client import filter_by_topic
from config import load_filters_from_json

# Default filters file path
DEFAULT_FILTERS_PATH = "filters.json"


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
    author_filters = filters.get("author_exclude", [])

    if not any([title_filters, url_filters, author_filters]):
        print_warning("No filter values provided in the configuration.")
        return []

    for doc in documents:
        doc_id = doc.get("id")
        if not doc_id:
            # Skip documents without an ID
            continue

        title = doc.get("title", "")
        url = doc.get("source_url", "")
        author = doc.get("author", "")

        title_match = _check_match(title, title_filters)
        url_match = _check_match(url, url_filters)
        author_match = _check_match(author, author_filters)

        if title_match or url_match or author_match:
            matching_ids.append(doc_id)

    return matching_ids


def _has_active_filters(filters: Dict[str, List[str]]) -> bool:
    """Check if there are any active filters."""
    return any(filters.values())


def _extract_filter_types(
    filters: Dict[str, List[str]],
) -> Tuple[Dict[str, List[str]], List[str]]:
    """Extract AI filters from standard filters."""
    ai_exclude_topics = filters.get("ai_topic_exclude", [])
    standard_filters = {k: v for k, v in filters.items() if k != "ai_topic_exclude"}
    return standard_filters, ai_exclude_topics


def _apply_standard_filters(
    documents: List[Dict[str, Any]], standard_filters: Dict[str, List[str]]
) -> Set[str]:
    """Apply standard filters to documents and return matching IDs."""
    return (
        set(filter_documents(documents, standard_filters))
        if _has_active_filters(standard_filters)
        else set()
    )


def _apply_ai_filters(
    documents: List[Dict[str, Any]], ai_exclude_topics: List[str]
) -> Set[str]:
    """Apply AI topic filtering to documents and return matching IDs."""
    if not ai_exclude_topics:
        return set()

    try:
        return set(filter_by_topic(documents, ai_exclude_topics))
    except Exception as e:
        print_error(f"AI topic analysis failed: {e}")
        return set()


def load_and_process_filters() -> Tuple[Dict[str, List[str]], List[str], bool]:
    """Load filters from default path and process them."""
    filters = load_filters_from_json(DEFAULT_FILTERS_PATH)
    standard_filters, ai_exclude_topics = _extract_filter_types(filters)
    has_filters = _has_active_filters(standard_filters) or bool(ai_exclude_topics)
    return standard_filters, ai_exclude_topics, has_filters


def filter_all_documents(
    documents: List[Dict[str, Any]],
    standard_filters: Dict[str, List[str]],
    ai_exclude_topics: List[str],
) -> List[str]:
    """Apply all filters to documents and return a list of document IDs to delete."""
    standard_filtered_ids = _apply_standard_filters(documents, standard_filters)
    ai_filtered_ids = _apply_ai_filters(documents, ai_exclude_topics)
    all_ids_to_delete = standard_filtered_ids | ai_filtered_ids
    return list(all_ids_to_delete)
