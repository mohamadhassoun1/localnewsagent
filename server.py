"""
LocalNewsAgent Web Server - Demo Dashboard
Displays generated articles and allows management
"""

import http.server
import socketserver
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime


class ArticleDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for article dashboard"""

    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_dashboard().encode('utf-8'))
        
        elif self.path.startswith('/article/'):
            slug = self.path.replace('/article/', '').replace('.html', '')
            html = self.get_article(slug)
            if html:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
        
        elif self.path.startswith('/api/articles'):
            articles = self.get_articles_list()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(articles).encode('utf-8'))

        # Serve published static files under /published/
        elif self.path.startswith('/published/'):
            rel = self.path[len('/published/'):]
            file_path = Path('published') / rel
            if file_path.exists() and file_path.is_file():
                ct = 'application/octet-stream'
                if file_path.suffix == '.html':
                    ct = 'text/html; charset=utf-8'
                elif file_path.suffix == '.json':
                    ct = 'application/json'
                elif file_path.suffix == '.css':
                    ct = 'text/css; charset=utf-8'
                self.send_response(200)
                self.send_header('Content-type', ct)
                self.end_headers()
                with open(file_path, 'rb') as rf:
                    self.wfile.write(rf.read())
                return

        # Trigger publish script (convenience endpoint - local only)
        elif self.path.startswith('/publish'):
            # Protect publish endpoint with a token if configured
            publish_token = os.getenv('PUBLISH_TOKEN')
            # parse query param token if present
            token = None
            if '?' in self.path:
                _, qs = self.path.split('?', 1)
                for part in qs.split('&'):
                    if part.startswith('token='):
                        token = part.split('=', 1)[1]
                        break

            if publish_token:
                if not token or token != publish_token:
                    self.send_response(403)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'Forbidden: missing or invalid publish token')
                    return

            # run publish script
            try:
                proc = subprocess.run(["python", "publish.py"], cwd=str(Path(__file__).parent), capture_output=True, text=True, timeout=120)
                output = proc.stdout + '\n' + proc.stderr
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(output.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
            return

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Not Found</h1>')

    def get_dashboard(self):
        """Return dashboard HTML"""
        articles = self.get_articles_list()
        
        articles_html = ""
        if articles:
            for article in articles:
                articles_html += f"""
                <div class="article-card">
                    <h3><a href="/article/{article['slug']}">{article['title']}</a></h3>
                    <p class="meta">
                        <span class="date">{article['date']}</span>
                        <span class="words">{article['words']} words</span>
                    </p>
                    <p class="summary">{article['summary'][:150]}...</p>
                    <div class="tags">
                        {' '.join([f'<span class="tag">{t}</span>' for t in article['tags'][:3]])}
                    </div>
                    <a href="/article/{article['slug']}" class="read-more">Read Full Article →</a>
                </div>
                """
        else:
            articles_html = """
            <div class="no-articles">
                <p>📝 No articles yet</p>
                <p>Run: <code>python main.py</code> to generate articles</p>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocalNewsAgent Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        header h1 {{
            color: #333;
            margin-bottom: 5px;
            font-size: 2.5em;
        }}
        
        header .subtitle {{
            color: #666;
            font-size: 1.1em;
            margin-bottom: 15px;
        }}
        
        .stats {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .articles {{
            display: grid;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .article-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .article-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .article-card h3 {{
            margin-bottom: 10px;
        }}
        
        .article-card h3 a {{
            color: #333;
            text-decoration: none;
            font-size: 1.4em;
        }}
        
        .article-card h3 a:hover {{
            color: #667eea;
        }}
        
        .meta {{
            color: #999;
            font-size: 0.9em;
            margin-bottom: 10px;
            display: flex;
            gap: 15px;
        }}
        
        .summary {{
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .tags {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        
        .tag {{
            background: #f0f0f0;
            color: #667eea;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }}
        
        .read-more {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .read-more:hover {{
            color: #764ba2;
            margin-left: 5px;
        }}
        
        .no-articles {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            color: #999;
        }}
        
        .no-articles p {{
            margin: 10px 0;
            font-size: 1.1em;
        }}
        
        .no-articles code {{
            background: #f5f5f5;
            padding: 5px 10px;
            border-radius: 3px;
            font-family: monospace;
            color: #333;
        }}
        
        footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }}
        
        footer a {{
            color: white;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 LocalNewsAgent</h1>
            <p class="subtitle">Autonomous Local News Publishing Dashboard</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(articles)}</div>
                    <div class="stat-label">Published Articles</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{sum(a['words'] for a in articles) if articles else 0}</div>
                    <div class="stat-label">Total Words</div>
                </div>
                <div class="stat">
                    <div class="stat-value">✅</div>
                    <div class="stat-label">System Status</div>
                </div>
            </div>
        </header>
        
        <div class="articles">
            {articles_html}
        </div>
        
        <footer>
            <p>LocalNewsAgent v1.0 | <a href="http://localhost:8000/dashboard">Dashboard</a> | <a href="http://localhost:8000/api/articles">API</a></p>
        </footer>
    </div>
</body>
</html>
        """

    def get_articles_list(self):
        """Get list of articles preferring published folder, fallback to drafts"""
        published_dir = Path('./published')
        drafts_dir = Path('./drafts')
        articles = []

        # First prefer published articles
        if published_dir.exists():
            # If there is an index.json, use it for ordering
            index_file = published_dir / 'index.json'
            if index_file.exists():
                try:
                    with open(index_file, 'r', encoding='utf-8') as f:
                        idx = json.load(f)
                        for item in idx:
                            articles.append({
                                'slug': item.get('slug'),
                                'title': item.get('title'),
                                'summary': item.get('summary', '')[:240],
                                'words': item.get('words', 0),
                                'tags': [],
                                'date': item.get('date', '')[:10]
                            })
                        return articles
                except Exception:
                    pass

            # Otherwise, load any JSON files in published
            for json_file in sorted(published_dir.glob('*.json'), reverse=True):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        articles.append({
                            'slug': data.get('slug', 'unknown'),
                            'title': data.get('title', 'Untitled'),
                            'summary': data.get('summary', 'No summary'),
                            'words': data.get('word_count', 0),
                            'tags': data.get('tags', []),
                            'date': data.get('published_at', datetime.now().isoformat())[:10]
                        })
                except:
                    pass

        # Fallback to drafts if no published articles found
        if not articles and drafts_dir.exists():
            for json_file in sorted(drafts_dir.glob('*__*.json'), reverse=True):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        articles.append({
                            'slug': data.get('slug', 'unknown'),
                            'title': data.get('title', 'Untitled'),
                            'summary': data.get('summary', 'No summary'),
                            'words': data.get('word_count', 0),
                            'tags': data.get('tags', []),
                            'date': data.get('published_at', datetime.now().isoformat())[:10]
                        })
                except:
                    pass

        return articles

    def get_article(self, slug):
        """Get article HTML"""
        published_dir = Path('./published')
        drafts_dir = Path('./drafts')

        # Check published JSON files first
        if published_dir.exists():
            for json_file in published_dir.glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('slug') == slug:
                            return self.render_article(data)
                except Exception:
                    pass

            # check published HTML
            html_file = published_dir / f'{slug}.html'
            if html_file.exists():
                with open(html_file, 'r', encoding='utf-8') as f:
                    return f.read()

        # Fallback to drafts JSON
        if drafts_dir.exists():
            for json_file in drafts_dir.glob('*__*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('slug') == slug:
                            return self.render_article(data)
                except Exception:
                    pass

            # Try to find HTML in drafts
            html_file = drafts_dir / f'{slug}.html'
            if html_file.exists():
                with open(html_file, 'r', encoding='utf-8') as f:
                    return f.read()

        return None

    def render_article(self, data):
        """Render article from JSON data"""
        keywords = ', '.join(data.get('keywords', []))
        tags = ' '.join([f'<a href="#tag-{t}">{t}</a>' for t in data.get('tags', [])])
        sources = ''.join([f'<li><a href="{s.get("url", "#")}">{s.get("name", "Source")}</a></li>' 
                          for s in data.get('sources', [])])
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get('title', 'Article')}</title>
    <meta name="description" content="{data.get('meta_description', '')}">
    <meta name="keywords" content="{keywords}">
    <meta property="og:title" content="{data.get('seo_title', '')}">
    <meta property="og:description" content="{data.get('meta_description', '')}">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, serif;
            line-height: 1.7;
            color: #333;
            background: #f9f9f9;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        header {{
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
            color: #222;
        }}
        
        .meta {{
            color: #666;
            font-size: 0.95em;
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
        }}
        
        .tags {{
            margin-top: 15px;
        }}
        
        .tags a {{
            display: inline-block;
            background: #f0f0f0;
            color: #667eea;
            padding: 5px 12px;
            margin-right: 8px;
            margin-bottom: 8px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.9em;
        }}
        
        .tags a:hover {{
            background: #667eea;
            color: white;
        }}
        
        article {{
            background: white;
            padding: 40px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 40px;
        }}
        
        article h2 {{
            font-size: 1.6em;
            margin: 30px 0 15px 0;
            color: #222;
        }}
        
        article h2:first-child {{
            margin-top: 0;
        }}
        
        article p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        article ul, article ol {{
            margin: 20px 0 20px 40px;
        }}
        
        article li {{
            margin-bottom: 10px;
        }}
        
        article a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        article a:hover {{
            text-decoration: underline;
        }}
        
        .image-prompt {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }}
        
        .image-prompt strong {{
            display: block;
            margin-bottom: 8px;
            color: #667eea;
        }}
        
        .sources {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-top: 30px;
        }}
        
        .sources h3 {{
            margin-bottom: 15px;
            color: #222;
        }}
        
        .sources ul {{
            list-style: none;
            margin: 0;
        }}
        
        .sources li {{
            margin-bottom: 10px;
        }}
        
        .sources a {{
            color: #667eea;
            text-decoration: none;
            word-break: break-all;
        }}
        
        .sources a:hover {{
            text-decoration: underline;
        }}
        
        .cta {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 5px;
            text-align: center;
            margin-top: 40px;
        }}
        
        .cta p {{
            font-size: 1.1em;
            margin-bottom: 15px;
        }}
        
        .back-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 20px;
        }}
        
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-link">← Back to Dashboard</a>
        
        <header>
            <h1>{data.get('title', 'Article')}</h1>
            <div class="meta">
                <span>📅 {data.get('published_at', 'Unknown date')[:10]}</span>
                <span>📝 {data.get('word_count', 0)} words</span>
            </div>
            <div class="tags">
                {tags}
            </div>
        </header>
        
        <article>
            {data.get('article_html', '<p>Content not available</p>')}
            
            <div class="image-prompt">
                <strong>📸 Featured Image Prompt:</strong>
                {data.get('image_prompt_main', 'No prompt')}
            </div>
            
            <div class="sources">
                <h3>📚 Sources</h3>
                <ul>
                    {sources if sources else '<li>No sources listed</li>'}
                </ul>
            </div>
        </article>
        
        <div class="cta">
            <p>{data.get('cta', 'Subscribe for more updates')}</p>
        </div>
    </div>
</body>
</html>
        """

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_server(port=8000):
    """Start the web server"""
    handler = ArticleDashboardHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"""
╔════════════════════════════════════════════════════════╗
║                                                        ║
║          🚀 LocalNewsAgent Dashboard Online            ║
║                                                        ║
║              http://localhost:{port}                    ║
║              http://localhost:{port}/dashboard        ║
║              http://localhost:{port}/api/articles     ║
║                                                        ║
║  Press CTRL+C to stop the server                     ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
        """)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Server stopped")


if __name__ == '__main__':
    run_server(8080)
