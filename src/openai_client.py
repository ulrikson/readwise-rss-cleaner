from typing import List, Dict, Any, Optional
import json

from openai import OpenAI

from config import load_openai_api_key
from print_helpers import print_warning, print_error, print_neutral

MODEL_CONFIG = {
    "name": "gpt-4.1-mini",
    "input_cost_per_million": 0.40,
    "output_cost_per_million": 1.60,
}

USER_PROMPT = "Here are the documents:\n{documents}\n\nHere are the topics to exclude:\n{exclude_topics}"

SYSTEM_PROMPT = (
    "You are an AI assistant tasked with filtering documents based on their titles. "
    "Analyze the provided list of documents, each with an 'id' and 'title'. "
    "This is a list of topics to exclude: {exclude_topics}. Compare the topics of the documents against the list of excluded topics. "
    "Return a JSON object with a single key 'matching_ids' whose value is a list of document 'id' strings "
    "for titles whose main topic is found in the excluded topics list. Only include IDs that match. "
)


def _build_prompt(
    documents: List[Dict[str, str]], exclude_topics: List[str]
) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(exclude_topics=exclude_topics),
        },
        {
            "role": "user",
            "content": USER_PROMPT.format(
                documents=documents, exclude_topics=exclude_topics
            ),
        },
    ]


def _handle_invalid_response() -> List[str]:
    print_warning("'matching_ids' is not a list of strings in OpenAI response.")
    return []


def _parse_openai_response(response_content: Optional[str]) -> List[str]:
    if not response_content:
        print_warning("OpenAI response content is empty.")
        return []
    try:
        ids = json.loads(response_content).get("matching_ids", [])
        return (
            ids
            if isinstance(ids, list) and all(isinstance(i, str) for i in ids)
            else _handle_invalid_response()
        )
    except json.JSONDecodeError:
        print_error(f"Failed to decode JSON from OpenAI response: {response_content}")
        return []


def _filter_docs_for_prompt(documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {"id": str(doc["id"]), "title": str(doc["title"])}
        for doc in documents
        if doc.get("id") and doc.get("title")
    ]


def _print_usage(prompt_tokens: int, completion_tokens: int) -> None:
    input_cost = prompt_tokens * MODEL_CONFIG["input_cost_per_million"] / 1_000_000
    output_cost = (
        completion_tokens * MODEL_CONFIG["output_cost_per_million"] / 1_000_000
    )
    total_cost = input_cost + output_cost
    print_neutral(
        f"      Input tokens: {prompt_tokens}, Output tokens: {completion_tokens}, Cost: ${total_cost:.4f} (input: ${input_cost:.4f}, output: ${output_cost:.4f})"
    )


def filter_by_topic(
    documents: List[Dict[str, Any]], exclude_topics: List[str]
) -> List[str]:
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
        response = client.chat.completions.create(
            model=MODEL_CONFIG["name"],
            messages=_build_prompt(docs_for_prompt, exclude_topics),
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        _print_usage(response.usage.prompt_tokens, response.usage.completion_tokens)
        return _parse_openai_response(response.choices[0].message.content)
    except Exception as e:
        print_error(f"Unexpected error during OpenAI analysis: {e}")
        return []
