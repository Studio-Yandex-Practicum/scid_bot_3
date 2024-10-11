import logging
from pathlib import Path


log_dir = Path(__file__).parent / 'log_levels'
log_dir.mkdir(exist_ok=True)


class LevelFilter(logging.Filter):
    """Фильтр для логирования сообщений только определенного уровня."""

    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


def setup_logging():
    """Настройка логирования для разных уровней."""

    logger = logging.getLogger()

    if logger.hasHandlers():
        logger.handlers.clear()

    info_handler = logging.FileHandler(log_dir / 'info.log', encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(LevelFilter(logging.INFO))
    info_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )

    error_handler = logging.FileHandler(
        log_dir / 'error.log', encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(LevelFilter(logging.ERROR))
    error_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )

    debug_handler = logging.FileHandler(
        log_dir / 'debug.log', encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.addFilter(LevelFilter(logging.DEBUG))
    debug_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )

    logger.setLevel(logging.DEBUG)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(debug_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)
