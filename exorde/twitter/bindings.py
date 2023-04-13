import logging, json, asyncio
from aiosow.autofill import autofill
from aiosow.bindings import alias, wire, setup
from aiosow.routines import routine
from exorde.browser import intercept, goto, evaluate_expression
from exorde.twitter import (
    generate_twitter_url,
    twitter_to_exorde_format,
)

# twitter_url is a randomly generated url
alias("twitter_url")(generate_twitter_url)

# intercept adaptive.json
broadcast_tweet, on_tweet_reception_do = wire()


@intercept("adaptive")
async def intercept_adaptive(message, memory):
    try:
        for tweet in json.loads(message["result"]["body"])["globalObjects"][
            "tweets"
        ].values():
            await autofill(broadcast_tweet(lambda: tweet), args=[], memory=memory)
    except Exception as e:
        logging.debug(e)


scroll = """
var lookup = 0;
setInterval( () => {
  lookup += 1000;
  scroll(0, lookup);
}, 750)
"""


async def manage_page(page_websocket):
    await goto("https://twitter.com/search?q=btc&src=typed_query", page_websocket)
    await asyncio.sleep(0.2)
    await evaluate_expression(scroll, page_websocket)


setup(manage_page)
routine(60)(manage_page)

# TODO: on available page

# tweet retrieval and format
broadcast_formated, on_formated_tweet_do = wire()
on_tweet_reception_do(broadcast_formated(twitter_to_exorde_format))
