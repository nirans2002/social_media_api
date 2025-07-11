from logging.config import dictConfig

from social_media_api.config import config, DevConfig
import logging

def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                 "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 16 if isinstance(config, DevConfig) else 256,
                    "default_value": "-",
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "logging.Formatter",
                    # "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    # For JsonFormatter, the format string just defines what keys are included in the log record
                    # It's a bit clunky, but it's the way to do it for now
                    "format": "%(asctime)s %(msecs)03d %(levelname)s (%(correlation_id)s) %(name)s %(lineno)d %(message)s",
                },

            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",  # could use logging.StreamHandler instead
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id"], #, "email_obfuscation"

                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filters": ["correlation_id"], #, "email_obfuscation"
                    "filename": "social_media_api.log",
                    "maxBytes": 1024 * 1024 * 1,  # 1 MB
                    "backupCount": 3,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "social_media_api": {
                    "handlers": ["default"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "uvicorn": {"handlers": ["default", "rotating_file"], "level": "INFO"},
                "databases": {"handlers": ["default"], "level": "WARNING"},
                "aiosqlite": {"handlers": ["default"], "level": "WARNING"}

            },
        }
    )
