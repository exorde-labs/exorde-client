import aiohttp


async def get_latest_tag():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.github.com/repos/exorde/exorde-client/releases/latest"
        ) as response:
            body = await response.json()
            return body["tag_name"]
