"""Configuration loader and validator."""
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Loads and validates config.yaml."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize config manager.
        
        Args:
            config_path: Path to config.yaml. If None, looks in project root.
        """
        if config_path is None:
            # Look for config.yaml in the project root
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load and validate config.yaml."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self._validate_config()
        self._expand_env_vars()
        logger.info(f"Config loaded from {self.config_path}")
    
    def _expand_env_vars(self):
        """Expand environment variables in config (${VAR_NAME})."""
        webhook_url = self.config.get('slack', {}).get('webhook_url', '')
        if webhook_url and webhook_url.startswith('${') and webhook_url.endswith('}'):
            env_var = webhook_url[2:-1]  # Extract VAR_NAME from ${VAR_NAME}
            expanded = os.getenv(env_var)
            if not expanded:
                raise ValueError(
                    f"Environment variable '{env_var}' not set. "
                    f"Set it via: export {env_var}='https://hooks.slack.com/...'"
                )
            self.config['slack']['webhook_url'] = expanded
    
    def _validate_config(self):
        """Validate required config fields."""
        required_sections = ['schedule', 'slack', 'sources', 'sections']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Check Slack webhook
        webhook = self.config['slack'].get('webhook_url', '').strip()
        if webhook.startswith('${'):
            # Will be expanded in _expand_env_vars
            pass
        elif not webhook:
            raise ValueError("Slack webhook_url must be set")
        
        # Check sources
        sources = self.config.get('sources', [])
        if not sources:
            raise ValueError("At least one source must be configured")
        
        for i, source in enumerate(sources):
            if not source.get('name') or not source.get('url'):
                raise ValueError(f"Source {i} must have 'name' and 'url'")
    
    def get_schedule_cron(self) -> str:
        """Get cron expression."""
        return self.config['schedule']['cron']
    
    def get_schedule_timezone(self) -> str:
        """Get timezone."""
        return self.config['schedule'].get('timezone', 'UTC')
    
    def get_lookback_hours(self) -> int:
        """Get lookback period in hours."""
        return self.config['schedule'].get('lookback_hours', 24)
    
    def get_max_items_per_section(self) -> int:
        """Get max articles per section."""
        return self.config['schedule'].get('max_items_per_section', 5)
    
    def get_slack_webhook_url(self) -> str:
        """Get Slack webhook URL."""
        return self.config['slack']['webhook_url']
    
    def get_newspaper_name(self) -> str:
        """Get newspaper name."""
        return self.config['slack'].get('newspaper_name', 'The Security Gazette')
    
    def get_sources(self) -> List[Dict[str, Any]]:
        """Get list of RSS sources."""
        return [s for s in self.config.get('sources', []) if s.get('enabled', True)]
    
    def get_section_config(self, section_name: str) -> Dict[str, Any]:
        """Get section configuration (emoji, keywords)."""
        return self.config['sections'].get(section_name, {})
    
    def get_all_section_names(self) -> List[str]:
        """Get all section names in order."""
        return list(self.config['sections'].keys())
