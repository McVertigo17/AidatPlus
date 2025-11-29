"""
Logging module for Aidat Plus application.
Provides structured logging with file and console handlers.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class AidatPlusLogger:
    """Custom logger class for Aidat Plus application."""
    
    def __init__(self, name: str = "AidatPlus", log_level: int = logging.INFO):
        """
        Initialize the logger with file and console handlers.
        
        Args:
            name: Logger name (typically module name)
            log_level: Minimum level to log
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Prevent adding handlers multiple times
        if not self.logger.handlers:
            self._setup_handlers(log_level)
    
    def _setup_handlers(self, log_level: int) -> None:
        """
        Setup file and console handlers for logging.
        
        Creates rotating file handler (10MB, 5 backups) and console handler.
        Applies different formatters for file and console output.
        
        Features:
            - UTF-8 encoding support for Turkish characters and emojis
            - Rotating file handler (max 10MB, keeps 5 backups)
            - Separate formatters for file and console output
            - Windows/Linux/macOS compatibility
        
        Args:
            log_level: Minimum logging level for handlers
        """
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        
        # File handler with rotation
        log_filename = f"logs/aidat_plus_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = RotatingFileHandler(
            log_filename, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'  # Unicode support for emoji and Turkish characters
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        
        # Console handler with UTF-8 encoding
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        # Set UTF-8 encoding for console (Windows compatibility)
        try:
            # Python 3.7+: reconfigure stream to UTF-8
            if hasattr(console_handler.stream, 'reconfigure'):
                console_handler.stream.reconfigure(encoding='utf-8')
            elif hasattr(console_handler.stream, 'buffer'):
                # Alternative: wrap with UTF-8 codec
                import io
                console_handler.setStream(
                    io.TextIOWrapper(console_handler.stream.buffer, encoding='utf-8')
                )
        except (AttributeError, UnicodeError, Exception):
            # Fallback: silent failure, use default encoding
            # File logging will still have UTF-8
            pass
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """
        Log debug message.
        
        Args:
            message: Debug message to log
        """
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """
        Log info message.
        
        Args:
            message: Info message to log
        """
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """
        Log warning message.
        
        Args:
            message: Warning message to log
        """
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """
        Log error message.
        
        Args:
            message: Error message to log
        """
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """
        Log critical message.
        
        Args:
            message: Critical message to log
        """
        self.logger.critical(message)


# Convenience functions for easy access
def get_logger(name: str = "AidatPlus") -> AidatPlusLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured AidatPlusLogger instance
    """
    return AidatPlusLogger(name)


# Global logger instance
logger = get_logger()


if __name__ == "__main__":
    # Example usage
    logger.info("Logger initialized successfully")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")