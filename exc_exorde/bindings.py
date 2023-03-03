from exc_twitter import bindings as __bindings__
from exc_twitter import tweet_wire
from . import format_tweet, spot, formated_tweet_wire
from exorde.bindings import wire

tweet_wire(format_tweet)
batch_for_ipfs_trigger, batch_ready_for_ipfs = wire(batch=2)
formated_tweet_wire(batch_for_ipfs_trigger)
batch_ready_for_ipfs(spot)
