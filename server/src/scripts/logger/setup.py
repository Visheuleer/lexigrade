import logging
from scripts.logger.logging_handler import TqdmLoggingHandler

def setup_logger(name: str = "cefr_lexicon"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    handler = TqdmLoggingHandler()
    handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    return logger