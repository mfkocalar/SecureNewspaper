"""RSS feed fetcher with parallel processing."""
import feedparser
import logging
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
import time

from .models import Article, ParsedFeed
from .config import ConfigManager

logger = logging.getLogger(__name__)


class RSSFetcher:
    """Fetches articles from multiple RSS sources in parallel."""
    
    TIMEOUT_PER_SOURCE = 10  # seconds
    MAX_WORKERS = 4
    
    def __init__(self, config: ConfigManager, use_mock: bool = False):
        """Initialize fetcher with config.
        
        Args:
            config: ConfigManager instance
            use_mock: If True, use mock sources for testing
        """
        self.config = config
        self.lookback_hours = config.get_lookback_hours()
        self.use_mock = use_mock
    
    def fetch_all(self) -> List[ParsedFeed]:
        """
        Fetch from all enabled sources in parallel.
        
        Returns:
            List of ParsedFeed objects (one per source)
        """
        if self.use_mock:
            return self._fetch_mock()
        
        sources = self.config.get_sources()
        results = []
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = {
                executor.submit(self._fetch_source, source): source['name']
                for source in sources
            }
            
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    parsed_feed = future.result(timeout=self.TIMEOUT_PER_SOURCE)
                    results.append(parsed_feed)
                except Exception as e:
                    logger.error(f"Error fetching {source_name}: {e}")
                    results.append(ParsedFeed(source_name=source_name, error=str(e)))
        
        return results
    
    def _fetch_mock(self) -> List[ParsedFeed]:
        """Fetch mock articles for testing."""
        from test.mock_sources import MockRSSFetcher
        
        logger.info("Using mock RSS sources for testing")
        mock_articles = MockRSSFetcher.parse_mock_feed()
        
        # Replicate mock articles across all configured sources for demo
        sources = self.config.get_sources()
        results = []
        
        for source in sources:
            results.append(ParsedFeed(
                source_name=source['name'],
                articles=mock_articles.copy(),
                fetch_duration_seconds=0.1
            ))
        
        return results
    
    def _fetch_source(self, source: dict) -> ParsedFeed:
        """
        Fetch a single RSS source.
        
        Args:
            source: Dict with 'name' and 'url' keys
            
        Returns:
            ParsedFeed with articles or error
        """
        source_name = source['name']
        source_url = source['url']
        
        start_time = time.time()
        
        try:
            logger.debug(f"Fetching {source_name} from {source_url}")
            feed = feedparser.parse(source_url)
            
            if feed.bozo:
                logger.warning(f"{source_name}: Malformed feed (XML errors present)")
            
            articles = self._parse_entries(feed.entries, source_name)
            duration = time.time() - start_time
            
            logger.info(f"Fetched {source_name}: {len(articles)} articles ({duration:.2f}s)")
            
            return ParsedFeed(
                source_name=source_name,
                articles=articles,
                fetch_duration_seconds=duration
            )
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to fetch {source_name}: {e}")
            return ParsedFeed(
                source_name=source_name,
                error=str(e),
                fetch_duration_seconds=duration
            )
    
    def _parse_entries(self, entries: list, source_name: str) -> List[Article]:
        """
        Parse RSS entries into Article objects.
        
        Args:
            entries: List of feedparser entries
            source_name: Name of the source
            
        Returns:
            List of Article objects
        """
        articles = []
        lookback_threshold = datetime.now(timezone.utc) - timedelta(hours=self.lookback_hours)
        
        for entry in entries:
            try:
                # Extract title
                title = entry.get('title', '').strip()
                if not title:
                    continue
                
                # Extract URL
                url = entry.get('link', '').strip()
                if not url:
                    url = entry.get('id', '')
                if not url:
                    continue
                
                # Extract publish date
                pubdate = self._parse_pubdate(entry, lookback_threshold)
                if not pubdate:
                    continue
                
                # Check if within lookback window
                if pubdate < lookback_threshold:
                    continue
                
                # Extract description (summary)
                description = entry.get('summary', '') or entry.get('description', '')
                description = description.strip()
                # Remove HTML tags (basic)
                description = self._strip_html(description)
                
                article = Article(
                    title=title,
                    url=url,
                    source=source_name,
                    pubdate=pubdate,
                    description=description
                )
                articles.append(article)
            
            except Exception as e:
                logger.debug(f"Failed to parse entry from {source_name}: {e}")
                continue
        
        return articles
    
    def _parse_pubdate(self, entry: dict, fallback_time: datetime):
        """
        Extract and parse publication date from entry.
        
        Returns datetime in UTC or fallback time if unable to parse.
        """
        import email.utils
        from time import mktime
        
        # Try various date fields
        date_field = None
        for field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if field in entry and entry[field]:
                date_field = entry[field]
                break
        
        if date_field:
            try:
                dt = datetime.fromtimestamp(mktime(date_field), tz=None)
                return dt
            except Exception:
                pass
        
        # Try string parsing
        for field in ['published', 'updated', 'created']:
            if field in entry:
                try:
                    _, timestamp = email.utils.parsedate_tz(entry[field])
                    if timestamp is not None:
                        dt = datetime.utcfromtimestamp(timestamp)
                        return dt
                except Exception:
                    pass
        
        # Fallback: use current time (recent article)
        return datetime.now(timezone.utc)
    
    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text (basic)."""
        import re
        # Remove common HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        import html
        text = html.unescape(text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
