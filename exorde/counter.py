import asyncio
from collections import deque
from datetime import datetime, timedelta
from typing import Dict


class AsyncItemCounter:
    def __init__(self):
        self.data: Dict[str, deque] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    async def increment(self, key: str) -> None:
        async with await self._get_lock(key):
            occurrences = self.data.get(key, deque())
            occurrences.append(datetime.now())
            self.data[key] = occurrences

    async def count_occurrences(
        self, key: str, time_period: timedelta = timedelta(hours=24)
    ) -> int:
        async with await self._get_lock(key):
            now = datetime.now()
            valid_time = now - time_period
            occurrences = self.data.get(key, deque())
            # Remove dates older than the specified time period
            while occurrences and occurrences[0] < valid_time:
                occurrences.popleft()
            return len(occurrences)

    async def _get_lock(self, key: str) -> asyncio.Lock:
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
        await counter.count_occurrences("apple")
    )  # Output: 2 within the last 24 hours
    print(
        await counter.count_occurrences("banana")
    )  # Output: 1 within the last 24 hours


if __name__ == "__main__":
    asyncio.run(main())
