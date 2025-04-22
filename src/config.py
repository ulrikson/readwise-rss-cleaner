import os
from typing import Optional

from dotenv import load_dotenv


def load_api_token() -> Optional[str]:
    """Loads the Readwise API token from environment variables.

    Returns:
        The API token if found, otherwise None.
    """
    load_dotenv()  # Load variables from .env file
    return os.getenv("READWISE_API_TOKEN") 