"""
persist.py

# backed-up persistence.

In order to safely write a document the function moves the previous file
to a .backup destination. This guarantee an available file with correct integrity
in case the client breaks during the write operation.

# restrictions

- It works using `dict`. (NOT `str`) ; it uses the JSONDecodeError in order to
detect wether a file is corrupted.

# functions

- persist(data: dict, file_path: str) -> None

- load(file_path: str) -> dict

"""

import aiofiles
import json
import asyncio
import os
from pathlib import Path


async def persist(data: dict, file_path: str) -> None:
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
            return json.loads(backup_data)


# Example usage
async def main():
    data_to_persist = {"name": "John Doe", "age": 30, "city": "Exampleville"}

    file_to_persist = "/tmp/exorde/stats.json"

    await persist(data_to_persist, file_to_persist)
    print("Data has been persisted asynchronously and backup created.")


# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())

__all__ = ["persist", "load"]
