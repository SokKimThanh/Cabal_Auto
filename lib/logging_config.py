"""Logging configuration for Cabal Auto Hunt."""

import logging
import logging.handlers
from pathlib import Path
import sys


def setup_logging(log_level=logging.INFO, rotation_type='size'):
    """
    Setup application-wide logging configuration.
    
    Args:
        log_level: Logging level (default: INFO)
        rotation_type: 'size' (rotate by 5MB) or 'daily' (rotate at midnight)
    
    Features:
    - Console output with UTF-8 encoding
    - File logging to logs/app.log
    - Automatic rotation by size or daily
    """
    
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    # Fix encoding for Windows console
    if hasattr(console_handler, 'setEncoding'):
        console_handler.setEncoding('utf-8')
    
    # File handler - choose rotation type
    if rotation_type == 'daily':
        # Rotate at midnight, keep 7 days of logs
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_dir / "app.log",
            when='midnight',  # Rotate at midnight
            interval=1,       # Every day
            backupCount=7,    # Keep 7 days of logs
            encoding='utf-8'
        )
        file_handler.suffix = "%Y-%m-%d"  # Format: app.log.2026-09-07
    else:
        # Default: Rotate by size (5MB)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,         # Keep 3 backup files
            encoding='utf-8'
        )
    
    file_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Log startup
    root_logger.info("="*60)
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log directory: {log_dir}")
    root_logger.info(f"Log level: {logging.getLevelName(log_level)}")
    root_logger.info("="*60)


if __name__ == "__main__":
    # Test logging with daily rotation (keep 7 days)
    setup_logging(logging.DEBUG, rotation_type='daily')
    
    logger = logging.getLogger(__name__)
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    
    print("\n✓ Test complete! Check logs/app.log")
    print("  Rotation type: DAILY (keep 7 days)")
    print("  Check: app.log, app.log.2026-09-06, app.log.2026-09-05, etc.")
