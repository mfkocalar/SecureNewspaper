"""Mock RSS sources for testing."""
import feedparser
from datetime import datetime, timedelta, timezone
from typing import List

from src.models import Article


class MockRSSFetcher:
    """Provides mock RSS data for testing without hitting real sources."""
    
    MOCK_FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Mock Security Feed</title>
    <link>https://example.com</link>
    <description>Mock feed for testing</description>
    
    <item>
      <title>APT29 Targeting European MFA Systems with New Bypass Technique</title>
      <link>https://example.com/1</link>
      <pubDate>{date1}</pubDate>
      <description>Researchers discovered a new attack campaign targeting multi-factor authentication systems used by European organizations. The threat actor is exploiting a vulnerability in legacy MFA protocols.</description>
    </item>
    
    <item>
      <title>CVE-2026-1234: Critical RCE Vulnerability in Apache Framework</title>
      <link>https://example.com/2</link>
      <pubDate>{date2}</pubDate>
      <description>A critical remote code execution vulnerability has been discovered in the Apache web framework affecting versions 2.4.0 through 2.4.57. Patch available now.</description>
    </item>
    
    <item>
      <title>Data Breach at TechCorp Exposes 5 Million Customer Records</title>
      <link>https://example.com/3</link>
      <pubDate>{date3}</pubDate>
      <description>TechCorp announced today that a breach compromised 5 million customer records including names, email addresses, and hashed passwords. The company is notifying affected users.</description>
    </item>
    
    <item>
      <title>Ransomware Gang LockBit Claims Attack on Fortune 500 Company</title>
      <link>https://example.com/4</link>
      <pubDate>{date4}</pubDate>
      <description>The LockBit ransomware gang has claimed responsibility for an attack on a major financial services company. Negotiations are ongoing for the release of encrypted data.</description>
    </item>
    
    <item>
      <title>New GDPR Regulations Impact Corporate Security Policies</title>
      <link>https://example.com/5</link>
      <pubDate>{date5}</pubDate>
      <description>The European regulators have released new GDPR enforcement guidelines that require enhanced security measures for data handling. Compliance deadline is 6 months from now.</description>
    </item>
    
    <item>
      <title>Kubernetes Audit Tool Released for Compliance Analysis</title>
      <link>https://example.com/6</link>
      <pubDate>{date6}</pubDate>
      <description>A new open-source tool has been released to audit Kubernetes deployments for security compliance issues. The tool scans for common misconfigurations and vulnerabilities.</description>
    </item>
    
    <item>
      <title>CISA Issues Alert on Actively Exploited Vulnerability</title>
      <link>https://example.com/7</link>
      <pubDate>{date7}</pubDate>
      <description>CISA has added a critical vulnerability to its list of actively exploited vulnerabilities affecting Windows systems. Immediate patching is recommended.</description>
    </item>
  </channel>
</rss>
"""
    
    @staticmethod
    def generate_mock_feed() -> str:
        """Generate mock RSS feed with recent dates."""
        now = datetime.now(timezone.utc)
        dates = [
            (now - timedelta(hours=i)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            for i in range(1, 8)
        ]
        
        feed_xml = MockRSSFetcher.MOCK_FEED_XML.format(
            date1=dates[0],
            date2=dates[1],
            date3=dates[2],
            date4=dates[3],
            date5=dates[4],
            date6=dates[5],
            date7=dates[6],
        )
        
        return feed_xml
    
    @staticmethod
    def parse_mock_feed() -> List[Article]:
        """Parse mock feed and return articles."""
        feed_xml = MockRSSFetcher.generate_mock_feed()
        feed = feedparser.parse(feed_xml)
        
        articles = []
        for entry in feed.entries:
            article = Article(
                title=entry.title,
                url=entry.link,
                source="Mock Source",
                pubdate=datetime.now(timezone.utc),
                description=entry.description
            )
            articles.append(article)
        
        return articles
