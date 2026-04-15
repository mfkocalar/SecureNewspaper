"""Main orchestrator - ties all modules together."""
import logging
from datetime import datetime, timezone
from typing import Optional
from .config import ConfigManager
from .fetcher import RSSFetcher
from .deduplicator import Deduplicator
from .classifier import ArticleClassifier
from .formatter import SlackFormatter
from .publisher import SlackPublisher
from .models import GazettePack

logger = logging.getLogger(__name__)


class SecurityNewspaperPipeline:
    """Complete pipeline: fetch → deduplicate → classify → format → publish."""
    
    def __init__(self, config: ConfigManager, use_mock: bool = False):
        """Initialize pipeline with config.
        
        Args:
            config: ConfigManager instance
            use_mock: If True, use mock RSS sources
        """
        self.config = config
        self.use_mock = use_mock
        self.fetcher = RSSFetcher(config, use_mock=use_mock)
        self.deduplicator = Deduplicator()
        self.classifier = ArticleClassifier(config)
        self.formatter = SlackFormatter(config)
        self.publisher = SlackPublisher(config)
    
    def run(self, publish: bool = True) -> Optional[GazettePack]:
        """
        Run complete pipeline.
        
        Args:
            publish: If True, publish to Slack. If False, just return formatted data.
            
        Returns:
            GazettePack with results, or None if failed
        """
        logger.info("=" * 60)
        logger.info("Starting Security Newspaper Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Fetch from all sources
        logger.info("Step 1: Fetching from RSS sources...")
        parsed_feeds = self.fetcher.fetch_all()
        
        # Aggregate articles
        all_articles = []
        sources_count = 0
        for feed in parsed_feeds:
            if feed.error:
                logger.warning(f"  {feed.source_name}: ERROR - {feed.error}")
            else:
                all_articles.extend(feed.articles)
                sources_count += 1
                logger.info(f"  {feed.source_name}: {len(feed.articles)} articles")
        
        logger.info(f"Fetched {len(all_articles)} total articles from {sources_count} sources")
        
        if not all_articles:
            logger.warning("No articles fetched, aborting pipeline")
            return None
        
        # Step 2: Deduplicate
        logger.info("Step 2: Deduplicating articles...")
        unique_articles = self.deduplicator.deduplicate(all_articles)
        logger.info(f"After dedup: {len(unique_articles)} unique articles")
        
        if not unique_articles:
            logger.warning("No unique articles, aborting pipeline")
            return None
        
        # Step 3: Classify
        logger.info("Step 3: Classifying articles into sections...")
        classified = self.classifier.classify(unique_articles)
        
        # Step 4: Create gazette pack
        logger.info("Step 4: Creating gazette pack...")
        gazette_pack = GazettePack(
            articles_by_section=classified,
            total_articles=len(unique_articles),
            sources_count=sources_count,
            publish_time=datetime.now(timezone.utc)
        )
        
        # Step 5: Format for Slack
        logger.info("Step 5: Formatting for Slack...")
        formatted = self.formatter.format_gazette(gazette_pack)
        
        # Step 6: Publish (optional)
        if publish:
            logger.info("Step 6: Publishing to Slack...")
            success = self.publisher.publish(formatted)
            if not success:
                logger.error("Failed to publish to Slack")
                return None
        else:
            logger.info("Step 6: Skipped publishing (dry-run mode)")
        
        logger.info("=" * 60)
        logger.info("Pipeline completed successfully")
        logger.info("=" * 60)
        
        return gazette_pack
