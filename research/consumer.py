#! python3.10

from random import sample
from typing import AsyncGenerator, Callable, Union
from asyncio import sleep, run, gather, create_task, wait_for, Queue
from dataclasses import dataclass

from asyncio.exceptions import TimeoutError


@dataclass
class Profile:
    fn: Callable[..., AsyncGenerator[int, None]]
    name: str


def build_profile(
    sleep_time: int,
    name: str,
    f: Union[Callable, None] = None,
) -> Profile:
    async def __f__() -> AsyncGenerator[int, None]:
        print(f"sleep {sleep_time}...", end="", flush=True)
        try:
            await sleep(sleep_time)
            if f:
                await f()
            print("... done")
            yield sleep_time
        except GeneratorExit:
            raise

    return Profile(fn=__f__, name=name)


def profile_factory() -> list[Profile]:
    normal = build_profile(1, "normal")
    slowed = build_profile(5, "slowed")
    hanged = build_profile(150, "hanged")

    return [normal, normal, normal, slowed, slowed, hanged]


async def consumer(
    profiles: list[Profile], identifier: int, result_queue: Queue
):
    print(f"consumer {identifier} started")
    cursor = -1
    max = len(profiles) - 1
    while True:
        if cursor == max:
            cursor = -1
        cursor += 1
        iterator = profiles[cursor].fn().__aiter__()
        try:
            result = await wait_for(iterator.__anext__(), timeout=2)
            await result_queue.put(result)
        except TimeoutError:
            pass


async def borg(result_queue: Queue):
    while True:
        result = await result_queue.get()
        yield result


async def theship(profiles: list[Profile], consumer_amount: int):
    result_queue: Queue = Queue()
    tasks = [
        create_task(consumer(sample(profiles, len(profiles)), i, result_queue))
        for i in range(consumer_amount)
    ]

    await gather(*tasks)
    async for result in borg(result_queue):
        print(result)


if __name__ == "__main__":
    profiles = profile_factory()
    try:
        run(theship(profiles, 20))
    except KeyboardInterrupt:
        print("bye bye !")
