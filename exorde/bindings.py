"""
88888888b                                  dP
88                                         88
a88aaaa    dP. .dP .d8888b. 88d888b. .d888b88 .d8888b.
88         `8bd8'  88'  `88 88'  `88 88'  `88 88ooood8 '
88         .d88b.  88.  .88 88       88.  .88 88.  ...
88888888P dP'  `dP `88888P' dP       `88888P8 `88888P'  S
  
  Supported composition for EXD mining.
"""

import logging

from exorde.twitter.bindings import on_formated_tweet_do
from exorde.translation.bindings import on_translated_do, translate
from exorde.xyake.bindings import on_keywords_extracted_do, populate_keywords
from exorde.ipfs.bindings import push_to_ipfs, on_new_cid_do
import exorde.protocol.bindings as _
from aiosow.routines import routine

from collections import deque

stack = deque(maxlen=1000)


def push_to_stack(value):
    global stack
    stack.append(value)


def print_stack():
    logging.info(f"{len(stack)} items ready to processed")


routine(1)(print_stack)

on_formated_tweet_do(push_to_stack)
# on_formated_tweet_do(translate)
# on_translated_do(populate_keywords)
# on_keywords_extracted_do(push_to_ipfs)
# on_new_cid_do(lambda value: print(value))
