"""
Composer module: Generate articles using local LLM or fallback rule-based method.
Outputs JSON with all SEO fields: title, slug, seo_title, meta_description, keywords, tags,
image prompts, and article HTML.
"""

import json
import logging
import re
import random
import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ComposedArticle:
    """Represents a composed article with all metadata."""
    title: str
    article_html: str  # HTML with <h2>, <p>, <ul>/<li> tags
    summary: str  # 40-60 words
    word_count: int
    tags: List[str]
    slug: str
    seo_title: str  # <=60 chars
    meta_description: str  # 120-155 chars
    keywords: List[str]  # 8-12 items
    image_prompt_main: str
    image_prompt_alt1: str
    image_prompt_alt2: str
    alt_text: str  # <=120 chars
    sources: List[Dict[str, str]]  # [{"name": "", "url": ""}]
    cta: str
    our_take: str
    published_at: str


class ArticleComposer:
    """Composes articles using local LLM or fallback rule-based generation."""

    def __init__(self, use_local_llm: bool = True, log_file: Optional[str] = None):
        self.use_local_llm = use_local_llm
        self.logger = logging.getLogger("ArticleComposer")
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)

        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, List[str]]:
        """Load sentence templates for rule-based fallback."""
        return {
            'lead': [
                "In a significant development, {fact}.",
                "Recent reports indicate that {fact}.",
                "A major announcement reveals that {fact}.",
                "The latest news shows that {fact}.",
            ],
            'transition': [
                "This development comes as {context}.",
                "Building on this trend, {context}.",
                "Contributing to this shift, {context}.",
                "Adding to this momentum, {context}.",
            ],
            'analysis': [
                "The implications of this move are noteworthy: {implication}.",
                "This represents a key shift toward {implication}.",
                "Industry experts point to this as evidence of {implication}.",
                "Looking ahead, this suggests {implication}.",
            ]
        }

    def check_local_llm_available(self) -> bool:
        """Check if gpt4all or ollama is available locally."""
        if not self.use_local_llm:
            return False

        try:
            # Try gpt4all
            import gpt4all
            self.logger.info("Local LLM (gpt4all) detected")
            return True
        except ImportError:
            pass

        try:
            # Try ollama
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("Local LLM (Ollama) detected")
                return True
        except Exception:
            pass

        self.logger.warning("No local LLM detected; falling back to rule-based generation")
        return False

    def compose_with_llm(self,
                        topic_title: str,
                        facts: List[str],
                        sources: List[Dict[str, str]]) -> Optional[ComposedArticle]:
        """Compose article using local LLM (gpt4all or ollama)."""
        try:
            # Attempt to import gpt4all dynamically
            gpt4all_module = __import__('gpt4all')
            model = gpt4all_module.GPT4All("orca-mini", allow_download=True)
        except Exception:
            self.logger.warning("gpt4all not available; switching to fallback")
            return None

        prompt = self._build_llm_prompt(topic_title, facts, sources)

        try:
            response = model.generate(prompt, max_tokens=2000, temp=0.7)
            result = json.loads(response)
            
            article = ComposedArticle(
                title=result.get('title', topic_title[:100]),
                article_html=result.get('article_html', ''),
                summary=result.get('summary', '')[:250],
                word_count=result.get('word_count', 0),
                tags=result.get('tags', [])[:8],
                slug=result.get('slug', self._generate_slug(topic_title)),
                seo_title=result.get('seo_title', '')[:60],
                meta_description=result.get('meta_description', '')[:155],
                keywords=result.get('keywords', [])[:12],
                image_prompt_main=result.get('image_prompt_main', ''),
                image_prompt_alt1=result.get('image_prompt_alt1', ''),
                image_prompt_alt2=result.get('image_prompt_alt2', ''),
                alt_text=result.get('alt_text', '')[:120],
                sources=sources,
                cta=result.get('cta', 'Subscribe for daily updates.'),
                our_take=result.get('our_take', 'A pivotal moment in technology.'),
                published_at=datetime.now().isoformat()
            )
            
            self.logger.info(f"Composed article via LLM: {article.slug}")
            return article
        except Exception as e:
            self.logger.error(f"LLM composition failed: {e}")
            return None

    def compose_with_fallback(self,
                              topic_title: str,
                              facts: List[str],
                              sources: List[Dict[str, str]],
                              category: str = "tech") -> ComposedArticle:
        """Compose article using rule-based templates and fact synthesis."""
        
        # Generate article structure
        article_html = self._build_article_html(topic_title, facts)
        
        # Generate SEO fields
        slug = self._generate_slug(topic_title)
        seo_title = self._generate_seo_title(topic_title)
        meta_description = self._generate_meta_description(topic_title, facts)
        keywords = self._generate_keywords(topic_title, category)
        tags = self._generate_tags(category, topic_title)
        
        # Generate image prompts
        image_prompts = self._generate_image_prompts(topic_title, category)
        
        # Generate summary
        summary = self._generate_summary(facts)
        
        # Word count
        word_count = len(article_html.split())
        
        # Our take
        our_take = self._generate_our_take(topic_title, category)
        
        article = ComposedArticle(
            title=topic_title[:100],
            article_html=article_html,
            summary=summary,
            word_count=word_count,
            tags=tags,
            slug=slug,
            seo_title=seo_title,
            meta_description=meta_description,
            keywords=keywords,
            image_prompt_main=image_prompts['main'],
            image_prompt_alt1=image_prompts['alt1'],
            image_prompt_alt2=image_prompts['alt2'],
            alt_text=image_prompts['alt_text'],
            sources=sources,
            cta="Subscribe for daily updates on tech and AI.",
            our_take=our_take,
            published_at=datetime.now().isoformat()
        )
        
        self.logger.info(f"Composed article via fallback: {slug} ({word_count} words)")
        return article

    def _build_article_html(self, topic: str, facts: List[str]) -> str:
        """Build article HTML from facts."""
        html_parts = [f"<h1>{topic}</h1>"]
        
        # Lead
        if facts:
            lead = f"<p>{facts[0]}</p>"
            html_parts.append(lead)
        
        # Body: distribute facts across paragraphs
        body_facts = facts[1:] if len(facts) > 1 else []
        for fact in body_facts[:8]:
            html_parts.append(f"<p>{fact}</p>")
        
        # Bullet facts
        if body_facts:
            html_parts.append("<h2>Key Points</h2>")
            html_parts.append("<ul>")
            for fact in body_facts[:5]:
                html_parts.append(f"<li>{fact}</li>")
            html_parts.append("</ul>")
        
        # Analysis section
        html_parts.append("<h2>What This Means</h2>")
        analysis = self._generate_analysis(facts)
        html_parts.append(f"<p>{analysis}</p>")
        
        # Our take
        html_parts.append("<h2>Our Take</h2>")
        html_parts.append(f"<p><strong>Our take:</strong> {self._generate_our_take(topic, 'tech')}</p>")
        
        # Internal links
        html_parts.append("<p><a href='/tag/tech'>Tech News</a> | <a href='/category/tech'>More Tech Stories</a></p>")
        
        return "\n".join(html_parts)

    def _build_llm_prompt(self, topic: str, facts: List[str], sources: List[Dict]) -> str:
        """Build prompt for local LLM."""
        facts_str = "\n".join([f"- {f}" for f in facts[:10]])
        sources_str = "\n".join([f"- {s.get('name', 'Unknown')}: {s.get('url', '')}" for s in sources])

        prompt = f"""You are a professional news article writer. Compose an original, SEO-optimized news article.

Topic: {topic}

Key Facts:
{facts_str}

Sources:
{sources_str}

RULES:
1. Never copy >20 consecutive characters from facts
2. Paraphrase and expand everything
3. Article must be 800-1200 words
4. Include "Our take:" near the end
5. Must include a Sources section
6. No adult, violent, or illegal content

Output ONLY valid JSON (no markdown):
{{
 "title": "<headline <=12 words>",
 "article_html": "<HTML with <h2>, <p>, <ul> tags>",
 "summary": "<40-60 words>",
 "word_count": <int>,
 "tags": ["tag1", "tag2"],
 "slug": "<url-slug>",
 "seo_title": "<<=60 chars>",
 "meta_description": "<120-155 chars>",
 "keywords": ["k1", "k2"],
 "image_prompt_main": "<16:9 image prompt>",
 "image_prompt_alt1": "<alt prompt>",
 "image_prompt_alt2": "<alt prompt 2>",
 "alt_text": "<<=120 chars>",
 "our_take": "<one sentence>",
 "cta": "Subscribe for daily updates."
}}
"""
        return prompt

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug."""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]

    def _generate_seo_title(self, title: str) -> str:
        """Generate SEO title (<=60 chars)."""
        seo = title[:60]
        if len(seo) < 30:
            seo += " | Latest News"
        return seo[:60]

    def _generate_meta_description(self, title: str, facts: List[str]) -> str:
        """Generate meta description (120-155 chars)."""
        desc = f"{title}. {facts[0][:100] if facts else 'Read the latest insights.'}"
        desc = desc[:155]
        return desc

    def _generate_keywords(self, title: str, category: str) -> List[str]:
        """Generate 8-12 SEO keywords."""
        base_keywords = [category, 'news', 'latest', 'today', 'trending']
        title_words = [w for w in title.lower().split() if len(w) > 3][:4]
        return (base_keywords + title_words)[:12]

    def _generate_tags(self, category: str, title: str) -> List[str]:
        """Generate 5-8 tags."""
        tags = [category, 'news', 'insights']
        title_words = [w for w in title.lower().split() if len(w) > 4][:3]
        return (tags + title_words)[:8]

    def _generate_image_prompts(self, title: str, category: str) -> Dict[str, str]:
        """Generate 3 image prompts (16:9, no logos/faces) + alt_text."""
        
        category_hints = {
            'tech': 'futuristic technology, digital interfaces, innovation',
            'ai': 'artificial intelligence, neural networks, machine learning visualizations',
            'crypto': 'blockchain, digital currency, decentralized networks',
            'business': 'corporate strategy, growth charts, business meeting'
        }
        
        hint = category_hints.get(category, 'modern technology')
        
        prompts = {
            'main': f"16:9 cinematic illustration of {hint}, abstract modern art style, no logos, no faces, professional, {title[:30]}",
            'alt1': f"Modern 16:9 infographic featuring {category} concepts, digital art, clean design, no people",
            'alt2': f"Abstract 16:9 visualization of {category} innovation, tech aesthetic, geometric shapes, vibrant colors",
            'alt_text': f"Illustration representing {title[:40]}"
        }
        
        return prompts

    def _generate_summary(self, facts: List[str]) -> str:
        """Generate 40-60 word summary."""
        summary_parts = facts[:3]
        summary = " ".join(summary_parts)
        words = summary.split()[:60]
        return " ".join(words)

    def _generate_our_take(self, _: str, category: str) -> str:
        """Generate 'Our take' statement."""
        takes = [
            f"This represents a significant shift in {category}.",
            f"A pivotal moment for the {category} industry.",
            f"This development will shape {category} for years to come.",
            f"Industry transformation is underway in {category}.",
        ]
        return random.choice(takes)

    def _generate_analysis(self, facts: List[str]) -> str:
        """Generate analysis paragraph from facts."""
        if len(facts) < 2:
            return "This development marks an important turning point."
        return f"The convergence of these factors suggests a broader transformation ahead. {facts[-1]}"

    def compose(self,
                topic_title: str,
                facts: List[str],
                sources: List[Dict[str, str]],
                category: str = "tech") -> ComposedArticle:
        """
        Main compose method: Try LLM first, fall back to rule-based.
        """
        if self.use_local_llm and self.check_local_llm_available():
            article = self.compose_with_llm(topic_title, facts, sources)
            if article:
                return article
        
        return self.compose_with_fallback(topic_title, facts, sources, category)

    def to_dict(self, article: ComposedArticle) -> Dict:
        """Convert article to dictionary for JSON serialization."""
        return asdict(article)
