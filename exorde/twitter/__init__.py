from dateutil import parser
import logging
import asyncio


def generate_twitter_url() -> str:
    return "https://twitter.com/search?q=BTC&src=typed_query&f=live"


# adaptive.json is a json request made on the website on search pages.
# It contains a list of tweets to be added to the feed
def response_to_tweet(response):
    for tweet in response["globalObjects"]["tweets"].values():
        yield tweet


async def scrap_twitter(page, pages, twitter_url):
    logging.info('Scraping "%s"', twitter_url)
    await pages[page]["page"].goto(twitter_url, timeout=80000)
    await asyncio.sleep(0.1)
    scroll = """
    var lookup = 0;
    setInterval( () => {
      lookup += 1000;
      scroll(0, lookup);
    }, 750)
    """
    await pages[page]["page"].evaluate(scroll)


twitter_to_exorde_format = lambda data: {
    "entities": [],
    "item": {
        "Author": "",
        "Content": data["full_text"].replace("\n", "").replace("'", "''"),
        "Controversial": data.get("possibly_sensitive", False),
        "CreationDateTime": parser.parse(data["created_at"]).isoformat(),
        "Description": "",
        "DomainName": "twitter.com",
        "Language": data["lang"],
        "Reference": "",
        "Title": "",
        "Url": f"https://twitter.com/a/status/{data['id_str']}",
        "internal_id": str(data["id"]),
        "internal_parent_id": None,
        "mediaType": "",
        # "source": data['source'], # new
        # "nbQuotes": data['quote_count'], # new
        "nbComments": data["reply_count"],
        "nbLiked": data["favorite_count"],
        "nbShared": data["retweet_count"],
        # "isQuote": data['is_quote_status'] # new
    },
    "keyword": "",
    "links": [],
    "medias": [],
    "spotterCountry": "",
    "tokenOfInterest": [],
}
