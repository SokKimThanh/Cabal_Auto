"""
Hunt Logger - Enhanced logging system for Hunt operations.

Features:
- File-based logging với rotating log files
- Structured logging: timestamp, event type, template name, coordinates, confidence
- Separate logs per session
- Log rotation khi file quá lớn (10MB)
- Keep last 5 log files
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import json


class HuntLogger:
    """Enhanced logger for Hunt operations."""
    
    def __init__(self, log_dir='logs', max_bytes=10*1024*1024, backup_count=5):
        """
        Initialize Hunt Logger.
        
        Args:
            log_dir: Directory to store log files
            max_bytes: Max size per log file (default 10MB)
            backup_count: Number of backup files to keep
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('HuntLogger')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create rotating file handler
        log_file = self.log_dir / 'hunt.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Session start
        self.session_start = datetime.now()
        self.logger.info('='*80)
        self.logger.info(f'Hunt Session Started: {self.session_start.strftime("%Y-%m-%d %H:%M:%S")}')
        self.logger.info('='*80)
    
    def log_match(self, template_name, box, threshold=None, confidence=None, monster_name=None):
        """
        Log template match event.
        
        Args:
            template_name: Name of matched template
            box: Match box (left, top, width, height)
            threshold: Threshold used
            confidence: Match confidence (if available)
            monster_name: Monster name (if available)
        """
        center_x = box[0] + box[2] // 2 if box else None
        center_y = box[1] + box[3] // 2 if box else None
        
        info = {
            'event': 'MATCH',
            'template': template_name,
            'monster': monster_name,
            'box': {'left': box[0], 'top': box[1], 'width': box[2], 'height': box[3]} if box else None,
            'center': {'x': center_x, 'y': center_y} if center_x else None,
            'threshold': threshold,
            'confidence': confidence
        }
        
        msg = f"[MATCH] Template: {template_name}"
        if monster_name:
            msg += f" | Monster: {monster_name}"
        if box:
            msg += f" | Box: ({box[0]}, {box[1]}, {box[2]}, {box[3]})"
            msg += f" | Center: ({center_x}, {center_y})"
        if threshold:
            msg += f" | Threshold: {threshold:.2f}"
        if confidence:
            msg += f" | Confidence: {confidence:.2f}"
        
        self.logger.info(msg)
        self._log_structured(info)
    
    def log_lost(self, template_name=None, monster_name=None, duration=None):
        """
        Log target lost event.
        
        Args:
            template_name: Template being searched
            monster_name: Monster name
            duration: How long target was tracked before lost
        """
        info = {
            'event': 'LOST',
            'template': template_name,
            'monster': monster_name,
            'duration': duration
        }
        
        msg = f"[LOST] Target lost"
        if template_name:
            msg += f" | Template: {template_name}"
        if monster_name:
            msg += f" | Monster: {monster_name}"
        if duration:
            msg += f" | Tracked for: {duration:.1f}s"
        
        self.logger.info(msg)
        self._log_structured(info)
    
    def log_state_change(self, old_state, new_state, reason=None):
        """
        Log hunt state change (search <-> attack).
        
        Args:
            old_state: Previous state
            new_state: New state
            reason: Reason for state change
        """
        info = {
            'event': 'STATE_CHANGE',
            'old_state': old_state,
            'new_state': new_state,
            'reason': reason
        }
        
        msg = f"[STATE] {old_state} → {new_state}"
        if reason:
            msg += f" | Reason: {reason}"
        
        self.logger.info(msg)
        self._log_structured(info)
    
    def log_hunt_start(self, config):
        """
        Log hunt session start with configuration.
        
        Args:
            config: Hunt configuration dict
        """
        info = {
            'event': 'HUNT_START',
            'config': {
                'window_title': config.get('window_title'),
                'target_key': config.get('target_key'),
                'attack_keys': config.get('attack_keys'),
                'search_interval': config.get('search_interval'),
                'attack_interval': config.get('attack_interval'),
                'lost_timeout_sec': config.get('lost_timeout_sec'),
                'attack_min_duration_sec': config.get('attack_min_duration_sec'),
                'template_count': len(config.get('templates', [])),
            }
        }
        
        self.logger.info('[START] Hunt started')
        self.logger.info(f"Window: {config.get('window_title')}")
        self.logger.info(f"Templates: {len(config.get('templates', []))} configured")
        self.logger.info(f"Timing: search={config.get('search_interval')}s, attack={config.get('attack_interval')}s")
        self._log_structured(info)
    
    def log_hunt_stop(self, reason='manual'):
        """
        Log hunt session stop.
        
        Args:
            reason: Reason for stopping (manual, error, etc.)
        """
        duration = (datetime.now() - self.session_start).total_seconds()
        
        info = {
            'event': 'HUNT_STOP',
            'reason': reason,
            'duration_sec': duration
        }
        
        self.logger.info(f'[STOP] Hunt stopped | Reason: {reason} | Duration: {duration:.1f}s')
        self.logger.info('='*80)
        self._log_structured(info)
    
    def log_error(self, error_type, message, exception=None):
        """
        Log error event.
        
        Args:
            error_type: Type of error
            message: Error message
            exception: Exception object (if available)
        """
        info = {
            'event': 'ERROR',
            'error_type': error_type,
            'message': message,
            'exception': str(exception) if exception else None
        }
        
        self.logger.error(f'[ERROR] {error_type}: {message}')
        if exception:
            self.logger.error(f'Exception: {exception}')
        self._log_structured(info)
    
    def log_info(self, message):
        """Log general info message."""
        self.logger.info(message)
    
    def log_debug(self, message):
        """Log debug message."""
        self.logger.debug(message)
    
    def _log_structured(self, data):
        """
        Log structured data as JSON for parsing.
        
        Args:
            data: Dict of structured data
        """
        # Write to separate structured log file
        structured_log = self.log_dir / 'hunt_structured.jsonl'
        try:
            with open(structured_log, 'a', encoding='utf-8') as f:
                data['timestamp'] = datetime.now().isoformat()
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.debug(f'Failed to write structured log: {e}')


# Global logger instance
_hunt_logger = None


def get_hunt_logger():
    """Get or create global hunt logger instance."""
    global _hunt_logger
    if _hunt_logger is None:
        _hunt_logger = HuntLogger()
    return _hunt_logger


def reset_hunt_logger():
    """Reset global hunt logger (for new session)."""
    global _hunt_logger
    _hunt_logger = None


if __name__ == '__main__':
    # Test logging
    logger = HuntLogger()
    
    logger.log_hunt_start({
        'window_title': 'CABAL',
        'target_key': 'z',
        'attack_keys': ['1', '2', '3'],
        'search_interval': 0.2,
        'attack_interval': 0.15,
        'lost_timeout_sec': 1.2,
        'attack_min_duration_sec': 1.5,
        'templates': [{'name': 'test1'}, {'name': 'test2'}]
    })
    
    logger.log_state_change('search', 'attack', 'Target found')
    
    logger.log_match(
        template_name='goc-45',
        box=(100, 200, 50, 60),
        threshold=0.85,
        confidence=0.92,
        monster_name='Coc go~'
    )
    
    logger.log_lost(template_name='goc-45', monster_name='Coc go~', duration=5.3)
    
    logger.log_state_change('attack', 'search', 'Target lost timeout')
    
    logger.log_hunt_stop('manual')
