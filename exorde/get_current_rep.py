import aiohttp
import json


async def get_current_rep(main_address):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/Stats/leaderboard.json"
        ) as response:
            leaderboard = json.loads(await response.text())
            return int(0) # unused
