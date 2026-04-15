"""Publisher - sends formatted gazette to Slack."""
import logging
import json
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .config import ConfigManager

logger = logging.getLogger(__name__)


class SlackPublisher:
    """Publishes formatted gazette to Slack webhook."""
    
    def __init__(self, config: ConfigManager):
        """Initialize publisher with config."""
        self.config = config
        self.webhook_url = config.get_slack_webhook_url()
    
    def publish(self, blocks_data: dict) -> bool:
        """
        Publish gazette to Slack.
        
        Args:
            blocks_data: Dict with 'blocks' key from SlackFormatter
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import here to avoid dependency issues if not using webhooks
            import requests
            
            response = requests.post(
                self.webhook_url,
                json=blocks_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Gazette published to Slack successfully")
                return True
            else:
                logger.error(
                    f"Slack webhook returned {response.status_code}: {response.text}"
                )
                return False
        
        except Exception as e:
            logger.error(f"Failed to publish to Slack: {e}")
            return False
