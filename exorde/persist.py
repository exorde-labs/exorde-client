#! env python3.10
"""
persist.py

# backed-up persistence.

In order to safely write a document the function moves the previous file
to a .backup destination. This guarantee an available file with correct
integrity in case the client breaks during the write operation.

# context
- The load function should be used when opening the client
- The write function is used when the data has been updated

# restrictions

- It works using `dict`. (NOT `str`) ; it uses the JSONDecodeError in order to
detect wether a file is corrupted.

- If both files are corrupted the load function returns an empty dict

# functions

- persist(data: dict, file_path: str) -> None

- load(file_path: str) -> dict

"""

import aiofiles
import json
import asyncio
import os
from pathlib import Path


async def _persist(data: dict, file_path: str) -> None:
    """
    Write data as JSON to the specified file path asynchronously.
    If the file already exists, create a backup with a .backup extension.

    Args:
        data: The data to be written as JSON.
        file_path (str): The path to the file where data will be written.
    """
    backup_extension = ".backup"
    backup_path = Path(file_path + backup_extension)

    if Path(file_path).is_file():
        os.rename(file_path, backup_path)

    async with aiofiles.open(file_path, "w") as file:
        json_data = json.dumps(data, indent=4)
        await file.write(json_data)


"""

## Differences between `_persist` and `make_persist_function`

_persist is a naive implementation that will fail saving the last
call in case of many multiple calls.

`make_persist_function` keeps the last task as the correct value to be saved.

"""


def make_persist_function():
    current_task = None

    async def persist(data: dict, file_path: str) -> None:
        nonlocal current_task

        # Cancel the previous task if exists
        if current_task:
            current_task.cancel()

        # Define a new task
        async def write_task():
            try:
                backup_extension = ".backup"
                backup_path = Path(file_path + backup_extension)

                if Path(file_path).is_file():
                    os.rename(file_path, backup_path)

                async with aiofiles.open(file_path, "w") as file:
                    json_data = json.dumps(data, indent=4)
                    await file.write(json_data)
            except asyncio.CancelledError:
                pass  # Ignore the CancelledError exception

        # Set the current task to the new task
        current_task = asyncio.create_task(write_task())
        await current_task

    return persist


persist = make_persist_function()


async def load(file_path: str) -> dict:
    """
    Load data from the specified file path asynchronously.
    If a JSON decode error occurs, attempt to load from the backup file.

    Args:
        file_path (str): The path to the file to load data from.

    Returns:
        dict: The loaded data as a dictionary.
    """
    try:
        async with aiofiles.open(file_path, "r") as file:
            data = await file.read()
            return json.loads(data)
    except (json.JSONDecodeError, FileNotFoundError):
        backup_path = Path(file_path + ".backup")
        async with aiofiles.open(backup_path, "r") as backup_file:
            backup_data = await backup_file.read()
            try:
                return json.loads(backup_data)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}


"""
Tests

"""


# Test loading data from backup when main file is corrupted
async def test_load_from_backup_on_corrupted():
    file_to_load = "test_data.json"
    backup_file = "test_data.json.backup"

    with open(file_to_load, "w") as file:
        file.write("Invalid JSON Content")

    data_to_persist = {"name": "Jane Smith", "age": 25, "city": "Testington"}
    with open(backup_file, "w") as backup_file:
        json.dump(data_to_persist, backup_file, indent=4)

    # Attempt to load from backup
    loaded_data = await load(file_to_load)
    expected_data = {"name": "Jane Smith", "age": 25, "city": "Testington"}
    assert (
        loaded_data == expected_data
    ), f"Expected {expected_data}, got {loaded_data}"


# Test loading data from backup when both main and backup files are corrupted
async def test_load_from_backup_on_both_corrupted():
    file_to_load = "test_data.json"
    backup_file = "test_data.json.backup"

    with open(file_to_load, "w") as file:
        file.write("Invalid JSON Content")

    with open(backup_file, "w") as backup_file:
        backup_file.write("Invalid JSON Content")

    # Attempt to load from backup
    loaded_data = await load(file_to_load)
    assert loaded_data == {}, f"Expected empty dictionary, got {loaded_data}"


# Test concurrent writes without locks
async def test_many_concurrent_writes():
    """
    if persist = _persist this test could use task 958 as last task (for example)
    """
    file_to_persist = "test_data.json"

    # Generate a list of data with unique ids
    data_list = [
        {
            "name": f"Person {i}",
            "age": i,
            "city": f"City {i}",
            "id": f"task_{i}",
        }
        for i in range(1000)
    ]

    # Trigger concurrent writes for each data
    tasks = [
        asyncio.create_task(persist(data, file_to_persist))
        for data in data_list
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass  # Ignore the CancelledError exception

    # Load data from the file
    async with aiofiles.open(file_to_persist, "r") as file:
        loaded_data = await file.read()

    print("Loaded data from file after concurrent writes:", loaded_data)


# Test backup behavior when write process is interrupted
async def test_backup_behavior_on_interrupt():
    file_to_persist = "test_data.json"

    data_to_persist = {"name": "John Doe", "age": 30, "city": "City A"}

    # Trigger a persist task and then immediately interrupt it
    task = asyncio.create_task(persist(data_to_persist, file_to_persist))
    await asyncio.sleep(0.5)  # Wait for half a second
    task.cancel()

    # Load data from the backup file
    backup_file = "test_data.json.backup"
    async with aiofiles.open(backup_file, "r") as file:
        loaded_data = await file.read()

    print("Loaded data from backup after interrupted write:", loaded_data)


# Run all tests
async def run_tests():
    await test_load_from_backup_on_corrupted()
    print("test_load_from_backup_on_corrupted - ok")
    await test_load_from_backup_on_both_corrupted()
    print("test_load_from_backup_on_both_corrupted - ok")
    await test_many_concurrent_writes()
    print("test_many_concurrent_writes - ok")
    await test_backup_behavior_on_interrupt()
    print("test_backup_behavior_on_interrupt - ok")


# Run the event loop for tests
if __name__ == "__main__":
    asyncio.run(run_tests())
