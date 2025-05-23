# Readwise RSS Cleaner

## Goal

This script processes documents from a Readwise Reader feed based on filters defined in a JSON. It can perform two main actions:

1. **Cleanup:** Archive or delete documents matching certain criteria (keywords in title/URL, AI-detected topics).
2. **Save:** Save specific documents (e.g., from certain domains or authors) to the Readwise library (moving them out of the feed).

The goal is to automate the curation of the Readwise Reader feed, keeping it focused and relevant.

## Requirements

- Python 3.9
- Dependencies listed in `requirements.txt`:

    ```txt
    requests
    python-dotenv
    backoff
    urllib3==1.26.15
    rich
    python-dateutil
    openai
    tzlocal
    ```

## Configuration

The script relies on environment variables, which should be configured as **GitHub Secrets** for automated runs via GitHub Actions:

- `READWISE_API_TOKEN`: Your API token for the Readwise API.
- `GIST_ID`: The ID of the public GitHub Gist containing your filter definitions (e.g., `filters.json`). See `filters.json.example`.
  - Please note that even though your Gist is "secret," it is not private. Avoid storing sensitive information in the Gist.
- `OPENAI_API_TOKEN`: Your OpenAI API key (only required if using `ai_topic_exclude` filters).

For local development, you can create a `.env` file in the project root and define these variables there.

```.env
READWISE_API_TOKEN=your_readwise_token
GIST_ID=your_gist_id
OPENAI_API_TOKEN=your_openai_key # Optional
```

## Filters

Filtering logic is defined in a JSON file hosted on GitHub Gist (specified by `GIST_ID`). See `filters.json.example` for the structure. Filters define rules for both the `cleanup` (archive/delete) and `save` actions.

## Usage (Local)

1. **Clone the repository:**

    ```sh
    git clone https://github.com/ulrikson/readwise-rss-cleaner.git
    cd readwise-rss-cleaner
    ```

2. **(Optional) Create and activate a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Configure environment variables:** Create a `.env` file or set environment variables directly.
5. **Run the script:**

    ```sh
    python src/main.py [OPTIONS]
    ```

### Command-line Options

- `--dry-run`: Identify documents to act on but do not perform the actual cleanup or save actions.
- `--updated-after`: Only fetch documents for cleanup updated after this ISO 8601 date (e.g., `2024-01-01T10:00:00`). Defaults to 2 hours ago (configurable via `DEFAULT_HOURS_AGO` constant in `src/date_helpers.py`).

## Deployment / Scheduling

This script is configured to run periodically using GitHub Actions.

- The workflow is defined in `.github/workflows/hourly_run.yml`.
- It runs on the `ubuntu-latest` runner, sets up Python 3.9, installs dependencies from `requirements.txt`, and executes `python src/main.py`.
- Configuration (API keys, Gist ID) is pulled from GitHub Secrets.
- The workflow can also be triggered manually from the repository's "Actions" tab.
