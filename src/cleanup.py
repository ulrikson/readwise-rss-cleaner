from typing import List, Optional, Dict, Any, Tuple, Set
from filtering import filter_documents
from readwise_client import delete_document, fetch_feed_documents
from openai_client import get_filtered_document_ids_by_topic
from rich.console import Console


def has_active_filters(filters: Dict[str, List[str]]) -> bool:
    return any(filters.get(key, []) for key in filters)


def fetch_documents(updated_after: str) -> Optional[List[Dict[str, Any]]]:
    try:
        return fetch_feed_documents(updated_after)
    except Exception as e:
        Console().print(
            f"[bold red]Failed to fetch documents: {e}. Exiting.[/bold red]"
        )
        return None


def print_dry_run(documents: List[Dict[str, Any]], ids_to_delete: List[str]) -> None:
    Console().print("[yellow]Dry run enabled. No documents will be deleted.[/yellow]")
    for doc in documents:
        if doc.get("id") in ids_to_delete:
            Console().print(f"  - {doc.get('title', 'N/A')} (ID: {doc.get('id')})")


def delete_documents(ids_to_delete: List[str]) -> Tuple[int, int]:
    deleted_count = 0
    failed_count = 0
    for doc_id in ids_to_delete:  # todo: try-catch?
        if delete_document(doc_id):
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


def _extract_filter_types(
    filters: Dict[str, List[str]],
) -> Tuple[Dict[str, List[str]], List[str]]:
    ai_exclude_topics = filters.get("ai_topic_exclude", [])
    standard_filters = {k: v for k, v in filters.items() if k != "ai_topic_exclude"}
    return standard_filters, ai_exclude_topics


def _apply_standard_filters(
    documents: List[Dict[str, Any]], standard_filters: Dict[str, List[str]]
) -> Set[str]:
    if not has_active_filters(standard_filters):
        return set()
    return set(filter_documents(documents, standard_filters))


def _apply_ai_filters(
    documents: List[Dict[str, Any]], ai_exclude_topics: List[str]
) -> Set[str]:
    try:
        return set(get_filtered_document_ids_by_topic(documents, ai_exclude_topics))
    except Exception as e:
        Console().print(f"[bold red]AI topic analysis failed: {e}[/bold red]")
        return set()


def _handle_no_documents_found(documents: Optional[List[Dict[str, Any]]]) -> bool:
    if documents is None or not documents:
        Console().print(
            "[yellow]No documents found matching the updated_after criteria.[/yellow]"
        )
        return True
    return False


def _handle_no_matches(all_ids_to_delete: Set[str]) -> bool:
    if not all_ids_to_delete:
        Console().print("[yellow]No documents matched any filter criteria.[/yellow]")
        return True
    return False


def run_cleanup(
    filters: Dict[str, List[str]],
    dry_run: bool = False,
    updated_after: str = "",
) -> None:
    console = Console()
    console.print("[bold]Starting Readwise Reader cleanup...[/bold]")

    standard_filters, ai_exclude_topics = _extract_filter_types(filters)

    if not has_active_filters(standard_filters) and not ai_exclude_topics:
        console.print("[yellow]No active filters found. Exiting.[/yellow]")
        return

    documents = fetch_documents(updated_after)
    if _handle_no_documents_found(documents):
        return
    documents = documents or []

    standard_filtered_ids = _apply_standard_filters(documents, standard_filters)
    ai_filtered_ids = _apply_ai_filters(documents, ai_exclude_topics)
    all_ids_to_delete: Set[str] = standard_filtered_ids.union(ai_filtered_ids)

    if _handle_no_matches(all_ids_to_delete):
        return

    ids_to_delete_list = list(all_ids_to_delete)

    if dry_run:
        print_dry_run(documents, ids_to_delete_list)
        return

    deleted_count, failed_count = delete_documents(ids_to_delete_list)
    print_cleanup_summary(
        len(ids_to_delete_list), deleted_count, failed_count, len(ai_filtered_ids)
    )
