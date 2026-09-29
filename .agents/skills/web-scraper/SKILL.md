---
name: web-scraper
description: Advanced Web scraper for extracting textual content, metadata, and hyperlinks from any URL.
---

# Web Scraper Skill

This skill provides a highly robust web scraping script located at `scripts/web_scraper.py`.

## Usage
Run the script to extract content from a website for deep analysis. It parses HTML, removes boilerplate, and extracts clean markdown-like text.

```bash
python .agents/skills/web-scraper/scripts/web_scraper.py --url "https://example.com" --output content.json
```

## Features
- **Clean Text Extraction:** Uses BeautifulSoup to strip scripts, styles, and navigational elements.
- **Link Extraction:** Compiles all outgoing hyperlinks for recursive research.
- **Metadata:** Extracts title and meta descriptions.
