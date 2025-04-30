# Readwise RSS Cleaner

## My Goal

I use Readwise Reader to collect articles from the web. Some sources are better than others. As of now, Readwise Reader has no filter for articles in a source. You can only filter sources into folders.

The main idea is simple:

- Fetch all documents from my Readwise Reader feed.
- Filter them based on keywords in the title, URL, or by using AI to exclude certain topics.
- Optionally, just preview what would be deleted (dry run), or actually delete the matching documents.

This helps keep my reading list focused and relevant, without manual curation.

## ToDos and Known Issues

- [ ] Database support instead of just a JSON file
- [ ] Combined filters, e.g. only delete if title contains X and URL contains Y

## Getting Started

### Prerequisites

- Python 3.9+
- Environment variables set for API keys:
  - `READWISE_API_TOKEN` for Readwise API access
  - `OPENAI_API_KEY` for AI topic filtering (optional, only needed for `ai_topic_exclude`)

### Installation

Clone the repository:

```sh
git clone https://github.com/ulrikson/readwise-rss-cleaner.git
cd readwise-rss-cleaner
```

(Optional) Create and activate a virtual environment:

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the required dependencies:

```sh
pip install -r requirements.txt
```

Create a `.env` file in the root directory and add your API keys:

```.env
READWISE_API_TOKEN=your_readwise_api_token_here
OPENAI_API_KEY=your_openai_api_key_here  # Only needed for AI topic filtering
```

## Configuration

Create a `filters.json` file in the root directory (or copy and modify `filters.json.example`).

## Usage

Run the main script to start the cleanup process:

```sh
python src/main.py
```

### Options

- `--dry-run`: Preview which documents would be deleted, but don't actually delete them.
- `--updated-after`: Only fetch documents updated after this ISO 8601 date (default: today at 00:00)

Example (dry run):

```sh
python src/main.py --dry-run
```

Example (updated after):

```sh
python src/main.py --updatedAfter 2025-01-01T00:00:00
```
