---
name: github-scraper
description: Advanced GitHub scraper for researching repositories, retrieving top hits, and extracting README contents.
---

# GitHub Scraper Skill

This skill provides an advanced GitHub scraper script located at `scripts/github_scraper.py`.

## Usage
Run the script to search GitHub and automatically download repository metadata and README contents for deep research.

```bash
python .agents/skills/github-scraper/scripts/github_scraper.py --query "quantitative finance agent" --limit 10 --output results.json
```

## Features
- **Pagination:** Fetches multiple pages if limit is high.
- **README Extraction:** Automatically attempts to fetch the raw README.md for semantic analysis.
- **Robust Error Handling:** Manages rate limits and API errors gracefully.
