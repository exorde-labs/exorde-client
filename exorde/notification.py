"""
- A notification is a message or alert delivered  to inform a user about a 
specific piece of information.
Notifications are designed to capture the user's attention and provide them 
with relevant information in a timely manner, without requiring them to actively 
check for updates.

- Notificatons are handled using `ntfy.sh` which provides a free solution.

- ntfy lets you send push notifications to your phone or desktop via
scripts from any computer, using simple HTTP PUT or POST requests.

- Users are expected to create a `topic` on ntfy.sh in order to identify
their notification channel.

- ntfy documentation : `https://docs.ntfy.sh/`

- followup : 
https://www.notion.so/exordelabs/a52da9b348b148f687a85f6fab366e7e?v=e17138b296ef4dc1b9cf52dd758c1bb4&p=9e58c4e9fc334778a545dfff66bc34ae&pm=s
"""

import aiohttp
import argparse

from exorde.counter import AsyncItemCounter
from exorde.models import Ponderation


async def send_notification(
    command_line_arguments: argparse.Namespace, data: str
):
    """
    - In exorde-client, the `topic` is passed using the `ntfy` key and
    retrieved here using the command_line_arguments variable.
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://ntfy.sh/{command_line_arguments.ntfy}"
        payload = data.encode(encoding="utf-8")

        async with session.post(url, data=payload) as response:
            response_text = await response.text()
            return response_text


async def status_notification(
    ponderation: Ponderation,
    counter: AsyncItemCounter,
    quota_layer: dict[str, float],
    only_layer: dict[str, float],
    command_line_arguments: argparse.Namespace,
):
    """
    - status_notification is called from the `brain.py` right
      after `print_counts`
    """
    rep = 0
    for item in ponderation.weights:
        rep += await counter.count_occurrences("rep_" + item)
    rep += await counter.count_occurrences("other")
    await send_notification(
        command_line_arguments,
        f"You collected {rep} unique posts over the last 24h",
    )