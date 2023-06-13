import aiohttp


async def get_latest_tag():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.github.com/repos/6r17/test_versioning/releases/latest"
        ) as response:
            body = await response.json()
            return body["tag_name"]
