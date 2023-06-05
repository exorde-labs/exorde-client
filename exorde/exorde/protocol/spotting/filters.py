from datetime import datetime, timedelta


def datetime_filter(value, expiration_delta, __stack__):
    zless = value.created_at.replace("Z", "")
    if not value.created_at:
        return False
    if datetime.fromisoformat(zless) - datetime.now() > timedelta(
        seconds=expiration_delta
    ):
        return False
    return True


def has_content(value):
    if not value.content:
        return False
    if not len(value.content) > 35:
        return False
    return True
