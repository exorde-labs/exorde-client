#! python3.10
import time
import logging
import json

"""
Json formatter that respects OVH logging platform field naming convention
https://help.ovhcloud.com/csm/en-gb-logs-data-platform-field-naming-conventions?id=kb_article_view&sysparm_article=KB0050047

USAGE:

./echo.py 2> >(./nurse.py)


"""


class JsonFormatter(logging.Formatter):
    def __init__(self, *__args__, **kwargs):
        self.host = kwargs["host"]
        self.api = kwargs["api"]
        self.datefmt = kwargs["datefmt"]

    LEVEL_MAP = {
        logging.INFO: 1,
        logging.DEBUG: 2,
        logging.ERROR: 3,
        logging.CRITICAL: 4,
    }

    def format(self, record):
        log_record = {
            "version": "1.1",
            "host": self.host,
            "short_message": record.getMessage()[:25] + "...",
            "full_message": record.getMessage(),
            "timestamp": time.time(),
            "level": self.LEVEL_MAP.get(record.levelno, 1),
            "line": record.lineno,
            "X-OVH-TOKEN": self.api,
            "_details": json.dumps(record.logcheck),
        }
        return json.dumps(log_record)


if __name__ == "__main__":
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        JsonFormatter(
            datefmt="%Y-%m-%d %H:%M:%S",
            host="node.exorde.dev",
            api="78268784-6006-485e-b7b4-c58d08549990",
        )
    )

    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[stream_handler],
    )
    i = 0
    while True:
        i = i + 1
        time.sleep(1)
        logging.info("hello world", extra={"logcheck": {"i": i}})
        if i % 3:
            logging.debug("hello world", extra={"logcheck": {"i": i}})
