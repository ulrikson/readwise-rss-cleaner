from typing import List, Dict, Any, Tuple

from data_types import SaveAction
from readwise_client import update_document, fetch_feed_documents
from filtering import determine_save_location
from print_helpers import (
    print_warning,
    print_error,
    print_bold,
    print_info,
    print_dry_run_save,
    print_save_summary,
)


def fetch_documents_for_save() -> List[Dict[str, Any]]:
    """Fetch documents from Readwise Reader API."""
    try:
        docs = fetch_feed_documents()
        # Filter out documents already in 'archive' or 'later' to avoid redundant updates
        return (
            [doc for doc in docs if doc.get("location") not in ["archive", "later"]]
            if docs
            else []
        )
    except Exception as e:
        print_warning(f"Failed to fetch documents: {e}. Returning empty list.")
        return []


def update_document_location(doc_id: str, location: str) -> bool:
    """Update document location and return success status."""
    try:
        update_document(doc_id, location)
        return True
    except Exception as e:
        print_error(f"Failed to update document {doc_id} to {location}: {e}")
        return False


def update_documents(actions: List[SaveAction]) -> Tuple[int, int]:
    """Update document locations and return counts of successful and failed updates."""
    updated = sum(
        1
        for action in actions
        if update_document_location(action.doc_id, action.location)
    )
    failed = len(actions) - updated
    return updated, failed


def _collect_save_actions(
    documents: List[Dict[str, Any]], filters: Dict[str, List[str]]
) -> List[SaveAction]:
    """Collect save actions for documents based on filter criteria."""
    actions: List[SaveAction] = []

    for doc in documents:
        doc_id = doc.get("id")
        if not doc_id:
            continue

        if location := determine_save_location(doc, filters):
            actions.append(SaveAction(doc_id=doc_id, location=location))

    return actions


def run_save(filters: Dict[str, List[str]], dry_run: bool = False) -> None:
    """Process documents with save filters and update matching items' locations."""
    print_bold("Starting Readwise Reader save process...")

    # Check if any save filters are defined
    save_filters_exist = bool(
        filters.get("author_save_inbox") or filters.get("author_save_later")
    )
    if not save_filters_exist:
        print_warning("No active save filters found. Exiting.")
        return

    documents = fetch_documents_for_save()
    if not documents:
        print_warning("No suitable documents found matching the criteria.")
        return

    actions_to_take = _collect_save_actions(documents, filters)
    if not actions_to_take:
        print_info("No documents matched any save filter criteria.")
        return

    if dry_run:
        print_dry_run_save(documents, actions_to_take)
        return

    updated_count, failed_count = update_documents(actions_to_take)
    print_save_summary(len(actions_to_take), updated_count, failed_count)
