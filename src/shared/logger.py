import os
import sys
import logging
import traceback
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import json

LOG_PATH = "logs/bot.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


class CustomJsonFormatter(json.JsonFormatter):
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s %(levelname)s %(message)s %(filename)s %(funcName)s %(lineno)d %(traceback)s",
            rename_fields={
                "levelname": "level",
                "filename": "file",
                "funcName": "func",
                "lineno": "lineno",
                "message": "msg",
                "traceback": "exception",
            },
            datefmt="%Y-%m-%d %H:%M:%S",
            json_ensure_ascii=False,
            json_indent=2,
        )


class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        s = super().format(record)
        if hasattr(record, "traceback") and record.traceback:
            s += "\n" + record.traceback
        return s


logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    LOG_PATH, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(CustomJsonFormatter())
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    ConsoleFormatter("%(asctime)s | %(levelname)s | %(message)s")
)
logger.addHandler(console_handler)


def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.critical("Необработанное исключение", extra={"traceback": tb_str})


sys.excepthook = global_exception_handler
