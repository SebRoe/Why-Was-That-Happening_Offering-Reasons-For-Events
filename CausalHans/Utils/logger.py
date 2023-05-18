import logging
import os
from colorama import Fore, Back, Style

def get_spec_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    for i in logger.handlers:
        logger.removeHandler(i)

    streamhandler = logging.StreamHandler()
    logger.addHandler(streamhandler)
    logger.handlers[0].setFormatter(CustomFormatter())

    log_level = os.environ.get("LOG_LEVEL", "")

    if log_level == "DEBUG":
        level = logging.DEBUG
    elif log_level == "INFO":
        level = logging.INFO
    elif log_level == "WARNING":
        level = logging.WARNING
    else:
        level = logging.ERROR

    logger.setLevel(level=level)

    return logger



class CustomFormatter(logging.Formatter):
    green = Fore.GREEN + Style.BRIGHT
    yellow = Fore.YELLOW + Style.BRIGHT
    black = Fore.BLACK + Style.BRIGHT
    red = Fore.YELLOW + Style.BRIGHT
    bold_red = Fore.RED + Style.BRIGHT
    reset = Style.RESET_ALL

    level = f'%(levelname)s'
    time = f'%(asctime)s'
    name = f'%(name)s.%(funcName)s()'
    func_name = f'%(funcName)s()'
    message = f'%(message)s'

    format = f'%(levelname)s - %(asctime)s - %(name)s.%(funcName)s() - %(message)s'
    # format = f'%(levelname)s - %(name)s.%(funcName)s() - %(message)s'
    FORMATS = {
        logging.DEBUG: black + level + reset + ' - ' + func_name + ' - ' + black + message + reset,
        logging.INFO: green + level + reset + ' - ' + green + message + reset,
        logging.WARNING: yellow + level + reset + ' - ' + time + ' - ' + func_name + ' - ' + yellow + message + reset,
        logging.ERROR: bold_red + format,
        logging.CRITICAL: bold_red + format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
