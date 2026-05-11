"""Main entry point and scheduler."""
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import ConfigManager
from .orchestrator import SecurityNewspaperPipeline

# Setup logging
def setup_logging():
    """Configure logging to file and console."""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "newspaper.log"
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


logger = setup_logging()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Security Newspaper - daily security news gazette"
    )
    parser.add_argument(
        '--now',
        action='store_true',
        help='Run pipeline immediately (don\'t schedule)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Use mock RSS sources for testing'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Format and display but don\'t publish to Slack'
    )
    parser.add_argument(
        '--config',
        default=None,
        help='Path to config.yaml (default: project root)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load config
        logger.info("Loading configuration...")
        config = ConfigManager(args.config)
        
        # Create pipeline
        pipeline = SecurityNewspaperPipeline(config, use_mock=args.test)
        
        if args.test:
            logger.warning("TEST MODE: Using mock RSS sources")
        
        # Run immediately or schedule
        if args.now:
            logger.info("Running pipeline immediately...")
            publish = not args.dry_run
            pipeline.run(publish=publish)
        else:
            logger.warning("DAEMON MODE: Running as background process (not recommended).")
            logger.warning("For production, use system cron instead:")
            logger.warning(f"  0 9 * * 1-5 cd /path/to/security-newspaper && /path/to/venv/bin/python -m src.main --now")
            logger.info("Starting scheduler...")
            
            # Setup scheduler
            scheduler = BackgroundScheduler()
            
            cron_expr = config.get_schedule_cron()
            timezone = config.get_schedule_timezone()
            
            logger.info(f"Schedule: {cron_expr} (timezone: {timezone})")
            
            # Parse cron expression
            trigger = CronTrigger.from_crontab(cron_expr, timezone=timezone)
            
            def scheduled_job():
                """Scheduled job callback."""
                logger.info(f"Scheduled job triggered at {datetime.now().isoformat()}")
                pipeline.run(publish=True)
            
            scheduler.add_job(
                scheduled_job,
                trigger=trigger,
                id='newspaper_job',
                name='Security Newspaper'
            )
            
            scheduler.start()
            logger.info("Scheduler started (daemon mode)")
            
            # Keep running
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("Shutting down scheduler...")
                scheduler.shutdown()
                logger.info("Scheduler stopped")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
