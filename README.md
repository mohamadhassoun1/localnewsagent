# LocalNewsAgent - Autonomous Local News Publishing System

A Python-based autonomous publishing agent that runs entirely locally on your machine. Discovers trending topics, extracts factual information from news sources, generates 100% original long-form articles (800–1600 words), performs QA checks, and saves publish-ready JSON drafts with full SEO metadata.

## ✨ Features

- **🔍 Multi-Source Discovery**: RSS feeds, site crawlers, DuckDuckGo SERP scraping (no APIs)
- **📰 Fact Extraction**: Automatic bullet point extraction, paywall detection, rewritten excerpts
- **✍️ Article Generation**: Local LLM (gpt4all/Ollama) with intelligent fallback to rule-based synthesis
- **📊 SEO-Ready**: Generates titles, meta descriptions, keywords, tags, image prompts
- **✅ Quality Assurance**: Word count validation, plagiarism check (20-char threshold), AdSense safety checks
- **💾 Publish-Ready Output**: JSON drafts + standalone HTML files + detailed session logs
- **🛡️ 100% Local**: No external APIs, no cloud dependencies, runs on your laptop

## 📦 Installation

### 1. Clone / Setup

```bash
cd c:\Users\moham\Desktop\blog
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Install Local LLM

For article generation with a local language model:

```bash
# Option A: gpt4all (recommended, easiest)
pip install gpt4all

# Option B: Ollama (more control)
# Download from https://ollama.ai
# Then: ollama pull orca-mini
```

## ⚙️ Configuration

### RSS Feeds (`rss_feeds.txt`)

Add RSS feed URLs, one per line:

```
https://news.ycombinator.com/rss
https://feeds.theverge.com/theverge/index.xml
https://arstechnica.com/feed
```

### Site URLs (`sites.txt`)

Base URLs to crawl for RSS/feeds:

```
https://www.theverge.com
https://arstechnica.com
https://techcrunch.com
```

Agent will attempt: `/rss`, `/feed`, `/feeds`, `/feed.xml`

## 🚀 Usage

### Basic Run

```bash
python main.py
```

Processes top 3 trending topics (default).

### Advanced Options

```bash
# Process top 5 topics with 1000 minimum words
python main.py --top-topics 5 --min-words 1000

# Use fallback generation (skip local LLM)
python main.py --no-llm

# Add custom search queries
python main.py --queries "AI breakthroughs" "blockchain news"

# Custom config files
python main.py --rss-file my_feeds.txt --sites-file my_sites.txt
```

## 📁 Output Structure

```
blog/
├── drafts/                    # Publish-ready articles
│   ├── slug__20250117_120000.json     # JSON with all metadata
│   ├── slug.html                      # Standalone HTML page
│   └── ...
├── logs/                      # Session logs
│   ├── session_20250117_120000.log
│   └── slug.log               # Per-article detailed log
├── published/                 # Published articles (manual move)
│   └── slug__20250117_120000_published.json
├── src/                       # Source modules
│   ├── __init__.py
│   ├── discovery.py           # Topic discovery
│   ├── extractor.py           # Fact extraction
│   ├── composer.py            # Article generation
│   ├── qa.py                  # QA validation
│   └── output.py              # File I/O
├── main.py                    # CLI orchestrator
├── rss_feeds.txt              # RSS feed URLs
├── sites.txt                  # Site URLs to crawl
└── requirements.txt           # Python dependencies
```

## 🔄 Workflow (A → F)

### A. Discovery
- Fetches configured RSS feeds
- Crawls sites for /rss, /feed endpoints
- Optionally scrapes DuckDuckGo results
- Builds topic list sorted by trend score

### B. Extraction
- Fetches article content from source URLs
- Detects paywalls and skips paywalled content
- Extracts 5-12 bullet facts (<=25 words each)
- Rewrites excerpts (original phrasing, <=20 char copying limit)

### C. Composition
- **Preferred**: Uses local LLM (gpt4all/Ollama) if available
- **Fallback**: Rule-based article generation using templates
- Generates 800-1600 word article with:
  - Professional magazine-style voice
  - Structured HTML (h2, p, ul/li tags)
  - Internal link placeholders (/tag/*, /category/*)
  - "Our take:" analysis statement

### D. SEO & Image Prompts
- **SEO Title**: ≤60 chars, keyword-rich
- **Meta Description**: 120-155 chars
- **Keywords**: 8-12 items
- **Tags**: 5-8 category tags
- **Image Prompts**: 3 variations (16:9, no logos/faces)
- **Alt Text**: ≤120 chars

### E. QA & Validation
- Minimum word count check (default: 800)
- Plagiarism detection (flags 20+ char matches from sources)
- AdSense safety checks (blocks adult, violent, hateful, medical/financial advice content)
- Structural validation ("Our take:" + Sources section required)
- Auto-regenerates on failure (up to 2 retries)

### F. Output & Publishing
- Saves publish-ready JSON to `./drafts/{slug}__{timestamp}.json`
- Generates standalone HTML to `./drafts/{slug}.html`
- Creates detailed session log to `./logs/{slug}.log`
- Lists all saved files

## 📋 JSON Output Format

```json
{
  "title": "AI Breakthroughs Reshape Industry Standards",
  "article_html": "<h1>...</h1><p>...</p>...",
  "summary": "Recent advances in machine learning...",
  "word_count": 1245,
  "tags": ["ai", "tech", "machine-learning", "industry"],
  "slug": "ai-breakthroughs-reshape-industry",
  "seo_title": "AI Breakthroughs Reshape Industry Standards | Tech News",
  "meta_description": "Explore how recent AI advances are transforming...",
  "keywords": ["ai", "machine learning", "tech news", "industry trends"],
  "image_prompt_main": "16:9 abstract visualization of neural networks...",
  "image_prompt_alt1": "Modern tech aesthetic with AI concepts...",
  "image_prompt_alt2": "Digital innovation landscape...",
  "alt_text": "Illustration of AI breakthroughs",
  "sources": [
    {"name": "TechCrunch", "url": "https://techcrunch.com/..."},
    {"name": "The Verge", "url": "https://theverge.com/..."}
  ],
  "cta": "Subscribe for daily updates on tech and AI.",
  "our_take": "This development signals a major shift in how the industry approaches machine learning.",
  "published_at": "2025-01-17T12:00:00.000000"
}
```

## 🛡️ Safety & Compliance

### Copyright Protection
- ✅ Never copies >20 consecutive characters from sources
- ✅ Paraphrases and expands all content
- ✅ Avoids reproducing full-text paywalled content
- ✅ Includes Sources section for attribution

### AdSense Compliance
- ✅ Blocks adult, violent, hateful content
- ✅ Prevents medical/financial advice claims
- ✅ Filters disallowed terms (viagra, casino, etc.)
- ✅ Safe for ad monetization

### Transparent Logging
- ✅ Detailed session logs track all steps
- ✅ Sources recorded for each article
- ✅ QA failures documented for review

## 🎯 Example Workflow

```bash
# 1. Configure feeds
echo "https://news.ycombinator.com/rss" >> rss_feeds.txt

# 2. Run discovery → extraction → composition → QA → output
python main.py --top-topics 3 --min-words 800

# 3. Check drafts
ls -la drafts/

# 4. Review article
cat drafts/slug__timestamp.json

# 5. (Manual) Publish when ready
# cp drafts/slug__*.json published/
```

## 🔧 Advanced: Custom LLM Setup

### Using Ollama

```bash
# Install Ollama from https://ollama.ai

# Pull a model
ollama pull orca-mini

# Start Ollama server
ollama serve

# In another terminal, run agent
python main.py
```

### Supported Models

- **gpt4all**: orca-mini, mistral, neural-chat, etc.
- **Ollama**: orca-mini, llama2, mistral, neural-chat, dolphin-mixtral, etc.

## 📊 Logging & Debugging

All activity logged to:
- `./logs/session_{timestamp}.log` - Full session transcript
- `./logs/{slug}.log` - Per-article details

Enable verbose output:

```bash
# Already enabled by default; check logs/ folder
```

## ⚖️ License & Attribution

This system respects copyright and includes proper source attribution. Always:
1. Paraphrase content (no >20 char copies)
2. Include Sources section
3. Use only publicly available sources
4. Respect robots.txt and terms of service

## 🤝 Contributing / Customization

### Modify Discovery

Edit `src/discovery.py`:
- Add new RSS sources
- Adjust trend scoring
- Implement custom crawlers

### Modify Composition

Edit `src/composer.py`:
- Change article templates
- Customize image prompts
- Adjust SEO field generation

### Modify QA Rules

Edit `src/qa.py`:
- Add disallowed terms
- Adjust plagiarism threshold
- Set minimum word count per category

## ❓ FAQ

**Q: Can I publish to WordPress/Shopify automatically?**
A: Not yet. Currently saves JSON drafts locally. You can write a custom integration script to poll `./drafts/` and post via APIs.

**Q: What if no local LLM is installed?**
A: Agent automatically falls back to rule-based generation. Quality is good but less sophisticated. Install gpt4all for best results.

**Q: Can I use paid APIs like OpenAI?**
A: Not by design—this runs entirely locally without internet APIs. For remote LLMs, you'd need to modify `src/composer.py`.

**Q: How do I know if content is plagiarized?**
A: The QA validator checks for 20+ character phrase matches against source texts. If issues found, `qa_results.issues` lists them.

**Q: Can I customize the article structure?**
A: Yes! Edit the HTML generation in `src/composer.py` and `_build_article_html()` method.

**Q: How long does a full run take?**
A: ~2-5 minutes depending on network speed and local LLM performance. Discovery is slowest (feeds + DuckDuckGo scraping).

## 🎓 Learning Resources

- [feedparser Documentation](https://feedparser.readthedocs.io/)
- [BeautifulSoup Guide](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [gpt4all GitHub](https://github.com/nomic-ai/gpt4all)
- [Ollama Models](https://ollama.ai/library)

## 📞 Support

If you encounter issues:
1. Check `./logs/` for error details
2. Verify RSS feeds are valid (test in browser)
3. Ensure internet connection for discovery phase
4. Confirm Python 3.8+ is installed

---

**LocalNewsAgent v1.0** — Bringing autonomous news publishing to your local machine. 🚀
