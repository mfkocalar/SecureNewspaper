"""Slack Block Kit formatter for newspaper-style gazette."""
import logging
from datetime import datetime
from typing import List, Dict
from .models import Article, GazettePack
from .config import ConfigManager

logger = logging.getLogger(__name__)


class SlackFormatter:
    """Formats articles into Slack Block Kit JSON for rich newspaper display."""
    
    MAX_BLOCKS = 50  # Safety limit (Slack allows ~100)
    DESCRIPTION_TRUNCATE = 150  # chars
    TITLE_TRUNCATE = 100  # chars
    
    def __init__(self, config: ConfigManager):
        """Initialize formatter with config."""
        self.config = config
    
    def format_gazette(self, gazette_pack: GazettePack) -> dict:
        """
        Format gazette into Slack Block Kit JSON.
        
        Args:
            gazette_pack: GazettePack with articles grouped by section
            
        Returns:
            Dict with 'blocks' key containing Block Kit JSON
        """
        blocks = []
        
        # Header
        blocks.extend(self._build_header(gazette_pack))
        
        # Sections with articles
        for section_name in gazette_pack.sections_order:
            articles = gazette_pack.articles_by_section.get(section_name, [])
            if not articles:
                continue
            
            # Section header
            section_config = self.config.get_section_config(section_name)
            emoji = section_config.get('emoji', '📌')
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{emoji} {section_name}*"
                }
            })
            
            # Articles in section (up to max_items_per_section)
            max_items = self.config.get_max_items_per_section()
            for article in articles[:max_items]:
                blocks.extend(self._build_article_blocks(article))
            
            # Divider between sections
            blocks.append({"type": "divider"})
            
            # Stop if approaching max blocks
            if len(blocks) >= self.MAX_BLOCKS - 5:
                logger.warning(f"Approaching Slack block limit ({len(blocks)}/{self.MAX_BLOCKS})")
                break
        
        # Footer
        blocks.extend(self._build_footer(gazette_pack))
        
        logger.info(f"Formatted gazette with {len(blocks)} blocks")
        
        return {"blocks": blocks}
    
    def _build_header(self, gazette_pack: GazettePack) -> List[dict]:
        """Build header blocks."""
        date_str = gazette_pack.publish_time.strftime("%d %B %Y")
        newspaper_name = self.config.get_newspaper_name()
        
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📰 {newspaper_name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_{date_str}_ • {gazette_pack.total_articles} stories • {gazette_pack.sources_count} sources"
                }
            },
            {"type": "divider"}
        ]
    
    def _build_article_blocks(self, article: Article) -> List[dict]:
        """Build article display blocks."""
        # Truncate title if needed
        title = article.title
        if len(title) > self.TITLE_TRUNCATE:
            title = title[:self.TITLE_TRUNCATE] + "…"
        
        # Truncate description if needed
        description = article.description
        if len(description) > self.DESCRIPTION_TRUNCATE:
            description = description[:self.DESCRIPTION_TRUNCATE] + "…"
        
        # Build article section
        article_text = f"*<{article.url}|{title}>*\n{description}\n"
        article_text += f"_via {article.source}_"
        
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": article_text
                }
            }
        ]
    
    def _build_footer(self, gazette_pack: GazettePack) -> List[dict]:
        """Build footer blocks."""
        time_str = gazette_pack.publish_time.strftime("%H:%M UTC")
        
        return [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Generated at {time_str} by Security Newspaper"
                    }
                ]
            }
        ]
