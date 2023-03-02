#! python3.10
'''
88888888b                                  dP
88                                         88
a88aaaa    dP. .dP .d8888b. 88d888b. .d888b88 .d8888b.
88         `8bd8'  88'  `88 88'  `88 88'  `88 88ooood8 '
88         .d88b.  88.  .88 88       88.  .88 88.  ...
88888888P dP'  `dP `88888P' dP       `88888P8 `88888P'  S

          Supported composition for EXD mining.
'''

from exorde.bindings import wire

from exc_twitter import tweet_wire
from exc_ipfs import upload_to_ipfs

PARAMETERS = {
    'ipfs_path': {
        'default': 'http://ipfs-api.exorde.network/add',
    }
}

def twitter_to_exorde_format(data: dict) -> dict:
    return data

formated_tweet_trigger, formated_tweet_wire = wire()
@tweet_wire
async def format_tweet(tweet):
    await formated_tweet_trigger(twitter_to_exorde_format(tweet))

async def spot(data, ipfs_path):
    '''
    Spotting data happens in two steps :
        - upload_to_ipfs
        - send a transaction to say "Job Done !"
    '''
    await upload_to_ipfs(data, ipfs_path)

formated_tweet_wire(spot)

# 1. retrieve tweets -> upload to ipfs -> data_spotting
# 2. get_job -> check
