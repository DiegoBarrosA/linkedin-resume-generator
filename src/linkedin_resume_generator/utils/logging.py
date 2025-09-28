"""Logging utilities for LinkedIn Resume Generator."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

import structlog
import colorlog

from ..config.settings import LoggingConfig


class Logger:
    """Centralized logging configuration."""
    
    _initialized = False
    _logger = None
    
    @classmethod
    def setup(cls, config: LoggingConfig) -> None:
        """Setup structured logging with colorization."""
        if cls._initialized:
            return
            
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="ISO"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Setup console handler with color
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s: %(message)s",
                datefmt=None,
                reset=True,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
                secondary_log_colors={},
                style='%'
            )
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.level))
        root_logger.addHandler(console_handler)
        
        # Add file handler if enabled
        if config.file_enabled and config.file_path:
            file_handler = logging.handlers.RotatingFileHandler(
                config.file_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_formatter = logging.Formatter(config.format)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
        cls._logger = structlog.get_logger("linkedin_resume_generator")
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> structlog.BoundLogger:
        """Get a logger instance."""
        if not cls._initialized:
            # Initialize with defaults if not already done
            from ..config.settings import LoggingConfig
            cls.setup(LoggingConfig())
        
        if name:
            return structlog.get_logger(name)
        return cls._logger or structlog.get_logger("linkedin_resume_generator")


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Convenience function to get a logger."""
    return Logger.get_logger(name)