"""DARKWIN Logging System Configuration

Provides centralized logging with both console (Rich) and file output.
Supports scan-specific logging and rotating file handlers for log management.

Features:
    - Rich console output with syntax highlighting
    - Rotating file handlers to prevent disk space issues
    - Scan-specific log files for detailed per-scan tracking
    - Configurable log levels and formatting
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from rich.logging import RichHandler

# Constants
LOG_DIR: Path = Path("logs")
SCAN_LOG_DIR: Path = LOG_DIR / "scans"
MAIN_LOG_FILE: Path = LOG_DIR / "darkwin.log"
MAX_LOG_SIZE: int = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT: int = 5
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Add SUCCESS level
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)

logging.Logger.success = success


def get_logger(name: str, scan_id: Optional[str] = None) -> logging.Logger:
    """Get a configured logger with console and file output.
    
    Creates or retrieves a logger with Rich console handler and rotating
    file handler. If scan_id provided, also creates scan-specific log file.
    
    Args:
        name: Logger name (typically __name__ or module name).
        scan_id: Optional scan ID for per-scan log files.
        
    Returns:
        Configured logging.Logger instance.
        
    Note:
        Logger is cached after first creation. Subsequent calls return
        existing logger to avoid duplicate handlers.
    """
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Skip if already configured (prevent duplicate handlers)
    if logger.handlers:
        return logger

    # Console Handler (Rich for pretty output)
    from rich.console import Console
    # Explicitly set force_terminal if needed or handle encoding
    rich_console = Console(force_terminal=True) if os.name == 'nt' else None
    
    console_handler: RichHandler = RichHandler(
        console=rich_console,
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=False,
    )
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # Create log directory if needed
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Main Log File (Rotating)
    global _permission_warning_shown
    if '_permission_warning_shown' not in globals():
        _permission_warning_shown = False

    try:
        file_handler: RotatingFileHandler = RotatingFileHandler(
            MAIN_LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_formatter: logging.Formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except PermissionError:
        if not _permission_warning_shown:
            print(f"[bold red]❌ CRITICAL: Permission denied on {MAIN_LOG_FILE}[/bold red]")
            if os.name == 'nt':
                print("[yellow]Please run your terminal as Administrator or check folder permissions for:[/yellow]")
                print(f"  {LOG_DIR.absolute()}")
            else:
                print("[yellow]Please fix log permissions by running:[/yellow]")
                print(f"sudo chown -R $USER:$USER {LOG_DIR}")
                print(f"sudo chmod -R 775 {LOG_DIR}")
            _permission_warning_shown = True
        # We continue without file logging rather than crashing

    # Scan-specific logger (if scan_id provided)
    if scan_id:
        SCAN_LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        scan_log_file: Path = SCAN_LOG_DIR / f"{scan_id}.log"
        scan_handler: logging.FileHandler = logging.FileHandler(scan_log_file, encoding="utf-8")
        scan_handler.setFormatter(file_formatter)
        scan_handler.setLevel(logging.DEBUG)
        logger.addHandler(scan_handler)
        
        # Add SocketIO real-time streaming
        try:
            from core.socketio_handler import SocketIOLogHandler
            socket_handler = SocketIOLogHandler(scan_id=scan_id)
            socket_handler.setLevel(logging.INFO)
            logger.addHandler(socket_handler)
        except Exception as e:
            # Don't fail if SocketIO setup fails
            pass

    return logger


class ScanLogger:
    """Wrapper for scan-specific logging with convenience methods.
    
    Provides a simple interface for logging during scan execution.
    All log entries are automatically associated with the scan ID.
    
    Attributes:
        logger: Underlying logging.Logger instance.
        scan_id: Associated scan ID for this logger.
    """
    
    def __init__(self, scan_id: str, name: str = "DARKWIN") -> None:
        """Initialize scan logger.
        
        Args:
            scan_id: Unique scan identifier.
            name: Logger name prefix (default: "DARKWIN").
        """
        self.logger: logging.Logger = get_logger(f"{name}.{scan_id}", scan_id=scan_id)
        self.scan_id: str = scan_id

    def debug(self, msg: str) -> None:
        """Log debug message."""
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        """Log info message."""
        self.logger.info(msg)

    def success(self, msg: str) -> None:
        """Log success message."""
        self.logger.success(msg)

    def warning(self, msg: str) -> None:
        """Log warning message."""
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        """Log error message."""
        self.logger.error(msg)

    def critical(self, msg: str) -> None:
        """Log critical message."""
        self.logger.critical(msg)
