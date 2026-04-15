"""Data models for the Security Newspaper."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List


@dataclass
class Article:
    """Represents a single security news article."""
    title: str
    url: str
    source: str
    pubdate: datetime
    description: str
    section: str = "INDUSTRY_POLICY"  # Default section
    
    def __hash__(self):
        """Hash based on title + url for deduplication."""
        return hash((self.title, self.url))
    
    def __eq__(self, other):
        """Equality based on title + url."""
        if not isinstance(other, Article):
            return False
        return self.title == other.title and self.url == other.url


@dataclass
class ParsedFeed:
    """Result of parsing a single RSS feed."""
    source_name: str
    articles: List[Article] = field(default_factory=list)
    error: Optional[str] = None
    fetch_duration_seconds: float = 0.0


@dataclass
class GazettePack:
    """Complete newspaper ready for publishing."""
    articles_by_section: dict  # {section_name: [Article, ...]}
    total_articles: int
    sources_count: int
    publish_time: datetime
    sections_order: List[str] = field(
        default_factory=lambda: [
            "THREAT_INTELLIGENCE",
            "VULNERABILITIES",
            "BREACHES",
            "RANSOMWARE",
            "INDUSTRY_POLICY",
            "TOOLS_TECHNIQUES",
            "ADVISORIES",
        ]
    )
