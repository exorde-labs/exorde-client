import logging, os

from aiosow.command import run

from exorde.spot.bindings import spotting

from exorde.validation.bindings import validator, validator_vote
from exorde.translation.bindings import translate
from exorde.xyake.bindings import populate_keywords

from aiosow.bindings import setup


@setup
def print_pid():
    logging.info("pid is %s", os.getpid())


"""
# Spotting
Spotting processes are expressed as functions that take and return 1 item
"""

# spotting(translate)
# spotting(populate_keywords)

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


launch = lambda: run("exorde")
