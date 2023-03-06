from exorde.bindings import setup, curse

from exc_twitter import bindings as __bindings__
from exc_twitter import tweet_wire

from . import (
    format_tweet,
    spot,
    formated_tweet_wire,
    instanciate_w3,
    choose_w3_gateway
)

setup()(instanciate_w3)
tweet_wire(format_tweet)
formated_tweet_wire(spot)
curse('w3_gateway')(choose_w3_gateway)
