import logging
import os
import sys

import structlog

_LOG_LEVEL_NAMES = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def is_debug_enabled() -> bool:
    return os.environ.get("APP_ENV", "dev").lower() == "dev"


def _get_log_level() -> int:
    raw = os.environ.get("LOG_LEVEL", "").upper()
    if raw in _LOG_LEVEL_NAMES:
        return _LOG_LEVEL_NAMES[raw]
    return logging.INFO


def configure_logging(debug: bool = False) -> None:
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if is_debug_enabled():
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(_get_log_level()),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )
