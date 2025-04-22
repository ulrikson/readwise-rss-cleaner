import argparse
from rich.console import Console
from datetime import datetime, timedelta
from dateutil import parser as date_parser

from config import load_api_token, load_filters_from_json
from cleanup import run_cleanup


def _parse_arguments() -> argparse.Namespace:
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
    parser.add_argument(
        "--updated-after",
        type=str,
        default=None,
        help="Only fetch documents updated after this ISO 8601 date (default: today at 00:00)",
    )
    return parser.parse_args()


def _parse_updated_after(updated_after: str) -> str:
    """Parse the updatedAfter argument and convert to UTC. Assume input is in UTC+2."""
    if updated_after:
        local_dt = date_parser.parse(updated_after)
    else:
        now = datetime.now()
        local_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Subtract 2 hours to get UTC
    utc_dt = local_dt - timedelta(hours=2)
    return utc_dt.isoformat()


def main() -> None:
    """Main function to orchestrate the script."""
    args = _parse_arguments()
    updated_after = _parse_updated_after(args.updated_after)
    api_token = load_api_token()
    filters = load_filters_from_json(args.filters_file)
    if not api_token:
        Console().print(
            "[bold red]Error:[/bold red] Readwise API token not found. Set the READWISE_API_TOKEN environment variable."
        )
        return
    run_cleanup(api_token, filters, args.dry_run, updated_after)


if __name__ == "__main__":
    main()
