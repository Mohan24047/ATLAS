import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'atlas.log')

logger = logging.getLogger('atlas')
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(handler)

def log_wake():
    logger.info("Wake word detected")

def log_tool(tool_name, args=None, result=None):
    if result:
        logger.info(f"Tool: {tool_name} -> {result}")
    else:
        logger.info(f"Tool: {tool_name} args={args}")

def log_error(message, exc=None):
    if exc:
        logger.error(f"{message}: {exc}")
    else:
        logger.error(message)

def log_reminder(message):
    logger.info(f"Reminder: {message}")

def log_info(message):
    logger.info(message)
