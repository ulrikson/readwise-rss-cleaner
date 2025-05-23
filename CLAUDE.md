# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

**Setup:**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run the application:**

```bash
python src/main.py                                    # Process today's documents
python src/main.py --dry-run                         # Preview actions without execution
python src/main.py --updated-after "2024-01-01T10:00:00"  # Process from specific date
```

**Testing:** No formal test framework is configured. Manual testing is done via `--dry-run` flag.

## Architecture Overview

This is a Readwise Reader feed automation tool with a **dual-workflow architecture**:

**Main Flow:**

1. **main.py** orchestrates: loads filters from GitHub Gist → fetches documents from Readwise API → runs cleanup + save workflows
2. **cleanup.py** identifies and deletes documents matching exclude filters
3. **save.py** moves documents to specific Readwise locations based on save filters

**Filtering System:**

- **Standard filters** (filtering.py): Keyword matching on title/URL/author
- **AI filters** (openai_client.py): Topic-based analysis using OpenAI GPT
- Both operate independently and can be combined

**Key Components:**

- **readwise_client.py**: API abstraction with exponential backoff retry logic
- **github_gist_client.py**: Loads filter configuration from public GitHub Gist
- **data_types.py**: Type definitions for FilterConfig and SaveAction
- **config.py**: Environment variable loading and default configurations

**Data Flow:**

```
GitHub Gist → Filter Config → Document Processing → API Updates
           ↗ Standard Filters ↘
Documents → ← AI Analysis ← → Readwise API Actions
```

## Configuration

**Environment Variables:**

- `READWISE_API_TOKEN`: Required for all operations
- `GIST_ID`: Required - GitHub Gist ID containing filter JSON
- `OPENAI_API_TOKEN`: Optional - only needed for `ai_topic_exclude` filters

**Filter Structure** (from GitHub Gist):

```json
{
  "title_exclude": ["keyword"],
  "url_exclude": ["domain.com"],
  "ai_topic_exclude": ["topic description"],
  "author_save_inbox": ["author"],
  "author_save_later": ["author"]
}
```

## Development Notes

- All API calls use exponential backoff with configurable retry attempts
- Dry-run capability is available throughout the entire pipeline
- Error handling follows continue-on-failure pattern - individual document failures don't stop processing
- The application is designed for automated execution via GitHub Actions (hourly schedule)
