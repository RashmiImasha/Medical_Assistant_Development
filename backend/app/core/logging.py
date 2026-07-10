import logging, sys
from app.core.config import get_settings
 
 
def configure_logging() -> None:
    """
    Configure root logging once, at app startup (called from main.py).
    Keeps format consistent across uvicorn, SQLAlchemy, and app loggers.
    """
    settings = get_settings()
 
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
 
    # Quiet down noisy third-party loggers unless we're debugging
    if settings.log_level.upper() != "DEBUG":
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
 
 
def get_logger(name: str) -> logging.Logger:
    """
    Use in every module: logger = get_logger(__name__)
    """
    return logging.getLogger(name)