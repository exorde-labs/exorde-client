import logging, os, random
import aiohttp

from exorde.spot.bindings import spotting
from exorde.validation.bindings import validator, validator_vote
from exorde.protocol import bindings as __bindings__

from exorde.translation.bindings import translate
from exorde.xyake.bindings import populate_keywords

from aiosow.bindings import setup, wrap, alias


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
                logging.error(f"Failed to fetch file, status code: {resp.status}")
                return []


alias("keyword")(lambda keywords_list: random.choice(keywords_list)).replace(" ", "%20")


@setup
def print_pid():
    logging.info("pid is %s", os.getpid())


"""
# Spotting
Spotting processes are expressed as functions that take and return 1 item
"""

spotting(translate)
spotting(populate_keywords)

"""
# Validation
Validators are expressed as function that take and return a list of items
"""


# equivalent to `validator(filter_something)`
@validator
def filter_something(items):
    return items


"""
# Votes (validation)
Votes are expressed as function that take a liste of items and return an integer

The voting system is an unanimous consent, if even a single vote function negates
the batch, the vote fails and the batch is not accepted.
"""


@validator_vote
def vote_something(items):
    return 1
