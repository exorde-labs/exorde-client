"""
at.py

Calls function at specified time. It mimics a cron like feature using a throttle
logic.

IT DOES NOT:
    - loop forever : the function is still expeced to be called periodicly
IT DOES:
    - throttle the parameter function to be called only onced at a specified 
        date
    - persist that it has called the action
    - delete the actions of previous day
EXPECT:
    - list of times
    - the path where to persist the data
    - the async action to be called
MISC:
    - persist.py
    - throttle.py
"""
from datetime import datetime
from typing import Callable

from datetime import datetime, time, timedelta, date
from collections import deque

from exorde.persist import PersistedDict


def at(hours: list[time], path: str, action: Callable):
    def assert_integrity(persisted: PersistedDict, index):  # index is a _Date
        if not index in persisted or not isinstance(persisted[index], list):
            persisted[index] = []
        current_date = date.today()
        previous_day = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            del persisted[previous_day]
        except:
            pass

    def custom_serializer(obj):
        if isinstance(obj, time):  # Serialize datetime.time objects to strings
            time_str = obj.strftime("%H:%M:%S")
            return {"__time__": True, "value": time_str}
        return obj

    def custom_object_hook(obj):
        if (
            "__time__" in obj
        ):  # Handle deserialization of datetime.time objects
            time_str = obj["value"]
            hour, minute, second = map(int, time_str.split(":"))
            time_obj = time(hour, minute, second)
            return time_obj
        return obj

    persisted = PersistedDict(
        path,
        serializer=custom_serializer,
        custom_object_hook=custom_object_hook,
    )
    result = None

    async def wrapper(*args, **kwargs):
        nonlocal result, persisted
        current_date = datetime.now().date().strftime("%Y-%m-%d")
        assert_integrity(persisted, current_date)
        print(persisted)
        for hour in hours:
            hour_as_datetime = datetime.combine(date.today(), hour)
            if (
                datetime.now() >= hour_as_datetime
                and hour not in persisted[current_date]
            ):
                persisted[current_date] = persisted[current_date] + [hour]
                result = await action(*args, **kwargs)

        # returned result is a non-feature
        return result

    return wrapper
