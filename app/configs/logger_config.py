import logging
import sys
import structlog
from app.configs.app_config import settings

def setup_logging():
    """
    Configures centralized logging for the application.
    Uses structlog for structured, pretty-printed logs.
    Respects the LOG_LEVEL from environment settings.
    """
    
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure shared processors
    shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.CallsiteParameterAdder(
        parameters=[
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.LINENO,
            structlog.processors.CallsiteParameter.FUNC_NAME,
        ]
    ),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    ]

    
    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )
    
    # Also configure standard logging to bridge logs from other libraries
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    
    logger = structlog.get_logger()
    logger.info("Logging initialized", level=settings.LOG_LEVEL)
