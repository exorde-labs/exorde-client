from exorde.playwright import (
    on_available_browser_tab,
    response,
    bindings as __bindings__,
)
from aiosow.bindings import alias, wire
from exorde.formated import broadcast_formated_when
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

on_tweet_reception_do(broadcast_formated_when(twitter_to_exorde_format))
