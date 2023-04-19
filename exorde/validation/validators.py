from exorde.validation.bindings import validator, validator_vote


"Validators are expressed as function that take and return a list of items"


@validator
def filter_something(items):
    return items


"""
Votes are expressed as function that take a liste of items and return an integer

The voting system is an unanimous consent, if even a single vote function negates
the batch, the vote fails and the batch is not accepted.
"""


@validator_vote
def vote_something(items):
    return 1
