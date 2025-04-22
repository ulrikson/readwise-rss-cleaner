from typing import List, Optional, Dict, Any, Tuple
from filtering import filter_documents
from readwise_client import delete_document, fetch_feed_documents
from rich.console import Console


def has_active_filters(filters: Dict[str, List[str]]) -> bool:
    return any(filters.values())


def fetch_documents(api_token: str, updated_after: str) -> Optional[List[Dict[str, Any]]]:
    try:
        return fetch_feed_documents(api_token, updated_after)
    except Exception:
        Console().print("[bold red]Failed to fetch documents. Exiting.[/bold red]")
        return None


def print_dry_run(documents: List[Dict[str, Any]], ids_to_delete: List[str]) -> None:
    Console().print("[yellow]Dry run enabled. No documents will be deleted.[/yellow]")
    for doc in documents:
        if doc.get("id") in ids_to_delete:
            Console().print(f"  - {doc.get('title', 'N/A')} (ID: {doc.get('id')})")


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
    Console().print("\n[bold]--- Cleanup Summary ---[/bold]")
    Console().print(f"Documents matching filters: {total}")
    Console().print(f"[green]Successfully deleted: {deleted}[/green]")
    if failed > 0:
        Console().print(f"[bold red]Failed to delete: {failed}[/bold red]")


def run_cleanup(
    api_token: str, filters: Dict[str, List[str]], dry_run: bool = False, updated_after: str = ""
) -> None:
    Console().print("[bold]Starting Readwise Reader cleanup...[/bold]")

    if not has_active_filters(filters):
        Console().print(
            "[yellow]No active filters found in the configuration file. Exiting.[/yellow]"
        )
        return

    documents = fetch_documents(api_token, updated_after)
    if documents is None or not documents:
        Console().print("[bold red]Failed to fetch documents. Exiting.[/bold red]")
        return

    ids_to_delete = filter_documents(documents, filters)
    if not ids_to_delete:
        Console().print("[yellow]No documents matched the filter criteria.[/yellow]")
        return

    Console().print(
        f"[cyan]Identified {len(ids_to_delete)} documents for deletion.[/cyan]"
    )

    if dry_run:
        print_dry_run(documents, ids_to_delete)
        return

    Console().print("[bold]Starting deletion process...[/bold]")
    deleted_count, failed_count = delete_documents(api_token, ids_to_delete)
    print_cleanup_summary(len(ids_to_delete), deleted_count, failed_count)
