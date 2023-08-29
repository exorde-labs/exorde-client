"""
Once-Per-Day Async Function Execution Decorator

This script defines an asynchronous decorator that ensures the decorated async function runs only once every 24 hours.
The decorator tracks the last execution time and enforces the time constraint.

Usage:
1. Import the decorator: `from once_per_day_decorator import once_per_day`
2. Apply the decorator to your async functions: `@once_per_day(delay_hours)`
3. Call the decorated functions, which will only execute once every 24 hours.

Example:
    @once_per_day(delay_hours=1.5)  # Delays the first execution by 1.5 hours
    async def my_async_function():
        # Your async function logic here

    await my_async_function()  # Will execute only once every 24 hours, with initial delay.

Note:
- This implementation uses an in-memory mechanism to track execution times.
- If the script is restarted, the execution tracking will be reset.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Callable


def once_per_day(delay_hours: float = 0) -> Callable:
    """
    An asynchronous decorator that ensures the decorated async function runs only once every 24 hours.

    Args:
        delay_hours (float): The initial delay in hours before the first function call.

    Returns:
        callable: The wrapped async function that enforces the once-per-day execution rule.
    """
    last_execution_time = None
    initial_call = True

    def decorator(func):
        async def wrapped(*args, **kwargs):
            nonlocal last_execution_time, initial_call

            if initial_call:
                initial_call = False
                last_execution_time = datetime.now() - timedelta(
                    hours=(24 - delay_hours)
                )

            if (
                last_execution_time is None
                or datetime.now() - last_execution_time >= timedelta(hours=24)
            ):
                last_execution_time = datetime.now()
                result = await func(*args, **kwargs)
                return result
            else:
                pass

        return wrapped

    return decorator


# Usage example
@once_per_day(delay_hours=1.5)  # Delays the first execution by 1.5 hours
async def my_async_function():
    """
    An example async function that demonstrates the once_per_day decorator.
    """
    print("Async function executed!")


# Testing the decorator
async def main():
    await my_async_function()  # This will execute after the initial delay and update the last_execution_time
    await asyncio.sleep(10)
    await my_async_function()  # This won't execute due to the 24-hour constraint


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
