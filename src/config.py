import os
import json
from typing import Optional, Dict, List, Any
import requests

from dotenv import load_dotenv
from print_helpers import print_warning

load_dotenv(override=True)

DEFAULT_FILTERS = {
    "title_exclude": [],
    "url_exclude": [],
    "ai_topic_exclude": [],
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


def load_readwise_api_token() -> str:
    """Loads the Readwise API token from environment variables."""
    token = os.getenv("READWISE_API_TOKEN")
    if not token:
        raise ValueError("READWISE_API_TOKEN environment variable is not set")
    return token


def load_openai_api_key() -> Optional[str]:
    """Loads the OpenAI API key from environment variables."""
    return os.getenv("OPENAI_API_TOKEN")


def load_gist_id() -> str:
    """Loads the GitHub Gist ID from environment variables."""
    gist_id = os.getenv("GIST_ID")
    if not gist_id:
        raise ValueError("GIST_ID environment variable is not set")
    return gist_id
