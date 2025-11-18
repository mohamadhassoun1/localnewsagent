"""
Discovery module: find trending topics from RSS feeds, site crawlers, and search results.
No external APIs used. Local parsing and scraping only.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Topic:
    """Represents a discovered news topic."""
    title_hint: str
    short_excerpt: str  # Rewritten, 20-40 words
    source_url: str
    published_time: Optional[str]
    category: str  # tech, ai, crypto, business
    trend_score: float  # 0-100
    source_name: str


class DiscoveryEngine:
    """Discovers trending topics from multiple local sources."""

    def __init__(self, log_file: Optional[str] = None):
        self.topics: List[Topic] = []
        self.seen_urls = set()
        self.logger = logging.getLogger("DiscoveryEngine")
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)

    def load_rss_feeds(self, feed_file: str) -> List[Dict]:
        """Load RSS feed URLs from config file."""
        try:
            with open(feed_file, 'r') as f:
                feeds = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            self.logger.info(f"Loaded {len(feeds)} RSS feeds from {feed_file}")
            return feeds
        except FileNotFoundError:
            self.logger.warning(f"RSS feed file not found: {feed_file}")
            return []

    def load_sites_to_crawl(self, sites_file: str) -> List[str]:
        """Load base URLs to crawl for feeds."""
        try:
            with open(sites_file, 'r') as f:
                sites = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            self.logger.info(f"Loaded {len(sites)} sites to crawl from {sites_file}")
            return sites
        except FileNotFoundError:
            self.logger.warning(f"Sites file not found: {sites_file}")
            return []

    def fetch_rss_feed(self, feed_url: str, category: str = "tech") -> List[Topic]:
        """Parse RSS feed and extract topics."""
        topics = []
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and feed.bozo_exception:
                self.logger.warning(f"Feed parsing issue for {feed_url}: {feed.bozo_exception}")

            source_name = feed.feed.get('title', urlparse(feed_url).netloc)
            
            for entry in feed.entries[:10]:  # Top 10 entries
                url = entry.get('link', '')
                title = entry.get('title', 'Untitled')
                published = entry.get('published', datetime.now().isoformat())
                
                if url and url not in self.seen_urls:
                    self.seen_urls.add(url)
                    
                    # Rewrite excerpt (truncate and paraphrase indicator)
                    summary = entry.get('summary', '')
                    excerpt = self._rewrite_excerpt(summary, max_words=30)
                    
                    # Simple trend scoring based on recency
                    try:
                        pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                        age_hours = (datetime.now(pub_date.tzinfo) - pub_date).total_seconds() / 3600
                        trend_score = max(0, 100 - (age_hours * 2))
                    except:
                        trend_score = 75

                    topic = Topic(
                        title_hint=title[:100],
                        short_excerpt=excerpt,
                        source_url=url,
                        published_time=published,
                        category=category,
                        trend_score=trend_score,
                        source_name=source_name
                    )
                    topics.append(topic)
                    
            self.logger.info(f"Fetched {len(topics)} topics from {source_name}")
        except Exception as e:
            self.logger.error(f"Error fetching RSS feed {feed_url}: {e}")
        
        return topics

    def discover_feed_url(self, base_url: str) -> Optional[str]:
        """Attempt to discover RSS/feed URL from a base site."""
        candidates = [
            f"{base_url}/rss",
            f"{base_url}/feed",
            f"{base_url}/feeds",
            f"{base_url}/feed.xml",
            f"{base_url}/rss.xml",
        ]
        
        for candidate in candidates:
            try:
                resp = requests.head(candidate, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    self.logger.info(f"Found feed URL: {candidate}")
                    return candidate
            except:
                pass
        
        return None

    def scrape_duckduckgo(self, query: str, category: str = "tech") -> List[Topic]:
        """
        Scrape DuckDuckGo results page for a given query (no API, HTML scraping only).
        Returns top results as topics.
        """
        topics = []
        try:
            url = f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # DuckDuckGo result structure (adjust based on current HTML)
            results = soup.find_all('div', {'class': 'result'}, limit=5)
            
            for result in results:
                try:
                    link_elem = result.find('a', {'class': 'result__a'})
                    title_elem = result.find('span', {'class': 'result__title'})
                    snippet_elem = result.find('a', {'class': 'result__snippet'})
                    
                    if link_elem and title_elem:
                        url = link_elem.get('href', '')
                        title = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        if url and url not in self.seen_urls and 'duckduckgo' not in url:
                            self.seen_urls.add(url)
                            excerpt = self._rewrite_excerpt(snippet, max_words=35)
                            
                            topic = Topic(
                                title_hint=title[:100],
                                short_excerpt=excerpt,
                                source_url=url,
                                published_time=datetime.now().isoformat(),
                                category=category,
                                trend_score=80,
                                source_name="DuckDuckGo"
                            )
                            topics.append(topic)
                except Exception as e:
                    self.logger.debug(f"Error parsing result: {e}")
            
            self.logger.info(f"Scraped {len(topics)} topics from DuckDuckGo for '{query}'")
        except Exception as e:
            self.logger.error(f"Error scraping DuckDuckGo for '{query}': {e}")
        
        return topics

    def _rewrite_excerpt(self, text: str, max_words: int = 30) -> str:
        """Truncate and normalize excerpt for display."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Truncate
        words = text.split()[:max_words]
        return ' '.join(words) + ('...' if len(text.split()) > max_words else '')

    def discover_all(self, 
                     rss_file: str = 'rss_feeds.txt',
                     sites_file: str = 'sites.txt',
                     queries: Optional[List[str]] = None) -> List[Topic]:
        """
        Run full discovery: RSS feeds -> site crawlers -> SERP queries.
        Returns sorted list by trend_score.
        """
        # 1. RSS feeds
        feeds = self.load_rss_feeds(rss_file)
        for feed_url in feeds:
            topics = self.fetch_rss_feed(feed_url)
            self.topics.extend(topics)
        
        # 2. Site crawlers (attempt to find feeds)
        sites = self.load_sites_to_crawl(sites_file)
        for site_url in sites:
            feed_url = self.discover_feed_url(site_url)
            if feed_url:
                topics = self.fetch_rss_feed(feed_url)
                self.topics.extend(topics)
        
        # 3. SERP queries (optional)
        if queries:
            for query in queries:
                topics = self.scrape_duckduckgo(query)
                self.topics.extend(topics)
        
        # Sort by trend score
        self.topics = sorted(self.topics, key=lambda t: t.trend_score, reverse=True)
        self.logger.info(f"Discovery complete: {len(self.topics)} unique topics found")
        
        return self.topics

    def get_top_topics(self, count: int = 5) -> List[Topic]:
        """Return top N topics by trend score."""
        return self.topics[:count]

    def to_dicts(self) -> List[Dict]:
        """Convert topics to dictionaries for JSON serialization."""
        return [asdict(t) for t in self.topics]
