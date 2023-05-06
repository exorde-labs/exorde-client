from datetime import datetime, timedelta, timezone
import logging


def datetime_filter(value, __stack__):
    if datetime.fromisoformat(value["item"]["CreationDateTime"]) - datetime.now(
        timezone.utc
    ) > timedelta(seconds=180):
        return False
    return True


def unique_filter(value, stack):
    # if we had keyword we could weight in the duplicates in keyword choice
    # we could also trigger page roll after a certain amount of duplicates
    # but we should be able to pass on this option to be able to "monitor"
    # specific items
    if value in stack:
        logging.debug("Duplicate collection")
    return value not in stack


def format_assertion(value, stack):
    try:
        assert len(value["item"]["Content"]) > 20
        return True
    except:
        return False
