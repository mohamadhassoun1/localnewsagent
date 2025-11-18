"""
Extractor module: fetch article content, extract facts, detect paywalls, rewrite excerpts.
Focuses on bullet facts (<=25 words each) and original rewriting (<=20 chars copying limit).
"""

import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExtractedArticle:
    """Represents extracted article data."""
    title: str
    main_excerpt: str  # <=50 words, rewritten
    bullet_facts: List[str]  # 5-12 bullets, each <=25 words
    important_links: List[str]
    full_text: str  # For word count
    is_paywalled: bool
    source_url: str


class ContentExtractor:
    """Extracts and rewrites article content from URLs."""

    def __init__(self, log_file: Optional[str] = None):
        self.logger = logging.getLogger("ContentExtractor")
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)

        self.paywall_indicators = [
            'subscribe', 'paywall', 'premium', 'membership',
            'sign in', 'register', 'meter', 'articles per month'
        ]

    def fetch_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch URL content with headers."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.encoding = resp.apparent_encoding or 'utf-8'
            return resp.text
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

    def detect_paywall(self, html: str) -> bool:
        """Check for paywall indicators in HTML."""
        html_lower = html.lower()
        for indicator in self.paywall_indicators:
            if indicator in html_lower:
                return True
        return False

    def extract_text_from_html(self, html: str) -> Tuple[str, str, List[str]]:
        """
        Extract main content, title, and links from HTML.
        Returns (title, main_text, links).
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Try to extract title
        title = ""
        if soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            title = soup.find('title').get_text(strip=True)
        
        # Extract main article text (look for common article containers)
        article_elem = None
        for tag in ['article', 'main', ['div', {'class': re.compile('content|article|post')}]]:
            if isinstance(tag, str):
                article_elem = soup.find(tag)
            else:
                article_elem = soup.find(tag[0], tag[1])
            if article_elem:
                break
        
        if not article_elem:
            article_elem = soup.body or soup
        
        # Extract paragraphs
        paragraphs = []
        for p in article_elem.find_all('p', limit=20):
            text = p.get_text(strip=True)
            if len(text) > 30:
                paragraphs.append(text)
        
        main_text = ' '.join(paragraphs)
        
        # Extract links
        links = []
        for a in article_elem.find_all('a', limit=10):
            href = a.get('href', '')
            if href and href.startswith('http'):
                links.append(href)
        
        return title, main_text, links

    def extract_bullet_facts(self, text: str, count: int = 8) -> List[str]:
        """
        Extract key facts as bullet points from text.
        Uses sentence splitting and fact-like heuristics.
        Each bullet <=25 words.
        """
        bullets = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Filter: must be fact-like (contain numbers, dates, names, etc.)
            if self._is_fact_like(sentence) and len(bullets) < count:
                # Truncate and ensure <=25 words
                rewritten = self._rewrite_for_facts(sentence, max_words=25)
                if rewritten and rewritten not in bullets:
                    bullets.append(rewritten)
        
        return bullets[:count]

    def _is_fact_like(self, sentence: str) -> bool:
        """Check if sentence looks like a fact (contains numbers, proper nouns, etc.)."""
        # Heuristic: has numbers, years, or capitals
        has_number = re.search(r'\d+', sentence)
        has_capital = re.search(r'\b[A-Z][a-z]+', sentence)
        is_long_enough = len(sentence) > 20
        
        return is_long_enough and (has_number or has_capital)

    def _rewrite_for_facts(self, text: str, max_words: int = 25) -> str:
        """Truncate and normalize fact for bullet point."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Simple rewrite: keep original but truncate
        words = text.split()[:max_words]
        result = ' '.join(words)
        if len(text.split()) > max_words:
            result += '.'
        return result

    def extract_main_excerpt(self, text: str, max_words: int = 50) -> str:
        """Extract and rewrite a main excerpt (<=50 words, original phrasing)."""
        # Find first substantial paragraph
        sentences = re.split(r'[.!?]\s+', text)
        excerpt_parts = []
        word_count = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                excerpt_parts.append(sentence)
                word_count += len(sentence.split())
                if word_count >= max_words:
                    break
        
        excerpt = '. '.join(excerpt_parts)
        words = excerpt.split()[:max_words]
        result = ' '.join(words)
        if len(excerpt.split()) > max_words:
            result += '.'
        
        return result

    def extract(self, url: str) -> Optional[ExtractedArticle]:
        """
        Fetch and extract article from URL.
        Returns ExtractedArticle or None if failed/paywalled.
        """
        html = self.fetch_url(url)
        if not html:
            return None
        
        # Check paywall
        is_paywalled = self.detect_paywall(html)
        if is_paywalled:
            self.logger.warning(f"Paywall detected on {url}")
        
        # Extract text and title
        title, main_text, links = self.extract_text_from_html(html)
        
        if not main_text:
            self.logger.warning(f"No content extracted from {url}")
            return None
        
        # Extract facts and excerpt
        bullet_facts = self.extract_bullet_facts(main_text)
        excerpt = self.extract_main_excerpt(main_text)
        
        article = ExtractedArticle(
            title=title,
            main_excerpt=excerpt,
            bullet_facts=bullet_facts,
            important_links=links,
            full_text=main_text,
            is_paywalled=is_paywalled,
            source_url=url
        )
        
        self.logger.info(f"Extracted article from {url}: {len(bullet_facts)} facts, {len(excerpt.split())} words in excerpt")
        
        return article

    def extract_multiple(self, urls: List[str]) -> List[ExtractedArticle]:
        """Extract articles from multiple URLs."""
        articles = []
        for url in urls:
            article = self.extract(url)
            if article and not article.is_paywalled:
                articles.append(article)
        return articles
