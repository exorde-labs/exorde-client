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
import json
from exorde.bindings import wire

PARAMETERS = {
    'ipfs_path': {
        'default': 'http://ipfs-api.exorde.network/add',
    }
}

def twitter_to_exorde_format(data: dict) -> dict:
    return {
        "Author": "",
        "Content": data['full_text'],
        "Controversial": data.get('possibly_sensitive', False),
        "CreationDateTime": data['created_at'],
        "Description": "",
        "DomainName": "twitter.com",
        "Language": data['lang'],
        "Reference": "",
        "Title": "",
        "Url": f"https://twitter.com/a/status/{data['id_str']}",
        "internal_id": data['id'],
        "media_type": "",
        # "source": data['source'], # new
        # "nbQuotes": data['quote_count'], # new
        "nbComments": data['reply_count'],
        "nbLikes": data['favorite_count'],
        "nbShared": data['retweet_count'],
        # "isQuote": data['is_quote_status'] # new
    }

formated_tweet_trigger, formated_tweet_wire = wire(batch=100)
async def format_tweet(tweet, **kwargs):
    formated = twitter_to_exorde_format(tweet)
    await formated_tweet_trigger(formated, **kwargs)

async def spot(data:list, ipfs_path):
    ''''''
    tweets = [tweet[0] for tweet in data]
    print(json.dumps(tweets, indent=4), ipfs_path)
    # await upload_to_ipfs(data, ipfs_path)

# 1. retrieve tweets -> upload to ipfs -> data_spotting
# 2. get_job -> check
