import logging
import os
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from typing import Optional

def get_logger(name: str, scan_id: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with console (Rich) and file output.
    If scan_id is provided, logs are also written to a scan-specific file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Console Handler (Rich)
    console_handler = RichHandler(rich_tracebacks=True, markup=True)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # Base Log Directory
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Main Log File (Rotating)
    main_log_file = os.path.join(log_dir, "darkwin.log")
    file_handler = RotatingFileHandler(
        main_log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # Scan-specific logger
    if scan_id:
        scan_log_dir = os.path.join(log_dir, "scans")
        if not os.path.exists(scan_log_dir):
            os.makedirs(scan_log_dir)
        
        scan_log_file = os.path.join(scan_log_dir, f"{scan_id}.log")
        scan_handler = logging.FileHandler(scan_log_file)
        scan_handler.setFormatter(file_formatter)
        scan_handler.setLevel(logging.DEBUG)
        logger.addHandler(scan_handler)

    return logger

class ScanLogger:
    def __init__(self, scan_id: str, name: str = "DARKWIN"):
        self.logger = get_logger(f"{name}.{scan_id}", scan_id=scan_id)
        self.scan_id = scan_id

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
