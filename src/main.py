import argparse
from rich.console import Console

from config import load_api_token, load_filters_from_json
from cleanup import run_cleanup


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


def main() -> None:
    """Main function to orchestrate the script."""
    args = parse_arguments()
    api_token = load_api_token()
    filters = load_filters_from_json(args.filters_file)
    if not api_token:
        Console().print(
            "[bold red]Error:[/bold red] Readwise API token not found. Set the READWISE_API_TOKEN environment variable."
        )
        return
    run_cleanup(api_token, filters, args.dry_run)


if __name__ == "__main__":
    main()
