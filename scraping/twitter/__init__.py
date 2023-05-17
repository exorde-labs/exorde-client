import asyncio, logging, random
from dateutil import parser
from aiosow.bindings import option


def generate_twitter_url(keyword) -> str:
    return f"https://twitter.com/search?q={keyword}&src=typed_query&f=live"


# adaptive.json is a json request made on the website on search pages.
# It contains a list of tweets to be added to the feed
def response_to_tweet(response):
    for tweet in response["globalObjects"]["tweets"].values():
        yield tweet


# Define a function to generate a random value around the habit with the specified variation
random_habit_value = lambda habit, variation: habit + random.uniform(
    -variation, variation
)

# Define a function that returns a lambda function to generate a random value around the habit with the specified variation
randomize = lambda habit, variation: lambda: random_habit_value(habit, variation)

# Define lambda functions to use the random habit value
expert_typing_speed = randomize(0.08, 0.02)
fast_typing_speed = randomize(0.12, 0.01)
average_typing_speed = randomize(0.2, 0.01)
slow_typing_speed = randomize(0.3, 0.02)
typing_behaviors = (
    expert_typing_speed,
    fast_typing_speed,
    average_typing_speed,
    slow_typing_speed,
)


async def behaved_typing(input, content, behavior):
    for letter in content:
        await input.type(letter)
        await asyncio.sleep(behavior())


async def authenticate_twitter(page, twitter_username, twitter_password):
    logging.info("authenticating with twitter")
    email_input = page.locator(
        '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input'
    )
    await behaved_typing(email_input, twitter_username, random.choice(typing_behaviors))
    next_button = page.locator(
        '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div'
    )
    await asyncio.sleep(random.uniform(1, 5))
    await next_button.click()
    password_input = page.locator(
        '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'
    )
    await asyncio.sleep(random.uniform(1, 2))
    await behaved_typing(
        password_input, twitter_password, random.choice(typing_behaviors)
    )

    login_button = page.locator(
        '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div'
    )
    await asyncio.sleep(random.uniform(3, 5))
    await login_button.click()


class MissingParameterError(Exception):
    pass


async def scrap_twitter(page, twitter_url, twitter_username, twitter_password):
    logging.info('Scraping "%s"', twitter_url)
    __id__, page = page
    page = page["page"]
    await page.goto(twitter_url, timeout=80000)
    await asyncio.sleep(random.uniform(1, 2))
    logging.info(page.url)
    if "flow/login" in page.url:
        if not twitter_username:
            raise MissingParameterError(
                "twitter_username could not be found, scrap_twitter prevented"
            )
        if not twitter_password:
            raise MissingParameterError(
                "twitter_password could not be found, scrap_twitter prevented"
            )
        await authenticate_twitter(page, twitter_username, twitter_password)
    await asyncio.sleep(random.uniform(10, 15))
    await page.goto(twitter_url, timeout=80000)
    scroll = """
    var lookup = 0;
    setInterval( () => {
      lookup += 1000;
      scroll(0, lookup);
    }, 750)
    """
    await page.evaluate(scroll)


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
