from loguru import logger
import sys

# Configure logger
logger.remove()  # Remove default sink
logger.add(
    sys.stdout,
    format="{time:HH:mm:ss} | {name}:{function}:{line} | {level} | {message}",
    level="INFO",
)
logger.add("logs/app.log", rotation="500 MB", retention="10 days", level="DEBUG")

# Global logger instance
app_logger = logger.bind(name="rehablarte")
