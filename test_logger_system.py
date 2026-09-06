#!/usr/bin/env python3
"""Test logger system to verify it's working correctly."""

import logging
import sys
from pathlib import Path

# Setup logging config
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / 'logs' / 'test_logger.log')
    ]
)

logger = logging.getLogger(__name__)

def test_logger():
    """Test various logger levels."""
    logger.debug("🔵 This is a DEBUG message")
    logger.info("🟢 This is an INFO message")
    logger.warning("🟡 This is a WARNING message")
    logger.error("🔴 This is an ERROR message")
    
    print("\n" + "="*60)
    print("✓ Logger test completed!")
    print("="*60)

def test_submodule_logger():
    """Test logger from different module."""
    from ui.components.compact_window_selector import logger as selector_logger
    from ui.controllers.app_window_controller import logger as controller_logger
    from lib.system.window_manager import logger as manager_logger
    
    print("\n" + "="*60)
    print("Testing SubModule Loggers:")
    print("="*60)
    
    selector_logger.info("✓ CompactWindowSelector logger works")
    controller_logger.info("✓ AppWindowController logger works")
    manager_logger.info("✓ WindowManager logger works")
    
    print("\n✓ All submodule loggers working!\n")

if __name__ == "__main__":
    test_logger()
    test_submodule_logger()
