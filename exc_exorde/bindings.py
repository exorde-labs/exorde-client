

from exorde.bindings import routine, oversight

from exc_twitter import bindings as __bindings__
from exc_twitter import tweet_wire

from exc_exorde import (
    configuration,
    contracts_and_abi_cnf,
    contracts,
    format_tweet,
    spot,
    formated_tweet_wire,
    read_web3,
    write_web3
)

# routines with timeout= 0 are executed instantly
routine(60 * 5, timeout=0)(configuration)
oversight('configuration')(contracts_and_abi_cnf)
# choose a url_Skale and instanciate web3
oversight('configuration')(write_web3)
oversight('configuration')(read_web3)
oversight('read_web3')(contracts)

# tweet retrieval
tweet_wire(format_tweet)
formated_tweet_wire(spot)
