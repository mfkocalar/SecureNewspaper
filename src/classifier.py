"""Article classifier - assigns articles to sections based on keywords."""
import re
import logging
from typing import List, Dict
from .models import Article
from .config import ConfigManager

logger = logging.getLogger(__name__)


class ArticleClassifier:
    """Classifies articles into sections using regex-based keyword matching."""
    
    def __init__(self, config: ConfigManager):
        """
        Initialize classifier with config.
        
        Args:
            config: ConfigManager instance
        """
        self.config = config
        # Precompile regexes for performance
        self.section_regexes: Dict[str, List[re.Pattern]] = {}
        self._compile_regexes()
    
    def _compile_regexes(self):
        """Precompile regex patterns from config."""
        for section_name in self.config.get_all_section_names():
            section_config = self.config.get_section_config(section_name)
            keywords = section_config.get('keywords', [])
            
            patterns = []
            for keyword in keywords:
                try:
                    # Case-insensitive regex
                    pattern = re.compile(keyword, re.IGNORECASE)
                    patterns.append(pattern)
                except re.error as e:
                    logger.error(f"Invalid regex in {section_name}: {keyword} - {e}")
            
            self.section_regexes[section_name] = patterns
    
    def classify(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """
        Classify articles into sections.
        
        Args:
            articles: List of Article objects
            
        Returns:
            Dict mapping section_name -> List[Article]
        """
        # Initialize all sections
        classified = {section: [] for section in self.config.get_all_section_names()}
        
        for article in articles:
            section = self._classify_single(article)
            classified[section].append(article)
            logger.debug(f"Classified '{article.title[:40]}...' to {section}")
        
        # Log summary
        for section, items in classified.items():
            if items:
                logger.info(f"{section}: {len(items)} articles")
        
        return classified
    
    def _classify_single(self, article: Article) -> str:
        """
        Classify a single article.
        
        Args:
            article: Article to classify
            
        Returns:
            Section name (or default if no match)
        """
        # Search text: title + description
        search_text = f"{article.title} {article.description}"
        
        # Check each section in order
        for section_name in self.config.get_all_section_names():
            patterns = self.section_regexes.get(section_name, [])
            
            for pattern in patterns:
                if pattern.search(search_text):
                    return section_name
        
        # Default to INDUSTRY_POLICY if no match
        return "INDUSTRY_POLICY"
