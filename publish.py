"""Publish script for LocalNewsAgent demo

Reads JSON files from `drafts/` and writes HTML + JSON copies to `published/`.
Run: python publish.py
"""
import json
from pathlib import Path
from datetime import datetime
import html


ROOT = Path(__file__).parent
DRAFTS = ROOT / 'drafts'
PUBLISHED = ROOT / 'published'


def ensure_dirs():
    PUBLISHED.mkdir(parents=True, exist_ok=True)


def render_article_html(article: dict) -> str:
    title = html.escape(article.get('title', 'Untitled'))
    seo_title = html.escape(article.get('seo_title', title))
    meta_description = html.escape(article.get('meta_description', ''))
    published_at = article.get('published_at') or datetime.utcnow().isoformat()
    body = article.get('article_html', '')
    sources = article.get('sources', [])
    sources_html = ''
    if sources:
        sources_html = '<h4>Sources</h4><ul>' + ''.join([f"<li><a href=\"{html.escape(s.get('url',''))}\">{html.escape(s.get('name',''))}</a></li>" for s in sources]) + '</ul>'

    cta = html.escape(article.get('cta', ''))

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{seo_title}</title>
  <meta name="description" content="{meta_description}">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 24px; max-width:900px }}
    header {{ margin-bottom: 18px }}
    .meta {{ color: #666; font-size: 0.95rem }}
    .content {{ margin-top: 18px }}
    footer {{ margin-top: 36px; padding-top: 12px; border-top: 1px solid #eee }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p class="meta">Published: {published_at} — {article.get('word_count','?')} words</p>
  </header>
  <main class="content">
    {body}
    {sources_html}
  </main>
  <footer>
    <p>{cta}</p>
  </footer>
</body>
</html>"""
    return page


def publish_all():
    ensure_dirs()
    index = []
    files = list(DRAFTS.glob('*.json'))
    if not files:
        print('No drafts found in', DRAFTS)
        return

    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                art = json.load(f)
        except Exception as e:
            print('Skipping', path.name, '— could not read JSON:', e)
            continue

        slug = art.get('slug') or (path.stem.split('__')[0])
        if not slug:
            slug = path.stem

        # write HTML
        html_content = render_article_html(art)
        out_html = PUBLISHED / f"{slug}.html"
        with open(out_html, 'w', encoding='utf-8') as fh:
            fh.write(html_content)

        # copy JSON metadata
        out_json = PUBLISHED / path.name
        with open(out_json, 'w', encoding='utf-8') as fj:
            json.dump(art, fj, ensure_ascii=False, indent=2)

        index.append({
            'title': art.get('title', slug),
            'slug': slug,
            'date': art.get('published_at', datetime.utcnow().isoformat()),
            'summary': art.get('summary', '')[:240],
            'words': art.get('word_count', 0),
        })

        print('Published:', slug)

    # write index
    idx_path = PUBLISHED / 'index.json'
    with open(idx_path, 'w', encoding='utf-8') as fi:
        json.dump(index, fi, ensure_ascii=False, indent=2)

    # write a simple HTML index page
    list_items = ''.join([f"<li><a href=\"{i['slug']}.html\">{html.escape(i['title'])}</a> — {i['date']} ({i['words']} words)</li>" for i in index])
    index_html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Published Articles</title></head><body><h1>Published Articles</h1><ul>{list_items}</ul></body></html>"""

    with open(PUBLISHED / 'index.html', 'w', encoding='utf-8') as fidx:
        fidx.write(index_html)

    print('\nPublishing complete. Published files are in', PUBLISHED)


if __name__ == '__main__':
    publish_all()
