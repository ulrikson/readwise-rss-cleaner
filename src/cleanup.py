from typing import List, Optional, Dict, Any, Tuple, Set
from filtering import filter_documents
from readwise_client import delete_document, fetch_feed_documents
from openai_client import get_filtered_document_ids_by_topic
from rich.console import Console


def has_active_filters(filters: Dict[str, List[str]]) -> bool:
    return any(filters.get(key, []) for key in filters)


def fetch_documents(
    api_token: str, updated_after: str
) -> Optional[List[Dict[str, Any]]]:
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


def print_cleanup_summary(
    total: int, deleted: int, failed: int, from_ai: int = 0
) -> None:
    Console().print("\n[bold]--- Cleanup Summary ---[/bold]")
    Console().print(f"Documents matching filters: {total}")
    if from_ai > 0:
        Console().print(f"  (Including {from_ai} identified by AI topic filter)")
    Console().print(f"[green]Successfully deleted: {deleted}[/green]")
    if failed > 0:
        Console().print(f"[bold red]Failed to delete: {failed}[/bold red]")


def run_cleanup(
    api_token: str,
    filters: Dict[str, List[str]],
    dry_run: bool = False,
    updated_after: str = "",
    openai_api_key: Optional[str] = None,
) -> None:
    Console().print("[bold]Starting Readwise Reader cleanup...[/bold]")

    ai_exclude_topics = filters.get("ai_topic_exclude", [])

    standard_filters = {k: v for k, v in filters.items() if k != "ai_topic_exclude"}

    if not has_active_filters(standard_filters) and not ai_exclude_topics:
        Console().print(
            "[yellow]No active filters (standard or AI) found. Exiting.[/yellow]"
        )
        return

    documents = fetch_documents(api_token, updated_after)
    if documents is None or not documents:
        Console().print("[bold red]Failed to fetch documents. Exiting.[/bold red]")
        return

    standard_filtered_ids: Set[str] = set(filter_documents(documents, standard_filters))
    Console().print(
        f"[cyan]Identified {len(standard_filtered_ids)} documents based on standard filters.[/cyan]"
    )

    ai_filtered_ids: Set[str] = set()
    if openai_api_key and ai_exclude_topics:
        Console().print("[cyan]Running AI topic analysis...[/cyan]")
        ai_filtered_ids = set(
            get_filtered_document_ids_by_topic(
                openai_api_key, documents, ai_exclude_topics
            )
        )
        Console().print(
            f"[cyan]Identified {len(ai_filtered_ids)} documents based on AI topic filters.[/cyan]"
        )
    elif ai_exclude_topics:
        Console().print(
            "[yellow]AI topic filters found, but OPENAI_API_KEY is not set. Skipping AI analysis.[/yellow]"
        )

    all_ids_to_delete: Set[str] = standard_filtered_ids.union(ai_filtered_ids)

    if not all_ids_to_delete:
        Console().print("[yellow]No documents matched any filter criteria.[/yellow]")
        return

    ids_to_delete_list = list(all_ids_to_delete)
    Console().print(
        f"[cyan]Total unique documents identified for deletion: {len(ids_to_delete_list)}[/cyan]"
    )

    if dry_run:
        print_dry_run(documents, ids_to_delete_list)
        return

    Console().print("[bold]Starting deletion process...[/bold]")
    deleted_count, failed_count = delete_documents(api_token, ids_to_delete_list)
    print_cleanup_summary(
        len(ids_to_delete_list), deleted_count, failed_count, len(ai_filtered_ids)
    )
