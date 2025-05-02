from typing import List, Optional, Dict, Any, Tuple, Set
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


def has_active_filters(filters: Dict[str, List[str]]) -> bool:
    return any(filters.values())


def fetch_documents(updated_after: str) -> Optional[List[Dict[str, Any]]]:
    try:
        return fetch_feed_documents(updated_after)
    except Exception as e:
        print_warning(f"Failed to fetch documents: {e}. Exiting.")
        return None


def delete_documents(ids_to_delete: List[str]) -> Tuple[int, int]:
    deleted = sum(1 for doc_id in ids_to_delete if delete_document(doc_id))
    failed = len(ids_to_delete) - deleted
    return deleted, failed


def _extract_filter_types(
    filters: Dict[str, List[str]],
) -> Tuple[Dict[str, List[str]], List[str]]:
    ai_exclude_topics = filters.get("ai_topic_exclude", [])
    standard_filters = {k: v for k, v in filters.items() if k != "ai_topic_exclude"}
    return standard_filters, ai_exclude_topics


def _apply_standard_filters(
    documents: List[Dict[str, Any]], standard_filters: Dict[str, List[str]]
) -> Set[str]:
    return (
        set(filter_documents(documents, standard_filters))
        if has_active_filters(standard_filters)
        else set()
    )


def _apply_ai_filters(
    documents: List[Dict[str, Any]], ai_exclude_topics: List[str]
) -> Set[str]:
    try:
        return set(filter_by_topic(documents, ai_exclude_topics))
    except Exception as e:
        print_error(f"AI topic analysis failed: {e}")
        return set()


def run_cleanup(
    filters: Dict[str, List[str]], dry_run: bool = False, updated_after: str = ""
) -> None:
    print_bold("Starting Readwise Reader cleanup...")

    standard_filters, ai_exclude_topics = _extract_filter_types(filters)
    if not has_active_filters(standard_filters) and not ai_exclude_topics:
        print_warning("No active filters found. Exiting.")
        return

    documents = fetch_documents(updated_after)
    if not documents:
        print_warning("No documents found matching the updated_after criteria.")
        return

    standard_filtered_ids = _apply_standard_filters(documents, standard_filters)
    ai_filtered_ids = _apply_ai_filters(documents, ai_exclude_topics)
    all_ids_to_delete = standard_filtered_ids | ai_filtered_ids

    if not all_ids_to_delete:
        print_info("No documents matched any filter criteria.")
        return

    ids_to_delete_list = list(all_ids_to_delete)

    if dry_run:
        print_dry_run(documents, ids_to_delete_list)
        return

    deleted_count, failed_count = delete_documents(ids_to_delete_list)
    print_cleanup_summary(
        len(ids_to_delete_list), deleted_count, failed_count, len(ai_filtered_ids)
    )
