import argparse
from typing import Optional

from github_gist_client import load_filters
from cleanup import run_cleanup
from save import run_save
from date_helpers import parse_datetime_to_utc, get_start_of_yesterday


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
        help="Only fetch documents updated after this ISO 8601 date (default: yesterday at 00:00)",
    )
    return parser.parse_args()


def _parse_updated_after(updated_after: Optional[str]) -> str:
    """Parse the updatedAfter argument and convert to UTC."""
    date = updated_after or get_start_of_yesterday()
    return parse_datetime_to_utc(date)


def main() -> None:
    """Main function to orchestrate the script."""
    args = _parse_arguments()
    updated_after = _parse_updated_after(args.updated_after)
    filters = load_filters()

    run_cleanup(filters, args.dry_run, updated_after)
    print()
    run_save(filters, args.dry_run)


if __name__ == "__main__":
    main()
