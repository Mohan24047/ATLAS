# Simple Logger
# Console logging for debugging

from datetime import datetime


class Logger:
    """Simple console logger for debugging."""
    
    DEBUG = True  # Set to False to disable debug logs
    
    @staticmethod
    def info(message):
        """Log info message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] INFO: {message}")
    
    @staticmethod
    def debug(message):
        """Log debug message (only if DEBUG is True)."""
        if Logger.DEBUG:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] DEBUG: {message}")
    
    @staticmethod
    def error(message):
        """Log error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ERROR: {message}")
    
    @staticmethod
    def warning(message):
        """Log warning message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] WARNING: {message}")
