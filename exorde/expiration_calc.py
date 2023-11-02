"""
Calculate maximum expiration date of collected items base on their appearence 
frequency in the keyword list 

https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/keywords.txt
"""
import aiohttp
import asyncio
from collections import Counter
from exorde.get_keywords import get_keywords
from exorde.cache import cached

def calculate_word_freq(text_content):
    if text_content is not None:
        # Split the content into lines and remove trailing '\r'
        lines = [line.strip('\r').lower() for line in text_content]
        
        # Calculate the frequency of each word using Counter
        word_freq = Counter(lines)
        
        return dict(word_freq)
    else:
        return {}


@cached(6 * 60) # might collide with get_keywords cache so we delay it a lil # todo improve using a priority queue
async def retrieve_and_calculate_word_freq():
    text_content = await get_keywords() 
    word_freq = calculate_word_freq(text_content)
    return word_freq
