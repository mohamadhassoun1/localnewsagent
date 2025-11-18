"""
Output & Logging module: Save publish-ready JSON drafts, HTML files, and logs.
Includes SEO metadata and image prompts.
"""

import json
import logging
from pathlib import Path
from datetime import datetime


class OutputManager:
    """Handles saving articles, logs, and metadata."""

    def __init__(self,
                 drafts_dir: str = './drafts',
                 published_dir: str = './published',
                 logs_dir: str = './logs'):
        self.drafts_dir = Path(drafts_dir)
        self.published_dir = Path(published_dir)
        self.logs_dir = Path(logs_dir)
        
        # Create directories if they don't exist
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        self.published_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("OutputManager")

    def save_draft(self, article_dict: dict, slug: str) -> str:
        """
        Save article as publish-ready JSON draft.
        Filename: {slug}__{timestamp}.json
        Returns: filepath
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{slug}__{timestamp}.json"
        filepath = self.drafts_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved draft: {filepath}")
        return str(filepath)

    def save_html(self, article_dict: dict, slug: str) -> str:
        """
        Save article as standalone HTML file.
        Filename: {slug}.html
        """
        filename = f"{slug}.html"
        filepath = self.drafts_dir / filename
        
        html_content = self._generate_html_page(article_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Saved HTML: {filepath}")
        return str(filepath)

    def _generate_html_page(self, article_dict: dict) -> str:
        """Generate a complete HTML page from article data."""
        
        article_content = article_dict.get('article_html', '')
        title = article_dict.get('title', 'Article')
        meta_desc = article_dict.get('meta_description', '')
        keywords = ', '.join(article_dict.get('keywords', []))
        
        # Generate image section
        image_section = ""
        if article_dict.get('image_prompt_main'):
            image_section = f"""
    <figure>
        <img src="https://via.placeholder.com/1200x675" alt="{article_dict.get('alt_text', 'Article image')}">
        <figcaption>Image prompt: {article_dict.get('image_prompt_main', '')}</figcaption>
    </figure>
"""
        
        # Generate sources section
        sources_section = ""
        if article_dict.get('sources'):
            sources_section = "<h2>Sources</h2>\n<ul>"
            for source in article_dict['sources']:
                sources_section += f"\n  <li><a href=\"{source.get('url', '#')}\">{source.get('name', 'Source')}</a></li>"
            sources_section += "\n</ul>"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{keywords}">
    <meta property="og:title" content="{article_dict.get('seo_title', title)}">
    <meta property="og:description" content="{meta_desc}">
    <meta name="article:tag" content="{', '.join(article_dict.get('tags', []))}">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 0.5em; }}
        h2 {{ font-size: 1.8em; margin-top: 1em; margin-bottom: 0.5em; }}
        p {{ margin-bottom: 1em; }}
        ul, ol {{ margin-left: 2em; margin-bottom: 1em; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 1em; }}
        .cta {{ background: #f0f0f0; padding: 1em; border-radius: 4px; margin: 1.5em 0; }}
        figure {{ margin: 1.5em 0; text-align: center; }}
        figure img {{ max-width: 100%; height: auto; }}
        figcaption {{ font-size: 0.9em; color: #666; margin-top: 0.5em; }}
    </style>
</head>
<body>
    <article>
        <header>
            <h1>{title}</h1>
            <div class="meta">
                <p>Published: {article_dict.get('published_at', datetime.now().isoformat())}</p>
                <p>Tags: {', '.join(article_dict.get('tags', []))}</p>
            </div>
        </header>
        
        {image_section}
        
        <div class="summary">
            <p><strong>Summary:</strong> {article_dict.get('summary', '')}</p>
        </div>
        
        <main>
            {article_content}
        </main>
        
        {sources_section}
        
        <div class="cta">
            <p><strong>{article_dict.get('cta', 'Subscribe for daily updates.')}</strong></p>
        </div>
    </article>
</body>
</html>"""
        
        return html

    def save_session_log(self, slug: str, session_data: dict) -> str:
        """
        Save detailed session log.
        Filename: {slug}.log
        """
        filename = f"{slug}.log"
        filepath = self.logs_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("LocalNewsAgent Session Log\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            # Log discovery phase
            f.write("DISCOVERY PHASE\n")
            f.write("-" * 40 + "\n")
            f.write(f"Topic: {session_data.get('topic', 'N/A')}\n")
            f.write(f"Sources discovered: {session_data.get('sources_count', 0)}\n")
            f.write(f"URLs processed: {session_data.get('urls_processed', 0)}\n\n")
            
            # Log extraction phase
            f.write("EXTRACTION PHASE\n")
            f.write("-" * 40 + "\n")
            f.write(f"Facts extracted: {session_data.get('facts_count', 0)}\n")
            f.write(f"Paywalled URLs skipped: {session_data.get('paywalled_count', 0)}\n\n")
            
            # Log composition phase
            f.write("COMPOSITION PHASE\n")
            f.write("-" * 40 + "\n")
            f.write(f"LLM used: {session_data.get('llm_used', 'Fallback')}\n")
            f.write(f"Word count: {session_data.get('word_count', 0)}\n\n")
            
            # Log QA phase
            f.write("QA & VALIDATION PHASE\n")
            f.write("-" * 40 + "\n")
            f.write(f"QA Status: {session_data.get('qa_status', 'UNKNOWN')}\n")
            f.write(f"AdSense Safe: {session_data.get('adsense_safe', False)}\n")
            if session_data.get('qa_issues'):
                f.write("Issues:\n")
                for issue in session_data['qa_issues']:
                    f.write(f"  - {issue}\n")
            f.write("\n")
            
            # Log output phase
            f.write("OUTPUT PHASE\n")
            f.write("-" * 40 + "\n")
            f.write(f"Slug: {slug}\n")
            f.write("Files saved:\n")
            for file_path in session_data.get('saved_files', []):
                f.write(f"  - {file_path}\n")
            f.write("\n")
            
            # Log sources used
            if session_data.get('sources_used'):
                f.write("SOURCES USED\n")
                f.write("-" * 40 + "\n")
                for source in session_data['sources_used']:
                    f.write(f"- {source.get('name', 'Unknown')}: {source.get('url', 'N/A')}\n")
        
        self.logger.info(f"Saved session log: {filepath}")
        return str(filepath)

    def publish_article(self, article_dict: dict) -> str:
        """
        Copy article from drafts to published directory.
        User can call this manually to "publish" an article.
        """
        slug = article_dict.get('slug', 'article')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{slug}__{timestamp}_published.json"
        filepath = self.published_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Published article: {filepath}")
        return str(filepath)

    def get_draft_list(self) -> list:
        """List all draft articles."""
        drafts = list(self.drafts_dir.glob("*__*.json"))
        return sorted([str(d) for d in drafts], reverse=True)

    def get_published_list(self) -> list:
        """List all published articles."""
        published = list(self.published_dir.glob("*_published.json"))
        return sorted([str(p) for p in published], reverse=True)
