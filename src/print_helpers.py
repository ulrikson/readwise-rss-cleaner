from rich.console import Console
from typing import List, Dict, Any
from data_types import SaveAction

CONSOLE = Console()


def print_warning(msg: str) -> None:
    CONSOLE.print(f"[yellow]Warning: {msg}[/yellow]")


def print_error(msg: str) -> None:
    CONSOLE.print(f"[bold red]Error: {msg}[/bold red]")


def print_success(msg: str) -> None:
    CONSOLE.print(f"[bold green]Success: {msg}[/bold green]")


def print_info(msg: str) -> None:
    CONSOLE.print(f"[blue]Info:[/blue] {msg}")


def print_bold(msg: str) -> None:
    CONSOLE.print(f"[bold]{msg}[/bold]")


def print_neutral(msg: str) -> None:
    CONSOLE.print(msg)


def print_dry_run(documents: List[Dict[str, Any]], ids_to_delete: List[str]) -> None:
    print_info("Dry run enabled. No documents will be deleted.")
    print_bold("Documents flagged for deletion:")
    [
        print_neutral(f"  - {doc.get('title', 'N/A')} (ID: {doc.get('id')})")
        for doc in documents
        if doc.get("id") in ids_to_delete
    ]


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


def print_dry_run_save(
    documents: List[Dict[str, Any]], actions: List[SaveAction]
) -> None:
    """Prints the summary of actions that would be taken in a save dry run."""
    print_info("Dry run enabled. No documents will be moved.")
    print_bold("Documents flagged for location update:")
    action_map = {action.doc_id: action.location for action in actions}
    [
        print_neutral(
            f"  - {doc.get('title', 'N/A')} (ID: {doc.get('id')}) -> Move to '{action_map[doc.get('id')]}'"
        )
        for doc in documents
        if doc.get("id") in action_map
    ]


def print_save_summary(total: int, updated: int, failed: int) -> None:
    """Prints the summary after a save operation."""
    print_bold("\n--- Save Summary ---")
    print_neutral(f"Documents matching save filters: {total}")
    print_success(f"Successfully moved {updated} documents")
    if failed:
        print_error(f"Failed to move {failed} documents")
