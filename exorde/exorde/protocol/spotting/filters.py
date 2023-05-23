from datetime import datetime, timedelta, timezone
import logging


def datetime_filter(value, expiration_delta, __stack__):
    if not value.created_at:
        return False
    if datetime.fromisoformat(value.created_at) - datetime.now(
        timezone.utc
    ) > timedelta(seconds=expiration_delta):
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


def format_assertion(value, __stack__):
    try:
        assert len(value["item"]["Content"]) > 20
        return True
    except:
        return False
