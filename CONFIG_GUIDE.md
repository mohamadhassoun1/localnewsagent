# LocalNewsAgent Configuration Guide

## RSS Feeds (rss_feeds.txt)

Configure your news sources here. One URL per line.

### Tech & AI Sources
```
https://news.ycombinator.com/rss
https://feeds.theverge.com/theverge/index.xml
https://arstechnica.com/feed
https://feeds.techcrunch.com/TechCrunch
https://feeds.bloomberg.com/technology/news.rss
https://feeds.cnbc.com/cnbc/tech
```

### General News
```
https://feeds.bbc.co.uk/news/rss.xml
https://feeds.reuters.com/reuters/businessNews
https://feeds.bloomberg.com/markets/news.rss
```

### Science & Innovation
```
https://feeds.wired.com/wired/index
https://feeds.scientificamerican.com/feeds/sa-main
```

### Business & Markets
```
https://feeds.bloomberg.com/markets/news.rss
https://feeds.cnbc.com/cnbc/business
https://feeds.reuters.com/reuters/businessNews
```

## Site URLs (sites.txt)

Base URLs where agent will auto-discover RSS feeds.

### Tech Sites
```
https://techcrunch.com
https://www.theverge.com
https://arstechnica.com
https://www.wired.com
https://www.theinformation.com
```

### News Outlets
```
https://www.bbc.com
https://www.reuters.com
https://www.bloomberg.com
https://www.cnbc.com
```

### Crypto (optional)
```
https://coindesk.com
https://www.theblock.co
```

## Command Examples

### Daily News Brief (3 articles, 800+ words)
```bash
python main.py --top-topics 3
```

### Deep Research (5 articles, 1500+ words, no LLM)
```bash
python main.py --top-topics 5 --min-words 1500 --no-llm
```

### Trending Topics Query
```bash
python main.py --queries "AI developments" "blockchain news" "quantum computing"
```

### Production Run (with custom config)
```bash
python main.py \
  --rss-file production_feeds.txt \
  --sites-file production_sites.txt \
  --top-topics 5 \
  --min-words 1200
```

## FAQ

**Q: Can I add multiple RSS feeds from one source?**
A: Yes! If a site has multiple feed categories, add them all to rss_feeds.txt.

**Q: What if a feed returns no results?**
A: Agent logs the issue. Check if feed still exists and is valid (test in browser).

**Q: How often should I run the agent?**
A: Depends on your use case:
- Daily morning: Good for news blogs
- Every 6 hours: High-volume tech news
- Weekly: In-depth analysis sites

**Q: Can I use broken/paywalled sources?**
A: Yes—agent automatically skips paywalled content. No errors, just fewer articles from that source.

**Q: How do I exclude certain topics?**
A: Currently manual—review and delete unwanted drafts from `./drafts/` folder.
Future: Add blacklist configuration.

**Q: Can I customize the article style?**
A: Yes! Edit `src/composer.py`:
- `_build_article_html()` - Change structure
- `_generate_our_take()` - Customize commentary
- Templates in `_load_templates()` - Adjust voice

## Performance Tips

1. **Start small** - Use 3-5 topics first to test
2. **Use high-quality sources** - Better RSS feeds = better articles
3. **Cache results** - Run daily at same time (avoids duplicate topics)
4. **Monitor logs** - Check `./logs/` for extraction issues
5. **Prune old drafts** - Manually archive old articles from `./drafts/`

## Debugging

Enable verbose logging:
```bash
# Logs saved to ./logs/ - check them after each run
cat logs/session_*.log
cat logs/slug.log
```

Key files to check:
- `logs/session_20250117_120000.log` - Full workflow
- `logs/article-slug.log` - Per-article details
- `drafts/article-slug__timestamp.json` - Article JSON
- `drafts/article-slug.html` - Article HTML

## Integration with CMS

### WordPress REST API
```python
import requests
import json

with open('drafts/article__timestamp.json', 'r') as f:
    article = json.load(f)

payload = {
    'title': article['title'],
    'content': article['article_html'],
    'excerpt': article['summary'],
    'meta': {
        'description': article['meta_description'],
        'keywords': ','.join(article['keywords']),
    },
    'tags': article['tags'],
    'status': 'draft',
}

requests.post('https://yoursite.com/wp-json/wp/v2/posts',
    headers={'Authorization': f'Bearer {token}'},
    json=payload)
```

### Ghost CMS API
Similar approach using Ghost's `/admin/api/` endpoints.

### Manual Publishing
1. Copy JSON to CMS admin
2. Generate images from prompts
3. Upload featured image
4. Publish

## Monitoring & Automation

### Windows Task Scheduler
```batch
# Create scheduled task to run daily at 6 AM
schtasks /create /tn "LocalNewsAgent" /tr "C:\path\to\python.exe C:\path\to\main.py" /sc daily /st 06:00:00
```

### Cron (Linux/macOS)
```bash
# Run daily at 6 AM
0 6 * * * cd /home/user/blog && python main.py >> logs/cron.log 2>&1
```

### Monitor with log rotation
```bash
# Keep only last 30 days of logs
find logs/ -name "*.log" -mtime +30 -delete
```

---

Happy publishing! 🚀
