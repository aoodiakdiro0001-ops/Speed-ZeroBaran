"""
Speed-ZeroBaran — Rich console logger
Pretty colored logs for both local runs and GitHub Actions output.
"""
from __future__ import annotations

import logging
import sys
from typing import Optional

try:
    from rich.logging import RichHandler
    _HAS_RICH = True
except ImportError:  # pragma: no cover
    _HAS_RICH = False


def get_logger(name: str = "speed-zerobaran", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    if _HAS_RICH:
        handler = RichHandler(
            rich_tracebacks=True,
            show_path=False,
            markup=True,
            log_time_format="[%H:%M:%S]",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


# Singleton logger used across the project
log = get_logger()
