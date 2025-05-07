from typing import List, Dict, Any, Optional
import json

from openai import OpenAI

from config import load_openai_api_key, USER_PROMPT, SYSTEM_PROMPT
from print_helpers import print_warning, print_error, print_info

MODEL_CONFIG = {
    "name": "gpt-4.1-mini",
    "input_cost_per_million": 0.40,
    "output_cost_per_million": 1.60,
}


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
    api_key = load_openai_api_key()
    docs_for_prompt = _filter_docs_for_prompt(documents)

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
