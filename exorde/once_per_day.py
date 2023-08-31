#!env python3.10

import asyncio
from datetime import datetime, timedelta
from typing import Callable
from exorde.persist import PersistedDict

# Import necessary modules for testing
from unittest.mock import patch, AsyncMock
from freezegun import freeze_time
from datetime import datetime
from collections import deque


def throttle_to_frequency(frequency_hours: float = 24) -> Callable:
    """
    An asynchronous decorator that ensures the decorated async function runs only
    with the specified frequency in hours.

    Args:
        frequency_hours (float): The frequency in hours for function calls.

    Returns:
        callable: The wrapped async function that enforces the frequency constraint.
    """

    def custom_serializer(obj):
        if isinstance(obj, datetime):
            return {"__datetime__": True, "value": obj.timestamp()}
        if isinstance(obj, deque):
            return {"__deque__": True, "value": list(obj)}
        return obj

    def custom_object_hook(obj):
        if "__datetime__" in obj:
            return datetime.fromtimestamp(obj["value"])
        if "__deque__" in obj:
            return deque(obj["value"])
        return obj

    persisted = PersistedDict(
        "/tmp/exorde/throttle.json",
        serializer=custom_serializer,
        custom_object_hook=custom_object_hook,
    )
    persisted["last_execution_time"] = None
    persisted["initial_call"] = True

    def decorator(func):
        def wrapped(*args, **kwargs):
            nonlocal persisted

            if persisted["initial_call"]:
                persisted["initial_call"] = False
                persisted["last_execution_time"] = datetime.now() - timedelta(
                    hours=frequency_hours
                )

            if persisted[
                "last_execution_time"
            ] is None or datetime.now() - persisted[
                "last_execution_time"
            ] >= timedelta(
                hours=frequency_hours
            ):
                persisted["last_execution_time"] = datetime.now()
                result = func(*args, **kwargs)
                return result
            else:
                pass

        return wrapped

    return decorator


async def test_throttler():
    def counter_builder():
        counter = 0

        def increment():
            nonlocal counter
            counter += 1

        def get():
            return counter

        return [increment, get]

    increment, get = counter_builder()

    throttled_increment = throttle_to_frequency(frequency_hours=1)(increment)
    for __i__ in range(0, 10):
        throttled_increment()
    await asyncio.sleep(1)
    assert get() == 1
    with freeze_time(datetime.now() + timedelta(hours=1, minutes=1)):
        throttled_increment()
    assert get() == 2


async def run_tests():
    await test_throttler()
    print("test_throttler - ok")


if __name__ == "__main__":
    asyncio.run(run_tests())
