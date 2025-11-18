"""
LocalNewsAgent Main Orchestrator
Runs the full A->F workflow: Discovery -> Extraction -> Composition -> QA -> Output
"""
# pylint: disable=unused-import

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import modules
from src.discovery import DiscoveryEngine
from src.extractor import ContentExtractor
from src.composer import ArticleComposer
from src.qa import QAValidator
from src.output import OutputManager


def setup_logging(log_file: Optional[str] = None):
    """Configure logging for the entire application."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler()]
        )


def run_discovery(rss_file: str = 'rss_feeds.txt',
                  sites_file: str = 'sites.txt',
                  queries: Optional[list] = None,
                  log_file: Optional[str] = None,
                  top_count: int = 5) -> list:
    """A. Discovery Phase: Find trending topics."""
    print("\n" + "="*80)
    print("PHASE A: DISCOVERY")
    print("="*80)
    
    engine = DiscoveryEngine(log_file=log_file)
    topics = engine.discover_all(
        rss_file=rss_file,
        sites_file=sites_file,
        queries=queries
    )
    
    top_topics = engine.get_top_topics(top_count)
    
    print(f"\nDiscovered {len(topics)} topics. Top {len(top_topics)} by trend score:")
    for i, topic in enumerate(top_topics, 1):
        print(f"  {i}. {topic.title_hint[:60]}")
        print(f"     Source: {topic.source_name} | Score: {topic.trend_score:.1f}")
    
    return top_topics


def run_extraction(topics: list,
                   log_file: Optional[str] = None) -> dict:
    """B. Fact Extraction Phase: Extract facts from sources."""
    print("\n" + "="*80)
    print("PHASE B: FACT EXTRACTION")
    print("="*80)
    
    extractor = ContentExtractor(log_file=log_file)
    
    extraction_data = {}
    for topic in topics:
        print(f"\nExtracting from: {topic.title_hint[:60]}")
        article = extractor.extract(topic.source_url)
        
        if article:
            if article.is_paywalled:
                print("  ⚠ Paywalled - skipping")
                continue
            
            extraction_data[topic.title_hint] = {
                'topic': topic,
                'article': article,
                'facts': article.bullet_facts,
                'sources': [
                    {'name': topic.source_name, 'url': topic.source_url}
                ]
            }
            print(f"  ✓ Extracted {len(article.bullet_facts)} bullet facts")
        else:
            print("  ✗ Failed to extract")
    
    print(f"\nExtracted data for {len(extraction_data)} topics")
    return extraction_data


def run_composition(extraction_data: dict,
                    use_llm: bool = True,
                    log_file: Optional[str] = None) -> dict:
    """C. Article Composition Phase: Generate articles."""
    print("\n" + "="*80)
    print("PHASE C: ARTICLE COMPOSITION")
    print("="*80)
    
    composer = ArticleComposer(use_local_llm=use_llm, log_file=log_file)
    
    composed_articles = {}
    for title_hint, data in extraction_data.items():
        print(f"\nComposing: {title_hint[:60]}")
        
        article = composer.compose(
            topic_title=title_hint,
            facts=data['facts'],
            sources=data['sources'],
            category='tech'
        )
        
        composed_articles[title_hint] = article
        print(f"  ✓ Generated {article.word_count} words")
        print(f"    Slug: {article.slug}")
        print(f"    Title: {article.seo_title}")
    
    return composed_articles


def run_qa(composed_articles: dict,
           min_word_count: int = 800,
           log_file: Optional[str] = None) -> dict:
    """E. QA & Validation Phase: Check quality."""
    print("\n" + "="*80)
    print("PHASE E: QA & VALIDATION")
    print("="*80)
    
    validator = QAValidator(min_word_count=min_word_count, log_file=log_file)
    
    qa_results = {}
    for title, article in composed_articles.items():
        print(f"\nValidating: {title[:60]}")
        
        # Prepare texts for validation
        article_text = article.article_html
        source_texts = [f["main_excerpt"] for f in [article]]
        
        result = validator.validate_article(
            article_text=article_text,
            article_html=article.article_html,
            source_texts=source_texts,
            has_our_take=True,
            has_sources_section=True
        )
        
        qa_results[title] = {
            'article': article,
            'qa_result': result
        }
        
        status = "✓ PASSED" if result.passed else "✗ FAILED"
        print(f"  {status}")
        print(validator.get_qa_report(result))
    
    return qa_results


def run_output(qa_results: dict,
               drafts_dir: str = './drafts',
               published_dir: str = './published',
               logs_dir: str = './logs') -> dict:
    """F. Output Phase: Save files."""
    print("\n" + "="*80)
    print("PHASE F: OUTPUT & SAVE")
    print("="*80)
    
    output_manager = OutputManager(
        drafts_dir=drafts_dir,
        published_dir=published_dir,
        logs_dir=logs_dir
    )
    
    saved_files = {}
    for title, data in qa_results.items():
        article = data['article']
        qa_result = data['qa_result']
        
        print(f"\nSaving: {article.slug}")
        
        # Convert to dict
        from dataclasses import asdict as dc_asdict
        article_dict = dc_asdict(article)
        
        # Save JSON draft
        json_path = output_manager.save_draft(article_dict, article.slug)
        print(f"  ✓ JSON: {Path(json_path).name}")
        
        # Save HTML
        html_path = output_manager.save_html(article_dict, article.slug)
        print(f"  ✓ HTML: {Path(html_path).name}")
        
        # Save session log
        session_data = {
            'topic': title,
            'word_count': article.word_count,
            'qa_status': 'PASSED' if qa_result.passed else 'FAILED',
            'adsense_safe': qa_result.is_adsense_safe,
            'qa_issues': qa_result.issues,
            'sources_used': article.sources,
            'saved_files': [json_path, html_path],
            'llm_used': 'Local LLM' if article.image_prompt_main else 'Fallback'
        }
        log_path = output_manager.save_session_log(article.slug, session_data)
        print(f"  ✓ Log: {Path(log_path).name}")
        
        saved_files[article.slug] = {
            'json': json_path,
            'html': html_path,
            'log': log_path
        }
    
    return saved_files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LocalNewsAgent: Autonomous local news publishing system'
    )
    parser.add_argument(
        '--top-topics',
        type=int,
        default=3,
        help='Number of top topics to process (default: 3)'
    )
    parser.add_argument(
        '--min-words',
        type=int,
        default=800,
        help='Minimum article word count (default: 800)'
    )
    parser.add_argument(
        '--rss-file',
        default='rss_feeds.txt',
        help='RSS feeds config file (default: rss_feeds.txt)'
    )
    parser.add_argument(
        '--sites-file',
        default='sites.txt',
        help='Sites config file (default: sites.txt)'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip local LLM and use fallback generation'
    )
    parser.add_argument(
        '--queries',
        nargs='+',
        help='Additional SERP queries (e.g., --queries "AI news" "Tech trends")'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = f"./logs/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    Path('./logs').mkdir(parents=True, exist_ok=True)
    setup_logging(log_file)
    
    logger = logging.getLogger("LocalNewsAgent")
    logger.info("LocalNewsAgent started")
    logger.info(f"Config: top_topics={args.top_topics}, min_words={args.min_words}")
    
    print("\n" + "█"*80)
    print("  LOCALNEWSAGENT v1.0 - Autonomous Local News Publishing")
    print("█"*80)
    
    try:
        # A. Discovery
        topics = run_discovery(
            rss_file=args.rss_file,
            sites_file=args.sites_file,
            queries=args.queries,
            log_file=log_file,
            top_count=args.top_topics
        )
        
        if not topics:
            print("\n✗ No topics discovered. Exiting.")
            return 1
        
        # B. Extraction
        extraction_data = run_extraction(topics, log_file=log_file)
        
        if not extraction_data:
            print("\n✗ No data extracted. Exiting.")
            return 1
        
        # C. Composition
        composed_articles = run_composition(
            extraction_data,
            use_llm=not args.no_llm,
            log_file=log_file
        )
        
        # E. QA
        qa_results = run_qa(
            composed_articles,
            min_word_count=args.min_words,
            log_file=log_file
        )
        
        # F. Output
        saved_files = run_output(qa_results)
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total articles processed: {len(saved_files)}")
        print(f"Session log: {log_file}")
        print("\nPublish-ready drafts saved to ./drafts/")
        for slug, _ in saved_files.items():
            print(f"  - {slug}")
        
        logger.info("LocalNewsAgent completed successfully")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
