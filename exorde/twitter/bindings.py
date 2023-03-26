from exorde.playwright import (
    on_available_browser_tab,
    response,
    bindings as __bindings__,
)
from aiosow.bindings import alias, wire

from exorde.twitter import (
    generate_twitter_url,
    scrap_twitter,
    response_to_tweet,
    twitter_to_exorde_format,
)

# twitter_url is a randomly generated url
alias("twitter_url")(generate_twitter_url)

# intercept adaptive.json
broadcast_tweet, on_tweet_reception_do = wire()
on_adaptive_response = response(lambda response: "adaptive" in response.url)
on_adaptive_response(broadcast_tweet(response_to_tweet))
on_available_browser_tab(scrap_twitter)

# tweet retrieval and format
broadcast_formated, on_formated_tweet_do = wire()
on_tweet_reception_do(broadcast_formated(twitter_to_exorde_format))

# when a tweet is formated, push it to batch preparation
# on_formated_tweet_do(build_batch)
