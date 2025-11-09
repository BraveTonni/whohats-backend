import logging


def setup_logger() -> None:
    """Method for setup logging"""
    logging.basicConfig(
        level=logging.INFO
    )