from typing import List, Dict, Any, Optional
import json

from openai import OpenAI

from config import load_openai_api_key
from print_helpers import print_warning, print_error, print_info

MODEL_CONFIG = {
    "name": "gpt-4.1-mini",
    "input_cost_per_million": 0.40,
    "output_cost_per_million": 1.60,
}

USER_PROMPT = (
    "Below is a list of documents, each with an 'id' and a 'summary'.\n"
    "Documents: {documents}\n\n"
    "Your task is to identify which documents should be excluded based on the exclusion topics."
)

SYSTEM_PROMPT = (
    "You are an expert AI assistant for document filtering.\n"
    "You will receive a list of documents, each with an 'id' and a 'summary'.\n"
    "You will also receive a list of exclusion topics.\n\n"
    "Exclusion topics are examples of what to filter out. They may be specific (e.g., 'articles about video games other than Nintendo Switch') "
    "or general (e.g., 'artiklar om teater').\n"
    "For each document, check if its main topic matches or is closely related to any exclusion topic. "
    "Exclude documents if their summary is about, related to, or a clear example of an exclusion topic.\n\n"
    "Return a JSON object with a single key 'matching_ids', whose value is a list of document 'id' strings "
    "for all documents that should be excluded. Only include IDs that match.\n\n"
    "If no documents match, return an empty list. Do not include any explanation or extra text.\n\n"
    "Here are some example exclusion topics for reference: ['articles about video games other than Nintendo Switch', "
    "'articles about live theater and plays', 'artiklar om teater']\n"
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
        {"id": str(doc["id"]), "summary": str(doc["summary"])}
        for doc in documents
        if doc.get("id") and doc.get("summary")
    ]


def _print_usage(prompt_tokens: int, completion_tokens: int) -> None:
    input_cost = prompt_tokens * MODEL_CONFIG["input_cost_per_million"] / 1_000_000
    output_cost = (
        completion_tokens * MODEL_CONFIG["output_cost_per_million"] / 1_000_000
    )
    total_cost = input_cost + output_cost
    print_info(f"AI Topic Analysis Cost: ${total_cost:.4f}")


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
        print_warning("No documents with both id and summary found for AI analysis.")
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
