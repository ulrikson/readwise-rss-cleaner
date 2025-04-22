import argparse
from typing import List, Optional, Dict, Any

from config import load_api_token, load_filters_from_json
from filtering import filter_documents
from readwise_client import delete_document, fetch_feed_documents


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Clean Readwise Reader RSS feed based on filters defined in a JSON file."
    )
    parser.add_argument(
        "--filters-file",
        type=str,
        default="filters.json",
        help="Path to the JSON file containing filter criteria (default: filters.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Identify documents to delete but do not actually delete them.",
    )
    return parser.parse_args()


def run_cleanup(
    api_token: str,
    filters: Dict[str, List[str]],
    dry_run: bool = False,
) -> None:
    """Executes the feed cleaning process based on loaded filters."""
    print("Starting Readwise Reader cleanup...")

    if not any(filters.values()):
        print("No active filters found in the configuration file. Exiting.")
        return

    try:
        documents = fetch_feed_documents(api_token)
    except Exception:  # Catch potential exceptions from the client
        print("Failed to fetch documents. Exiting.")
        return  # Exit if fetching fails

    if not documents:
        print("No documents found in the feed. Exiting.")
        return

    ids_to_delete = filter_documents(documents, filters)

    if not ids_to_delete:
        print("No documents matched the filter criteria.")
        return

    print(f"Identified {len(ids_to_delete)} documents for deletion.")

    if dry_run:
        print("Dry run enabled. No documents will be deleted.")
        print("--- Documents matching filters --- ")
        for doc in documents:
            if doc.get("id") in ids_to_delete:
                print(f"  - {doc.get('title', 'N/A')} (ID: {doc.get('id')})")
        print("----------------------------------")
        return

    deleted_count = 0
    failed_count = 0
    print("Starting deletion process...")
    for doc_id in ids_to_delete:
        if delete_document(api_token, doc_id):
            deleted_count += 1
        else:
            failed_count += 1

    print("\n--- Cleanup Summary ---")
    print(f"Documents matching filters: {len(ids_to_delete)}")
    print(f"Successfully deleted: {deleted_count}")
    if failed_count > 0:
        print(f"Failed to delete: {failed_count}")
    print("----------------------")


def main() -> None:
    """Main function to orchestrate the script."""
    args = parse_arguments()
    api_token = load_api_token()
    filters = load_filters_from_json(args.filters_file)

    if not api_token:
        print(
            "Error: Readwise API token not found."
            " Set the READWISE_API_TOKEN environment variable."
        )
        return

    run_cleanup(api_token, filters, args.dry_run)


if __name__ == "__main__":
    main()
