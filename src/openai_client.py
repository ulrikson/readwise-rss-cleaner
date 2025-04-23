from typing import List, Dict, Any, Optional
import os
import json

from openai import OpenAI, APIError, RateLimitError
from rich.console import Console


CONSOLE = Console()
MODEL = "gpt-4o-mini"  # Or specify gpt-4.1-mini if available via API


def _build_prompt(
    documents_json: str, exclude_topics_json: str
) -> List[Dict[str, str]]:
    """Builds the prompt messages for the OpenAI API call."""
    system_prompt = (
        "You are an AI assistant tasked with filtering documents based on their titles. "
        "Analyze the provided list of documents, each with an 'id' and 'title'. "
        f"Determine the main topic of each title. Compare these topics against the list of excluded topics: {exclude_topics_json}. "
        "Return a JSON object containing a single key 'matching_ids' whose value is a list of document 'id' strings "
        "for titles whose main topic is found in the excluded topics list. Only include IDs that match. "
        "If no documents match, return an empty list. Ensure the output is valid JSON."
    )
    user_prompt = f"Here are the documents:\n{documents_json}\n\nHere are the topics to exclude:\n{exclude_topics_json}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _parse_openai_response(response_content: Optional[str]) -> List[str]:
    """Parses the JSON response from OpenAI and validates the structure."""
    if not response_content:
        CONSOLE.print("[yellow]Warning:[/yellow] OpenAI response content is empty.")
        return []

    try:
        data = json.loads(response_content)
        if not isinstance(data, dict) or "matching_ids" not in data:
            CONSOLE.print(
                f"[yellow]Warning:[/yellow] Unexpected JSON structure from OpenAI: {response_content}"
            )
            return []

        matching_ids = data["matching_ids"]
        if not isinstance(matching_ids, list) or not all(
            isinstance(item, str) for item in matching_ids
        ):
            CONSOLE.print(
                f"[yellow]Warning:[/yellow] 'matching_ids' is not a list of strings in OpenAI response: {matching_ids}"
            )
            return []

        return matching_ids
    except json.JSONDecodeError:
        CONSOLE.print(
            f"[bold red]Error:[/bold red] Failed to decode JSON from OpenAI response: {response_content}"
        )
        return []


def get_filtered_document_ids_by_topic(
    openai_api_key: str,
    documents: List[Dict[str, Any]],
    exclude_topics: List[str],
) -> List[str]:
    """
    Analyzes document titles using OpenAI to identify topics and returns IDs of documents
    matching the exclude_topics list.

    Args:
        openai_api_key: The OpenAI API key.
        documents: A list of documents (dictionaries), each must have 'id' and 'title'.
        exclude_topics: A list of topics to filter out.

    Returns:
        A list of document IDs whose titles match the excluded topics.
    """
    if not exclude_topics or not documents:
        return []

    # Prepare documents for the prompt (only id and title)
    docs_for_prompt = [
        {"id": doc.get("id"), "title": doc.get("title")}
        for doc in documents
        if doc.get("id") and doc.get("title")  # Ensure required fields exist
    ]

    if not docs_for_prompt:
        CONSOLE.print(
            "[yellow]Warning:[/yellow] No documents with both ID and Title found for AI analysis."
        )
        return []

    try:
        client = OpenAI(api_key=openai_api_key)
        messages = _build_prompt(
            json.dumps(docs_for_prompt), json.dumps(exclude_topics)
        )

        CONSOLE.print(
            f"[INFO] Sending {len(docs_for_prompt)} document titles to {MODEL} for topic analysis..."
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,  # Lower temperature for more deterministic topic analysis
            response_format={"type": "json_object"},  # Request JSON output
        )

        response_content = response.choices[0].message.content
        print(response_content)
        filtered_ids = _parse_openai_response(response_content)

        CONSOLE.print(
            f"[INFO] OpenAI analysis complete. Found {len(filtered_ids)} documents matching excluded topics."
        )
        return filtered_ids

    except RateLimitError as e:
        CONSOLE.print(
            f"[bold red]Error:[/bold red] OpenAI rate limit exceeded: {e}. Skipping AI analysis."
        )
        return []
    except APIError as e:
        CONSOLE.print(
            f"[bold red]Error:[/bold red] OpenAI API error: {e}. Skipping AI analysis."
        )
        return []
    except Exception as e:
        CONSOLE.print(
            f"[bold red]Error:[/bold red] An unexpected error occurred during OpenAI analysis: {e}"
        )
        return []
