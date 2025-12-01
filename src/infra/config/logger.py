import sys
import os
from pathlib import Path
from loguru import logger
from abc import ABC, abstractmethod


class ILogger(ABC):
    """Logger interface."""
    
    @abstractmethod
    def get_logger(self):
        """
        Gets the configured logger.

        Returns:
            Logger: Logger instance
        """
        raise NotImplementedError
    
    @abstractmethod
    def configure(self) -> "LoggerConfig":
        """
        Configures the logger.

        Returns:
            LoggerConfig: Configured instance
        """
        raise NotImplementedError


class LoggerConfig(ILogger):
    """
    Centralized logger configuration using Loguru.
    Sets up handlers for console and file with automatic rotation.
    """
    
    def __init__(self, settings = None):
        """
        Initializes the logger configuration.

        Args:
            settings: Settings instance. If None, creates a new one.
        """
        self.settings = settings 
        self._logger = logger
        self._configured = False
    
    def configure(self) -> "LoggerConfig":
        """
        Configures the logger with handlers.

        Returns:
            LoggerConfig: Self for method chaining
        """
        if self._configured:
            return self
        
        self._logger.remove()
        
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        console_level = "DEBUG" if self.settings.debug else "INFO"
        file_level = "DEBUG"
        
        self._logger.add(
            sys.stderr,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                "Worker:{process} | {module}:{function}:{line} | {message}"
            ),
            level=console_level,
            colorize=True,
        )
        
        self._logger.add(
            os.path.join(log_dir, "app_{time:YYYY-MM-DD}.log"),
            rotation="5 MB",
            retention="10 days",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                "Worker:{process}[{thread}] | "
                "{module}:{function}:{line} | {message}"
            ),
            level=file_level,
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
        
        self._logger.add(
            os.path.join(log_dir, "errors_{time:YYYY-MM-DD}.log"),
            rotation="10 MB",
            retention="30 days",
            level="ERROR",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                "Worker:{process}[{thread}] | "
                "{module}:{function}:{line} | {message}"
            ),
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
        
        self._configured = True
        self._logger.info(
            f"Logger configured - Environment: {self.settings.environment}, "
            f"Debug: {self.settings.debug}"
        )
        
        return self
    
    def get_logger(self):
        """
        Gets the logger instance.

        Returns:
            Logger: Loguru logger instance
        """
        if not self._configured:
            self.configure()
        return self._logger
    
    @classmethod
    def create_default(cls):
        """
        Creates an instance with default configuration.

        Returns:
            LoggerConfig: Configured instance
        """
        return cls().configure()


