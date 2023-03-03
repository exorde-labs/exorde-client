from exc_twitter import bindings as __bindings__
from exc_twitter import tweet_wire
from . import format_tweet, spot, formated_tweet_wire

tweet_wire(format_tweet)
formated_tweet_wire(spot)
