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


import logging, os, aiohttp, json, sys
from aiosow.bindings import setup, option, on
from aiosow.routines import routine

option(
    "--no_headless",
    action="store_true",
    default=False,
    help="Wether it should run in headless mode",
)
option(
    "--user_agent",
    default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    help="User-Agent used",
)
option("--tabs", default=1, help="Amount of tabs open")
option("--tab_lifetime", default=60, help="Time passed on each page")

option("--twitter_username", default=None, help="Twitter username")
option("--twitter_password", default=None, help="Twitter password")

option(
    "-m",
    "--main_address",
    help="Main Ethereum Address, which will get all REP & EXDT for this local worker contribution. Exorde Reputation is non-transferable. Correct usage example: -m 0x0F67059ea5c125104E46B46769184dB6DC405C42",
    required=False,
)
option(
    "--no_main_address",
    default=False,
    action="store_true",
    help="Bypass mandatory main_address",
)
option(
    "-wn",
    "--worker_name",
    default="keys",
    help="Worker name which will be used to store the keys at .config/exorde",
)


@setup
def set_protocol_buffers_python_implementation():
    os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


@setup
def run_forever():
    return {"run_forever": True}


@setup
@routine(60 * 5)
async def fetch_runtime_configuration():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/runtime.json"
        ) as response:
            response = await response.text()
            return json.loads(response)


def exit_like_a_gentlmen():
    logging.info(
        "We would like to inform you that the Exorde protocol is SHUTTING DOWN !"
    )
    sys.exit()


on("remote_kill", condition=lambda online: online)(exit_like_a_gentlmen)


@setup
def print_pid():
    logging.info("pid is %s", os.getpid())


"""
# Spotting
Spotting processes are expressed as functions that take and return 1 item
"""

option(
    "--no_spotting",
    action="store_true",
    default=False,
    help="Won't run spotting",
)

option("--source", nargs="+", help="Scraping module to be used")


@setup
def init_spotting(no_spotting, remote_kill, memory):
    if not no_spotting and not remote_kill:
        from exorde.protocol.spotting import bindings as __bindings__
        from exorde.protocol.spotting import applicator as spotting_applicator
        from exorde.protocol.spotting import filter as spotting_filter
        from exorde import keywords as __keywords__

        # from exorde.spotting import batch_applicator as spotting_batch_applicator
        from exorde.protocol.spotting.filters import (
            datetime_filter,
            unique_filter,
            format_assertion,
        )
        from exorde_lab.translation.bindings import translate
        from exorde_lab.xyake.bindings import populate_keywords
        from exorde_lab.meta_tagger import (
            meta_tagger_initialization,
            preprocess,
        )
        from exorde.drivers.meta_tagger import zero_shot

        setup(meta_tagger_initialization)

        spotting_filter(datetime_filter)
        spotting_filter(unique_filter)
        spotting_filter(format_assertion)

        spotting_applicator(preprocess)
        spotting_applicator(translate)
        spotting_applicator(populate_keywords)
        spotting_applicator(zero_shot)


"""
# Validation
Validators are expressed as function that take and return a list of items

# Votes (validation)
Votes are expressed as function that take a liste of items and return an integer

The voting system is an unanimous consent, if even a single vote function negates
the batch, the vote fails and the batch is not accepted.
"""

option(
    "--no_validation",
    action="store_true",
    default=False,
    help="Won't run validation",
)


@setup
def init_validation(no_validation, remote_kill):
    if not no_validation and not remote_kill:
        from exorde.protocol.validation.bindings import (
            validator as validation_validator,
        )
        from exorde.protocol.base import bindings as __bindings__
        from exorde.drivers.meta_tagger import tag
        from exorde_lab.meta_tagger import meta_tagger_initialization

        setup(meta_tagger_initialization)
        validation_validator(tag)
