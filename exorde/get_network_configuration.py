import aiohttp, json


async def get_network_configuration() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/ClientNetworkConfig.json"
        ) as response:
            json_content = await response.text()
            return json.loads(json_content)
