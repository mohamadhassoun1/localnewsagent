# QUICKSTART - LocalNewsAgent

Get started publishing original articles in under 5 minutes.

## 1️⃣ Install

```bash
cd c:\Users\moham\Desktop\blog
pip install -r requirements.txt
```

## 2️⃣ (Optional) Install Local LLM

For best article quality, install one of:

```bash
# Option A: gpt4all (recommended, easiest, auto-downloads models)
pip install gpt4all

# Option B: Ollama (more control, visit https://ollama.ai)
# Then: ollama pull orca-mini
```

## 3️⃣ Configure Sources

**rss_feeds.txt** - Add your RSS feeds (one per line):
```
https://news.ycombinator.com/rss
https://feeds.theverge.com/theverge/index.xml
https://arstechnica.com/feed
```

**sites.txt** - Add base URLs to crawl (one per line):
```
https://techcrunch.com
https://www.theverge.com
https://arstechnica.com
```

## 4️⃣ Run!

### Default (top 3 topics, 800+ words):
```bash
python main.py
```

### Custom (top 5 topics, 1000+ words, no LLM fallback):
```bash
python main.py --top-topics 5 --min-words 1000
```

### With search queries:
```bash
python main.py --queries "artificial intelligence" "blockchain" "quantum computing"
```

## 5️⃣ Check Output

Articles saved to `./drafts/`:

```bash
# List all drafts
ls -la drafts/

# View JSON metadata
cat drafts/article-slug__20250117_120000.json

# View standalone HTML
start drafts/article-slug.html    # Windows
# or open drafts/article-slug.html  # macOS
```

## 📋 What You Get

Each article includes:
- ✅ 800-1600 word original article
- ✅ SEO title, meta description, keywords
- ✅ 3 AI image prompts (for DALL-E, Midjourney, etc.)
- ✅ Fact bullets, analysis, "Our take"
- ✅ HTML + JSON formats
- ✅ Session logs with sources

## 🎯 Next Steps

1. **Review drafts** in `./drafts/` folder
2. **Edit HTML** as needed
3. **Generate images** using prompts (e.g., DALL-E)
4. **Publish manually** to your CMS (WordPress, Ghost, etc.)

Or create a custom publish script that polls `./drafts/` for auto-posting!

## ❓ Troubleshooting

| Issue | Fix |
|-------|-----|
| "No topics discovered" | Check RSS feeds are valid (copy URL into browser) |
| "No data extracted" | URLs may be paywalled or blocked; add more RSS sources |
| Slow generation | First LLM run downloads model (~2GB). Subsequent runs are faster |
| Bad quality articles | Install gpt4all for better generation |

## 💡 Pro Tips

- **Best time to run**: Early morning to catch overnight news
- **Setup automation**: Use Windows Task Scheduler or cron to run `python main.py` daily
- **Monitor quality**: Review logs in `./logs/` for issues
- **Refine sources**: Add high-quality RSS feeds for better topics
- **Customize templates**: Edit `src/composer.py` for your brand voice

---

Ready? Run `python main.py` now! 🚀
