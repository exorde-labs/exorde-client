import aiohttp
import argparse


async def send_notification(
    command_line_arguments: argparse.Namespace, data: str
):
    """
    - ntfy lets you send push notifications to your phone or desktop via
    scripts from any computer, using simple HTTP PUT or POST requests.

    - Users are expected to create a `topic` on ntfy.sh in order to identify
    their notification channel.

    - ntfy documentation : `https://docs.ntfy.sh/`

    - In exorde-client, the `topic` is passed using the `ntfy` key and
    retrieved here using the command_line_arguments variable.

    - [followup](https://www.notion.so/exordelabs/a52da9b348b148f687a85f6fab366e7e?v=e17138b296ef4dc1b9cf52dd758c1bb4&p=9e58c4e9fc334778a545dfff66bc34ae&pm=s)
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://ntfy.sh/{command_line_arguments.ntfy}"
        payload = data.encode(encoding="utf-8")

        async with session.post(url, data=payload) as response:
            response_text = await response.text()
            return response_text
