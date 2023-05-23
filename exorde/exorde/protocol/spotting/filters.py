from datetime import datetime, timedelta, timezone


def datetime_filter(value, expiration_delta, __stack__):
    if not value.created_at:
        return False
    if datetime.fromisoformat(value.created_at) - datetime.now(
        timezone.utc
    ) > timedelta(seconds=expiration_delta):
        return False
    return True


def has_content(value):
    if not value.content:
        return False
    if not len(value.content) > 35:
        return False
    return True
