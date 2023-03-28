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
from exorde.translation.bindings import on_translated_do, translate
from exorde.twitter.bindings import on_formated_tweet_do
from exorde.ipfs.bindings import push_to_ipfs, on_new_cid_do
from exorde.xyake.bindings import on_keywords_extracted_do, populate_keywords

# when a tweet is formated, push it to translation
on_formated_tweet_do(translate)

on_translated_do(populate_keywords)

on_keywords_extracted_do(lambda value: print(value))

when_item_is_ready = lambda v: v
when_item_is_ready(push_to_ipfs)

# print new cids
on_new_cid_do(lambda value: print(value))
