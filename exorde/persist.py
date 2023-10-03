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
import logging
import aiofiles
import json
import asyncio
import os
from datetime import datetime
from collections import deque
from pathlib import Path
from typing import Callable, Union


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
        try:
            json_data = json.dumps(data, indent=4)
            await file.write(json_data)
        except Exception as err:
            logging.error(err)
            logging.error(data)


"""

## Differences between `_persist` and `make_persist_function`

_persist is a naive implementation that will fail saving the last
call in case of many multiple calls.

`make_persist_function` keeps the last task as the correct value to be saved.

"""


def make_persist_function():
    current_task = None

    async def persist(
        data: dict, file_path: str, custom_serializer=None
    ) -> None:
        """Writes the content of `data` into a file specified at `file_path`"""
        nonlocal current_task

        # Cancel the previous task if exists
        if current_task:
            current_task.cancel()

        # Define a new task
        async def write_task():
            try:
                backup_extension = ".backup"
                backup_path = Path(file_path + backup_extension)

                # Check if the directory exists, create it if it doesn't
                parent_dir = Path(file_path).parent
                parent_dir.mkdir(parents=True, exist_ok=True)

                if Path(file_path).is_file():
                    os.rename(file_path, backup_path)

                # Use the custom serializer if provided, otherwise use the default
                serializer = custom_serializer if custom_serializer else None

                async with aiofiles.open(file_path, "w") as file:
                    try:
                        json_data = json.dumps(
                            data, indent=4, default=serializer
                        )
                        await file.write(json_data)
                    except asyncio.exceptions.CancelledError:
                        pass  # Ignore the CancelledError exception
            except Exception:
                logging.exception("An error occured in persist")

        # Set the current task to the new task
        current_task = asyncio.create_task(write_task())
        try:
            await current_task
        except:
            pass

    return persist


persist = make_persist_function()


def load(
    file_path: str,
    custom_object_hook: Union[Callable, None] = None,
) -> dict:
    """
    Load data from the specified file path synchronously.
    If a JSON decode error occurs, attempt to load from the backup file.

    Args:
        file_path (str): The path to the file to load data from.
        custom_object_hook (callable, optional): A custom object hook for decoding.

    Returns:
        dict: The loaded data as a dictionary.
    """
    try:
        with open(file_path, "r") as file:
            data = file.read()

            # Use the custom object hook if provided, otherwise use the default
            object_hook = custom_object_hook if custom_object_hook else None

            return json.loads(data, object_hook=object_hook)
    except (json.JSONDecodeError, FileNotFoundError):
        backup_path = Path(file_path + ".backup")
        try:
            with open(backup_path, "r") as backup_file:
                backup_data = backup_file.read()
                try:
                    # Use the custom object hook if provided, otherwise use the default
                    object_hook = (
                        custom_object_hook if custom_object_hook else None
                    )

                    return json.loads(backup_data, object_hook=object_hook)
                except (json.JSONDecodeError, FileNotFoundError):
                    return {}
        except FileNotFoundError:
            return {}


import os


class PersistedDict:
    def __init__(
        self,
        file_path: str,
        serializer: Union[Callable, None] = None,
        custom_object_hook: Union[Callable, None] = None,
    ):
        self.file_path = file_path
        self.serializer = serializer
        self.custom_object_hook = custom_object_hook
        self.data = self._load()
        self.hold_persist: bool = False

    async def _persist(self):
        await persist(
            self.data, self.file_path, custom_serializer=self.serializer
        )

    def _load(self):
        return load(self.file_path, custom_object_hook=self.custom_object_hook)

    def __getitem__(self, key):
        try:
            return self.data[key]
        except:
            return None

    def __setitem__(self, key, value):
        self.data[key] = value
        if not self.hold_persist:
            asyncio.create_task(self._persist())

    def __delitem__(self, key):
        del self.data[key]
        if not self.hold_persist:
            asyncio.create_task(self._persist())

    async def deep_merge(self, update_context: dict) -> None:
        """
        Merge the update_context dictionary into the PersistedDict object deeply.

        Args:
            update_context (dict): The dictionary to merge into the PersistedDict object.
        """
        self.hold_persist = True
        self.data = self._deep_merge_dicts(self.data, update_context)
        self.hold_persist = False
        await self._persist()
        await asyncio.sleep(0.01)

    def _deep_merge_dicts(self, target, source):
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                target[key] = self._deep_merge_dicts(target[key], value)
            else:
                target[key] = value
        return target

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)


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
    loaded_data = load(file_to_load)
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
    loaded_data = load(file_to_load)
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


async def test_custom_serializer():
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

    file_to_persist = "test_data.json"

    data_to_persist = {
        "name": "John Doe",
        "age": 30,
        "city": "City A",
        "timestamp": datetime.now(),
        "events": deque([1, 2, 3, 4, 5]),
    }

    # Write data using custom serializer
    await persist(data_to_persist, file_to_persist, custom_serializer)

    # Load data using custom serializer
    loaded_data = load(file_to_persist, custom_object_hook)

    assert (
        loaded_data == data_to_persist
    ), f"Expected {data_to_persist}, got {loaded_data}"


async def test_persisted_dict():
    file_path = "test_data_b.json"

    persisted_dict = PersistedDict(file_path)

    # Test setting and persisting data
    persisted_dict["name"] = "John"
    persisted_dict["age"] = 30
    await asyncio.sleep(1)  # Allow time for the data to persist

    # Test loading persisted data
    loaded_dict = PersistedDict(file_path)
    assert loaded_dict["name"] == "John"
    assert loaded_dict["age"] == 30

    # Test deleting and persisting data
    del persisted_dict["age"]
    await asyncio.sleep(1)  # Allow time for the data to persist

    # Test loading after deletion
    loaded_dict = PersistedDict(file_path)
    assert "age" not in loaded_dict


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
    await test_custom_serializer()
    print("test_custom_serializer - ok")
    await test_persisted_dict()
    print("test_persisted_dict - ok")


# Run the event loop for tests
if __name__ == "__main__":
    asyncio.run(run_tests())

__all__ = ["persist", "load"]
