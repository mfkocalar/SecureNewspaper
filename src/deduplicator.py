"""Deduplicator to prevent duplicate articles in same session."""
import logging
from typing import List, Set
from .models import Article

logger = logging.getLogger(__name__)


class Deduplicator:
    """
    Session-based deduplicator using in-memory hash set.
    Clears on application start (same-day cache MVP).
    """
    
    def __init__(self):
        """Initialize deduplicator with empty hash set."""
        self.seen_hashes: Set[int] = set()
    
    def deduplicate(self, articles: List[Article]) -> List[Article]:
        """
        Filter articles, removing those already seen.
        
        Args:
            articles: List of Article objects
            
        Returns:
            List of unique articles (new ones only)
        """
        unique_articles = []
        duplicates_count = 0
        
        for article in articles:
            article_hash = hash(article)
            
            if article_hash in self.seen_hashes:
                duplicates_count += 1
                logger.debug(f"Duplicate detected: {article.title[:50]}...")
            else:
                self.seen_hashes.add(article_hash)
                unique_articles.append(article)
        
        if duplicates_count > 0:
            logger.info(f"Removed {duplicates_count} duplicate articles")
        
        return unique_articles
    
    def clear(self):
        """Clear the cache (for testing or session reset)."""
        self.seen_hashes.clear()
        logger.debug("Deduplicator cache cleared")
