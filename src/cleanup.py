from typing import List, Optional, Dict, Any, Tuple
from filtering import filter_documents
from readwise_client import delete_document, fetch_feed_documents


def has_active_filters(filters: Dict[str, List[str]]) -> bool:
    return any(filters.values())


def fetch_documents(api_token: str) -> Optional[List[Dict[str, Any]]]:
    try:
        return fetch_feed_documents(api_token)
    except Exception:
        print("Failed to fetch documents. Exiting.")
        return None


def print_dry_run(documents: List[Dict[str, Any]], ids_to_delete: List[str]) -> None:
    print("Dry run enabled. No documents will be deleted.")
    print("--- Documents matching filters --- ")
    for doc in documents:
        if doc.get("id") in ids_to_delete:
            print(f"  - {doc.get('title', 'N/A')} (ID: {doc.get('id')})")
    print("----------------------------------")


def delete_documents(api_token: str, ids_to_delete: List[str]) -> Tuple[int, int]:
    deleted_count = 0
    failed_count = 0
    for doc_id in ids_to_delete:
        if delete_document(api_token, doc_id):
            deleted_count += 1
        else:
            failed_count += 1
    return deleted_count, failed_count


def print_cleanup_summary(total: int, deleted: int, failed: int) -> None:
    print("\n--- Cleanup Summary ---")
    print(f"Documents matching filters: {total}")
    print(f"Successfully deleted: {deleted}")
    if failed > 0:
        print(f"Failed to delete: {failed}")
    print("----------------------")


def run_cleanup(
    api_token: str, filters: Dict[str, List[str]], dry_run: bool = False
) -> None:
    print("Starting Readwise Reader cleanup...")

    if not has_active_filters(filters):
        print("No active filters found in the configuration file. Exiting.")
        return

    documents = fetch_documents(api_token)
    if documents is None or not documents:
        print("Failed to fetch documents. Exiting.")
        return

    ids_to_delete = filter_documents(documents, filters)
    if not ids_to_delete:
        print("No documents matched the filter criteria.")
        return

    print(f"Identified {len(ids_to_delete)} documents for deletion.")

    if dry_run:
        print_dry_run(documents, ids_to_delete)
        return

    print("Starting deletion process...")
    deleted_count, failed_count = delete_documents(api_token, ids_to_delete)
    print_cleanup_summary(len(ids_to_delete), deleted_count, failed_count)
