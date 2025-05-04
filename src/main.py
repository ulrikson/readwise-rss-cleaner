import argparse
from typing import Optional, Dict, List, Any

from github_gist_client import load_filters
from cleanup import run_cleanup
from save import run_save
from date_helpers import parse_datetime_to_utc, get_default_updated_after
from readwise_client import fetch_feed_documents
from print_helpers import print_error


def _parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Clean and save Readwise Reader feed items based on filters from a GitHub gist."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Identify documents to act on but do not actually perform the action.",
    )
    parser.add_argument(
        "--updated-after",
        type=str,
        default=None,
        help="Only fetch documents updated after this ISO 8601 date",
    )
    return parser.parse_args()


def _parse_updated_after(updated_after: Optional[str]) -> str:
    """Parse the updatedAfter argument and convert to UTC."""
    date = updated_after or get_default_updated_after()
    return parse_datetime_to_utc(date)


def _get_filters() -> Dict[str, List[str]]:
    """Get filters from the GitHub gist."""
    try:
        return load_filters()
    except Exception as e:
        print_error(f"Error loading filters: {e}")
        return {}


def _get_documents(updated_after: str) -> List[Dict[str, Any]]:
    """Get documents from the Readwise Reader API."""
    try:
        return fetch_feed_documents(updated_after)
    except Exception as e:
        print_error(f"Error fetching documents: {e}")
        return []


def main() -> None:
    """Main function to orchestrate the script."""
    args = _parse_arguments()
    updated_after = _parse_updated_after(args.updated_after)

    if not (filters := _get_filters()):
        print_error("Cannot proceed - no valid filters found")
        return

    if not (documents := _get_documents(updated_after)):
        print_error("Cannot proceed - no documents found")
        return

    run_cleanup(documents, filters, args.dry_run)
    print()
    run_save(documents, filters, args.dry_run)


if __name__ == "__main__":
    main()
