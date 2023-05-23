from aiosow.bindings import setup, wrap, alias
import aiohttp, random, logging


@setup
@wrap(lambda keywords_list: {"keywords_list": keywords_list})
async def fetch_lines_from_url() -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/keywords.txt"
        ) as resp:
            if resp.status == 200:
                content = await resp.text()
                lines = content.split("\n")
                return lines
            else:
                logging.error(
                    f"Failed to fetch file, status code: {resp.status}"
                )
                return []


alias("keyword")(
    lambda keywords_list: random.choice(keywords_list).replace(" ", "%20")
)
