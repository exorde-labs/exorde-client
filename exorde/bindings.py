"""
--------------------------------------------------------
88888888b                                  dP
88                                         88
a88aaaa    dP. .dP .d8888b. 88d888b. .d888b88 .d8888b.
88         `8bd8'  88'  `88 88'  `88 88'  `88 88ooood8 '
88         .d88b.  88.  .88 88       88.  .88 88.  ...
88888888P dP'  `dP `88888P' dP       `88888P8 `88888P'  S
--------------composition for EXD mining-----------------
"""


import logging, os, random, aiohttp, importlib
from aiosow.bindings import setup, wrap, alias, option

option(
    "no_headless",
    action="store_true",
    default=False,
    help="Wether it should run in headless mode",
)
option(
    "user_agent",
    default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    help="User-Agent used",
)
option("tabs", default=1, help="Amount of tabs open")
option("tab_lifetime", default=60, help="Time passed on each page")

option("twitter_username", default=None, help="Twitter username")
option("twitter_password", default=None, help="Twitter password")


@setup
def run_forever():
    return {"run_forever": True}


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


alias("keyword")(lambda keywords_list: random.choice(keywords_list).replace(" ", "%20"))


@setup
def print_pid():
    logging.info("pid is %s", os.getpid())


"""
# Spotting
Spotting processes are expressed as functions that take and return 1 item
"""

option(
    "no_spotting",
    action="store_true",
    default=False,
    help="Won't run spotting",
)

SOURCES = ("reddit", "twitter")

for source in SOURCES:
    option(
        f"no_{source}", action="store_true", default=False, help=f"Won't scrap {source}"
    )


@setup
def init_spotting(no_spotting, memory):
    if not no_spotting:
        from exorde.spotting.bindings import spotting
        from exorde.translation.bindings import translate
        from exorde.xyake.bindings import populate_keywords

        for source in SOURCES:
            if not memory[f"no_{source}"]:
                importlib.import_module(f"exorde.{source}.bindings")

        spotting(translate)
        spotting(populate_keywords)


"""
# Validation
Validators are expressed as function that take and return a list of items

# Votes (validation)
Votes are expressed as function that take a liste of items and return an integer

The voting system is an unanimous consent, if even a single vote function negates
the batch, the vote fails and the batch is not accepted.
"""

option(
    "no_validation",
    action="store_true",
    default=False,
    help="Won't run validation",
)


@setup
def init_validation(no_validation):
    if not no_validation:
        from exorde.validation.bindings import validator, validator_vote
        from exorde.protocol import bindings as __bindings__

        # equivalent to `validator(filter_something)`
        def filter_something(items):
            return items

        validator(filter_something)

        def vote_something(__items__):
            return 1

        validator_vote(vote_something)
