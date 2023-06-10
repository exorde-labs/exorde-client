
import aiohttp
import json
import logging

async def log_current_rep(main_address):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/Stats/leaderboard.json"
        ) as response:
            leaderboard = json.loads(await response.text())
            logging.info(
                f"\n*********\n[REPUTATION] Current Main Address REP = {round(leaderboard.get(main_address, 0), 4)}\n*********\n"
            )