from typing import List, Dict, Any, Optional
import os
import json

from openai import OpenAI
from rich.console import Console

# Import the loader function
from config import load_openai_api_key
from print_helpers import print_warning, print_error

CONSOLE = Console()
MODEL = "gpt-4.1-mini"


def _build_prompt(
    documents: List[Dict[str, str]], exclude_topics: List[str]
) -> List[Dict[str, str]]:
    system_prompt = (
        "You are an AI assistant tasked with filtering documents based on their titles. "
        "Analyze the provided list of documents, each with an 'id' and 'title'. "
        f"Determine the main topic of each title. Compare these topics against the list of excluded topics: {exclude_topics}. "
        "Return a JSON object with a single key 'matching_ids' whose value is a list of document 'id' strings "
        "for titles whose main topic is found in the excluded topics list. Only include IDs that match. "
        "If no documents match, return an empty list. Ensure the output is valid JSON."
    )
    user_prompt = f"Here are the documents:\n{json.dumps(documents)}\n\nHere are the topics to exclude:\n{json.dumps(exclude_topics)}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _parse_openai_response(response_content: Optional[str]) -> List[str]:
    if not response_content:
        print_warning("OpenAI response content is empty.")
        return []
    try:
        data = json.loads(response_content)
        ids = data.get("matching_ids", [])
        if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
            print_warning("'matching_ids' is not a list of strings in OpenAI response.")
            return []
        return ids
    except json.JSONDecodeError:
        print_error(f"Failed to decode JSON from OpenAI response: {response_content}")
        return []


def _filter_docs_for_prompt(documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {"id": str(doc["id"]), "title": str(doc["title"])}
        for doc in documents
        if doc.get("id") and doc.get("title")
    ]


def get_filtered_document_ids_by_topic(
    documents: List[Dict[str, Any]],
    exclude_topics: List[str],
) -> List[str]:
    """
    Returns IDs of documents whose titles match excluded topics using OpenAI topic analysis.
    """
    if not exclude_topics or not documents:
        return []

    api_key = load_openai_api_key()
    if not api_key:
        print_error("OpenAI API key not found. Skipping AI analysis.")
        return []

    docs_for_prompt = _filter_docs_for_prompt(documents)
    if not docs_for_prompt:
        print_warning("No documents with both ID and Title found for AI analysis.")
        return []

    try:
        client = OpenAI(api_key=api_key)
        messages = _build_prompt(docs_for_prompt, exclude_topics)
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        response_content = response.choices[0].message.content
        return _parse_openai_response(response_content)
    except Exception as e:
        print_error(f"Unexpected error during OpenAI analysis: {e}")
        return []
