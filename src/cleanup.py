from typing import List, Optional, Dict, Any, Tuple
from filtering import (
    filter_all_documents,
    load_and_process_filters,
)
from readwise_client import delete_document, fetch_feed_documents
from print_helpers import (
    print_warning,
    print_error,
    print_success,
    print_neutral,
    print_bold,
    print_info,
)


def fetch_documents(updated_after: str) -> Optional[List[Dict[str, Any]]]:
    try:
        return fetch_feed_documents(updated_after)
    except Exception as e:
        print_warning(f"Failed to fetch documents: {e}. Exiting.")
        return None


def print_dry_run(documents: List[Dict[str, Any]], ids_to_delete: List[str]) -> None:
    print_info("Dry run enabled. No documents will be deleted.")
    [
        print_neutral(f"  - {doc.get('title', 'N/A')} (ID: {doc.get('id')})")
        for doc in documents
        if doc.get("id") in ids_to_delete
    ]


def delete_documents(ids_to_delete: List[str]) -> Tuple[int, int]:
    deleted = sum(1 for doc_id in ids_to_delete if delete_document(doc_id))
    failed = len(ids_to_delete) - deleted
    return deleted, failed


def print_cleanup_summary(
    total: int, deleted: int, failed: int, from_ai: int = 0
) -> None:
    print_bold("\n--- Cleanup Summary ---")
    print_neutral(f"Documents matching filters: {total}")
    if from_ai:
        print_neutral(f"  (Including {from_ai} identified by AI topic filter)")
    print_success(f"Deleted {deleted} documents")
    if failed:
        print_error(f"Failed to delete: {failed}")


def _handle_no_documents_found(documents: Optional[List[Dict[str, Any]]]) -> bool:
    if not documents:
        print_warning("No documents found matching the updated_after criteria.")
        return True
    return False


def _handle_no_matches(ids_to_delete: List[str]) -> bool:
    if not ids_to_delete:
        print_info("No documents matched any filter criteria.")
        return True
    return False


def run_cleanup(dry_run: bool = False, updated_after: str = "") -> None:
    print_bold("Starting Readwise Reader cleanup...")

    standard_filters, ai_exclude_topics, has_filters = load_and_process_filters()
    if not has_filters:
        print_warning("No active filters found. Exiting.")
        return

    documents = fetch_documents(updated_after)
    if _handle_no_documents_found(documents):
        return

    documents = documents or []
    ids_to_delete = filter_all_documents(documents, standard_filters, ai_exclude_topics)

    if _handle_no_matches(ids_to_delete):
        return

    if dry_run:
        print_dry_run(documents, ids_to_delete)
        return

    deleted_count, failed_count = delete_documents(ids_to_delete)

    print_cleanup_summary(len(ids_to_delete), deleted_count, failed_count)
