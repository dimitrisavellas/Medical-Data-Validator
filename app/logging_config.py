import sys
from loguru import logger
from app.config.settings import settings

def setup_logging():
    logger.remove()
    
    # JSON formatter
    def json_serializer(record):
        subset = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "extra": record["extra"]
        }
        return subset

    logger.add(
        sys.stderr,
        level=settings.log_level,
        serialize=True, # Loguru supports JSON serialization out of the box, but custom structure might need sink customization
        backtrace=False,
        diagnose=False,
    )
    
    # File logging (optional, but good for persistence in volume)
    logger.add(
        settings.log_file_path,
        rotation="50 MB",
        retention="30 days",
        level=settings.log_level,
        serialize=True
    )

setup_logging()
