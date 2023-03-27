"""
88888888b                                  dP
88                                         88
a88aaaa    dP. .dP .d8888b. 88d888b. .d888b88 .d8888b.
88         `8bd8'  88'  `88 88'  `88 88'  `88 88ooood8 '
88         .d88b.  88.  .88 88       88.  .88 88.  ...
88888888P dP'  `dP `88888P' dP       `88888P8 `88888P'  S
  
  Supported interface implementation for EXD mining.
"""

import exorde.playwright.bindings as _
import exorde.protocol.bindings as _
from exorde.twitter.bindings import on_formated_tweet_do
from exorde.ipfs.bindings import push_to_next_batch, on_new_cid_do

# when a tweet is formated, push it to batch preparation
on_formated_tweet_do(push_to_next_batch)

# print new cids
on_new_cid_do(lambda value: print(value))
