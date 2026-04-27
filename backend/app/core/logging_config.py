"""
Structured logging configuration for Dekho backend.
Uses Python's built-in logging with JSON-style formatting for production
and coloured console output for development.
"""
import logging
import os
import sys
from datetime import datetime, timezone


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class StructuredFormatter(logging.Formatter):
    """Formats log records as structured key=value strings."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        level = record.levelname
        msg = record.getMessage()
        name = record.name

        base = f"[{ts}] {level:8s} {name}: {msg}"

        # Attach any extra context fields
        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            )
        }
        if extras:
            extra_str = " | " + " ".join(f"{k}={v}" for k, v in extras.items())
            base += extra_str

        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)

        return base


def setup_logging():
    """Configure root logger and return a named logger for the app."""
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        root.addHandler(handler)

    # Quieten noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logging.getLogger("dekho")


# Module-level logger — import this wherever needed
logger = setup_logging()
