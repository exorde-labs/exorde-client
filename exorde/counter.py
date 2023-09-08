import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Dict

from exorde.persist import persist, load

STATS_FILE_PATH = "/tmp/exorde/stats.json"


def ItemCounterSerializer(obj):
    if isinstance(obj, datetime):
        return {"__datetime__": True, "value": obj.timestamp()}
    if isinstance(obj, deque):
        return {"__deque__": True, "value": list(obj)}
    return obj


def ItemCounterObjectHook(obj):
    if "__datetime__" in obj:
        return datetime.fromtimestamp(obj["value"])
    if "__deque__" in obj:
        return deque(obj["value"])
    return obj


class AsyncItemCounter:
    def __init__(self):
        self.data: Dict[str, deque] = load(
            STATS_FILE_PATH, ItemCounterObjectHook
        )

    async def increment(self, key: str) -> None:
        occurrences = self.data.get(key, deque())
        occurrences.append(datetime.now())
        self.data[key] = occurrences
        await persist(
            self.data, STATS_FILE_PATH, custom_serializer=ItemCounterSerializer
        )

    async def count_last_n_items(self, n_items: int) -> Dict[str, int]:
        result = {}

        for key in self.data:
            occurrences = self.data.get(key, deque())
            # Convert to list and take the last n_items
            result[key] = len(list(occurrences)[-n_items:])
        return result

    async def count_occurrences(
        self, key: str, time_period: timedelta = timedelta(hours=24)
    ) -> int:
        now = datetime.now()
        # Cleaning up is always enforced on static 24h
        valid_time_cleanup = now - timedelta(hours=24)
        occurrences = self.data.get(key, deque())
        # Remove dates older than 24 hours
        while occurrences and occurrences[0] < valid_time_cleanup:
            occurrences.popleft()

        # Count occurrences within the specified time period
        valid_time_count = now - time_period
        count = sum(1 for occ in occurrences if occ >= valid_time_count)

        return count


# Example usage:
async def main() -> None:
    counter = AsyncItemCounter()

    await counter.increment("apple")
    await asyncio.sleep(1)
    await counter.increment("apple")
    await counter.increment("banana")

    print(
        await counter.count_occurrences("apple", timedelta(hours=1))
    )  # Output: 2 within the last 1 hour
    print(
        await counter.count_occurrences("banana", timedelta(hours=24))
    )  # Output: 1 within the last 24 hours


if __name__ == "__main__":
    asyncio.run(main())
