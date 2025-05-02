from typing import List, Optional, Dict, Any, Tuple, Set, NamedTuple
from filtering import filter_documents
from readwise_client import delete_document, fetch_feed_documents
from openai_client import filter_by_topic
from print_helpers import (
    print_warning,
    print_error,
    print_bold,
    print_info,
    print_dry_run,
    print_cleanup_summary,
)


class FilterConfig(NamedTuple):
    """Data transfer object for filter configuration and state."""

    standard_filters: Dict[str, List[str]]
    ai_exclude_topics: List[str]
    has_standard_filters: bool
    has_ai_filters: bool

    @property
    def is_valid(self) -> bool:
        """Check if any filters are active."""
        return self.has_standard_filters or self.has_ai_filters


def has_active_filters(filters: Dict[str, List[str]]) -> bool:
    """Check if any filters are active and non-empty."""
    return any(filters.values())


def fetch_documents(updated_after: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch documents from Readwise Reader API updated after the specified date."""
    try:
        return fetch_feed_documents(updated_after)
    except Exception as e:
        print_warning(f"Failed to fetch documents: {e}. Exiting.")
        return None


def delete_documents(ids_to_delete: List[str]) -> Tuple[int, int]:
    """Delete documents by ID and return counts of successful and failed deletions."""
    deleted = sum(1 for doc_id in ids_to_delete if delete_document(doc_id))
    failed = len(ids_to_delete) - deleted
    return deleted, failed


def _prepare_filters(filters: Dict[str, List[str]]) -> FilterConfig:
    """Extract and prepare filters, returning FilterConfig object."""
    ai_exclude_topics = filters.get("ai_topic_exclude", [])
    standard_filters = {k: v for k, v in filters.items() if k != "ai_topic_exclude"}
    has_standard_filters = has_active_filters(standard_filters)
    has_ai_filters = bool(ai_exclude_topics)

    return FilterConfig(
        standard_filters=standard_filters,
        ai_exclude_topics=ai_exclude_topics,
        has_standard_filters=has_standard_filters,
        has_ai_filters=has_ai_filters,
    )


def _apply_standard_filters(
    documents: List[Dict[str, Any]], filter_config: FilterConfig
) -> Set[str]:
    """Apply standard keyword/pattern filters to documents and return matching IDs."""
    if not filter_config.has_standard_filters:
        return set()

    return set(filter_documents(documents, filter_config.standard_filters))


def _apply_ai_filters(
    documents: List[Dict[str, Any]], filter_config: FilterConfig
) -> Set[str]:
    """Apply AI-based topic filtering to documents and return matching IDs."""
    if not filter_config.has_ai_filters:
        return set()

    try:
        return set(filter_by_topic(documents, filter_config.ai_exclude_topics))
    except Exception as e:
        print_error(f"AI topic analysis failed: {e}")
        return set()


def _collect_documents_to_delete(
    documents: List[Dict[str, Any]], filter_config: FilterConfig
) -> Tuple[List[str], int]:
    """Process documents with filters and return IDs to delete and AI filter count."""
    standard_filtered_ids = _apply_standard_filters(documents, filter_config)
    ai_filtered_ids = _apply_ai_filters(documents, filter_config)
    all_ids_to_delete = list(standard_filtered_ids | ai_filtered_ids)
    return all_ids_to_delete, len(ai_filtered_ids)


def run_cleanup(
    filters: Dict[str, List[str]], dry_run: bool = False, updated_after: str = ""
) -> None:
    """Process documents with configured filters and delete matching items."""
    print_bold("Starting Readwise Reader cleanup...")

    filter_config = _prepare_filters(filters)
    if not filter_config.is_valid:
        print_warning("No active filters found. Exiting.")
        return

    documents = fetch_documents(updated_after)
    if not documents:
        print_warning("No documents found matching the updated_after criteria.")
        return

    ids_to_delete, ai_filtered_count = _collect_documents_to_delete(
        documents, filter_config
    )
    if not ids_to_delete:
        print_info("No documents matched any filter criteria.")
        return

    if dry_run:
        print_dry_run(documents, ids_to_delete)
        return

    deleted_count, failed_count = delete_documents(ids_to_delete)
    print_cleanup_summary(
        len(ids_to_delete), deleted_count, failed_count, ai_filtered_count
    )
