import logging


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOGGING_CONFIG = {
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "level": logging.INFO,
    "datefmt": DATE_FORMAT,
}

logging.basicConfig(**LOGGING_CONFIG)


def logger(text: str) -> None:
    logging.info(text)
