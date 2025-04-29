import argparse
from rich.console import Console
from datetime import datetime
from typing import Optional

from cleanup import run_cleanup
from date_helpers import parse_datetime_to_utc


def _parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Clean Readwise Reader RSS feed based on filters defined in a JSON file."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Identify documents to delete but do not actually delete them.",
    )
    parser.add_argument(
        "--updated-after",
        type=str,
        default=None,
        help="Only fetch documents updated after this ISO 8601 date (default: today at 00:00)",
    )
    return parser.parse_args()


def _parse_updated_after(updated_after: Optional[str]) -> str:
    """Parse the updatedAfter argument and convert to UTC."""
    date = (
        updated_after
        or datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    )
    return parse_datetime_to_utc(date)


def main() -> None:
    """Main function to orchestrate the script."""
    args = _parse_arguments()
    updated_after = _parse_updated_after(args.updated_after)

    run_cleanup(args.dry_run, updated_after)


if __name__ == "__main__":
    main()
