import logging
import os


def setup_logging():
    """Setup logging for the application."""
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # Set common formatter
    _formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    # Ensure logs appear in terminal even if root isn't configured
    _has_console = any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in logger.handlers)
    if not _has_console:
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(logging.INFO)
        _console_handler.setFormatter(_formatter)
        logger.addHandler(_console_handler)
        logger.propagate = False

    # Ensure logs are also saved to a file next to this script
    _log_file = os.path.join(os.path.dirname(__file__), "digital-cv.log")
    _has_file = any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "") == _log_file for h in logger.handlers)
    if not _has_file:
        try:
            _file_handler = logging.FileHandler(_log_file)
            _file_handler.setLevel(logging.INFO)
            _file_handler.setFormatter(_formatter)
            logger.addHandler(_file_handler)
        except Exception:
            # If file handler can't be created, continue with console-only logging
            pass
    return logger
    