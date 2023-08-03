import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Dict


class AsyncItemCounter:
    def __init__(self):
        self.data: Dict[str, deque] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self.locks_creation_lock = asyncio.Lock()

    async def increment(self, key: str) -> None:
        async with await self._get_lock(key):
            occurrences = self.data.get(key, deque())
            occurrences.append(datetime.now())
            self.data[key] = occurrences

    async def count_last_n_items(self, n_items: int) -> Dict[str, int]:
        result = {}
        async with self.locks_creation_lock:
            keys = list(self.locks.keys())

        for key in keys:
            async with await self._get_lock(key):
                occurrences = self.data.get(key, deque())
                # Convert to list and take the last n_items
                result[key] = len(list(occurrences)[-n_items:])
        return result

    async def count_occurrences(
        self, key: str, time_period: timedelta = timedelta(hours=24)
    ) -> int:
        async with await self._get_lock(key):
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

    async def _get_lock(self, key: str) -> asyncio.Lock:
        async with self.locks_creation_lock:
            if key not in self.locks:
                self.locks[key] = asyncio.Lock()
        return self.locks[key]


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
