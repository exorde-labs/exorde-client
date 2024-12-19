from print_dict_struct import print_dict_structure
from ipfs import download_ipfs_file
import json
import asyncio
import traceback
import difflib

from colorama import Fore, Style


def simple_diff(original, modified):
    """
    Highlight character-level differences between two strings, preserving structure and newlines.

    Args:
        original (str): Original text.
        modified (str): Modified text.

    Returns:
        None: Prints the highlighted diff with added and removed parts.
    """
    # Generate character-level diff
    diff = difflib.ndiff(original, modified)

    for char in diff:
        if char.startswith("-"):
            print(Fore.RED + char[2:] + Style.RESET_ALL, end="")  # Highlight removed characters
        elif char.startswith("+"):
            print(Fore.GREEN + char[2:] + Style.RESET_ALL, end="")  # Highlight added characters
        else:
            print(char[2:], end="")  # Print unchanged characters

async def download_ipfs_files(selected_batchs: list[str]):
    for cid in selected_batchs:
        yield await download_ipfs_file(cid)

def get_pre_dot(content: str) -> str:
    try:
        return content.split('.')[0]
    except:
        return content

async def process_item(manager, item):
    analysis = item["analysis"]
    item_data = item["item"]
    file_name = get_pre_dot(item_data["domain"])
    file_name = file_name if file_name != "x" else "twitter"
    try:
        resp = await manager.send(
            "quality_{}".format(file_name), json.dumps(item_data)
        )
        print("________________________")
        print("\tSPOTTED DOMAIN: {}".format(file_name))
        print("\tSPOTTED URL: {}".format(item_data["url"]))
        print("\n\tSPOTTED RAW:\n")
        print(item_data["raw_content"])
        print("\n\tSPOTTED TRAN (FROM:{}):\n".format(item_data["language"]))
        print(item_data["translated_content"])
        if resp.get("response", None) and resp.get("response", None).get("adapter", None):
            print("\n\tADAPTER CONTENT:\n\n{}".format(resp["response"]["adapter"]))
            print("\n\tDIFF:\n")
            simple_diff(item_data["raw_content"], resp["response"]["adapter"])
            print("\n\n\tSPOTTED KW: \n\n{}\n".format(item["analysis"]["top_keywords"]))
        elif resp.get("error", None):
            print("\n\tADAPTER ERROR:\n\n{}".format(resp["error"]))
        print('')
        print("________________________")

        # 3. Translate items
        # 4. Extract keywords
        # 5. Embedding
        # 6. Cosine similarity

    except ValueError:
        print("No adapter for {}".format(file_name))
    except asyncio.exceptions.CancelledError:
        await manager.wait_for_event_server_back_online(f"quality_{file_name}")
        return await process_item(manager, item)
    except Exception as e:
        traceback.print_exc()
        print(f"Error processing {file_name}: {e}") 

async def create_report(manager, selected_batchs: list[str]):
    print("creating report")
    # 1. Download IPFS files
    async for ipfs_file in download_ipfs_files(selected_batchs):
#        print_dict_structure(ipfs_file)
        tasks = []
        for item in ipfs_file["items"]:
            # Create a task for each item to process them concurrently
            task = asyncio.create_task(process_item(manager, item))
            tasks.append(task)
        # Wait for all tasks for this IPFS file to complete
        await asyncio.gather(*tasks)
