import argparse
from rich.console import Console
from datetime import datetime
from typing import Optional

from config import load_api_token, load_filters_from_json, load_openai_api_key
from cleanup import run_cleanup
from date_helpers import parse_datetime_to_utc


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
    readwise_api_token = load_api_token()
    openai_api_key = load_openai_api_key()
    filters = load_filters_from_json(args.filters_file)

    if not readwise_api_token:
        Console().print(
            "[bold red]Error:[/bold red] Readwise API token not found. Set the READWISE_API_TOKEN environment variable."
        )
        return

    if filters.get("ai_topic_exclude") and not openai_api_key:
        Console().print(
            "[bold yellow]Warning:[/bold yellow] AI topic filters are defined, but OpenAI API key not found. Set the OPENAI_API_KEY environment variable to enable AI filtering."
        )

    run_cleanup(
        readwise_api_token, filters, args.dry_run, updated_after, openai_api_key
    )


if __name__ == "__main__":
    main()
