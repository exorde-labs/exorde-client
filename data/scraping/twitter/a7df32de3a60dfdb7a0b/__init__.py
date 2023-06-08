import hashlib
import re
from datetime import date
from typing import AsyncGenerator
from datetime import datetime, timedelta, date
import snscrape.modules
from exorde_data import Item


from exorde_data import (
    Item,
    Content,
    Author,
    CreatedAt,
    Title,
    Url,
    Domain,
    ExternalId,
    ExternalParentId,
)


async def is_within_timeframe_seconds(datetime_str, timeframe_sec):
    # Convert the datetime string to a datetime object
    dt = datetime.fromisoformat(datetime_str)

    # Get the current datetime in UTC
    current_dt = datetime.utcnow()

    # Calculate the time difference between the two datetimes
    time_diff = current_dt - dt

    # Check if the time difference is within 5 minutes
    if abs(time_diff) <= timedelta(seconds=timeframe_sec):
        return True
    else:
        return False


def cleanhtml(raw_html):
    """
    Clean HTML tags and entities from raw HTML text.

    Args:
        raw_html (str): Raw HTML text.

    Yields:
        str: Cleaned text without HTML tags and entities.
    """
    CLEANR = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
    cleantext = re.sub(CLEANR, "", raw_html)
    return cleantext


def convert_datetime(datetime_str):
    datetime_str = str(datetime_str)
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S%z")
    converted_str = dt.strftime("%Y-%m-%dT%H:%M:%S.00Z")
    return converted_str
########################################################################


async def get_sns_tweets(
    search_keyword, select_top_tweets, nb_tweets_wanted
) -> AsyncGenerator[Item, None]:
    """
    Get SNS tweets (Twitter) based on the given search keyword.
    Args:
        search_keyword (str): Keyword to search for tweets.
        nb_tweets_wanted (int): Number of tweets wanted.
    Returns:
        list: List of found tweets as dictionaries.
    """
    today = date.today()
    c = 0
    # found_tweets = []
    ## top == False
    if select_top_tweets == False:
        mode = snscrape.modules.twitter.TwitterSearchScraperMode.LIVE
    else:
        mode = snscrape.modules.twitter.TwitterSearchScraperMode.TOP

    try:
        attempted_tweet_collect = (
            snscrape.modules.twitter.TwitterSearchScraper(
                "{} since:{}".format(search_keyword, today), mode=mode
            ).get_items()
        )
    except:
        raise StopIteration

    for _post in attempted_tweet_collect:
        post = _post.__dict__

        tr_post = dict()
        c += 1
        if c > nb_tweets_wanted:
            break

        tr_post["external_id"] = str(post["id"])
        tr_post["external_parent_id"] = post["inReplyToTweetId"]

        tr_post["mediaType"] = "Social_Networks"
        tr_post["domainName"] = "twitter.com"
        tr_post["url"] = "https://twitter.com/ExordeLabs/status/{}".format(
            post["id"]
        )

        # Create a new sha1 hash
        sha1 = hashlib.sha1()
        # Update the hash with the author string encoded to bytest
        try:
            author = post["user"].displayname
        except:
            author = "unknown"
        sha1.update(author.encode())
        # Get the hexadecimal representation of the hash
        author_sha1_hex = sha1.hexdigest()
        tr_post["author"] = author_sha1_hex
        tr_post["creationDateTime"] = post["date"]
        if tr_post["creationDateTime"] is not None:
            newness = is_within_timeframe_seconds(
                tr_post["creationDateTime"], 480
            )
            if not newness:
                break  # finish the generation if we scrolled further than 5min old tweets

        tr_post["lang"] = post["lang"]
        tr_post["title"] = ""
        tr_post["content"] = cleanhtml(
            post["renderedContent"].replace("\n", "").replace("'", "''")
        )
        if tr_post["content"] in ("", "[removed]") and tr_post["title"] != "":
            tr_post["content"] = tr_post["title"]

        yield Item(
            content=Content(tr_post["content"]),
            author=Author(tr_post["author"]),
            creation_datetime=CreatedAt(convert_datetime(tr_post["creationDateTime"])),
            title=Title(tr_post["title"]),
            domain=Domain("twitter.com"),
            url=Url(tr_post["url"]),
            external_id=ExternalId(tr_post["external_id"]),
            external_parent_id=ExternalParentId(tr_post["external_parent_id"]),
        )


async def query(url: str) -> AsyncGenerator[Item, None]:
    if "twitter.com" not in url:
        raise ValueError("Not a twitter URL")
    url_parts = url.split("twitter.com/")[1].split("&")
    search_keyword = ""
    if url_parts[0].startswith("search"):
        search_keyword = url_parts[0].split("q=")[1]
    nb_tweets_wanted = 25
    select_top_tweets = False
    if "f=live" not in url_parts:
        select_top_tweets = True
    if len(search_keyword) == 0:
        print("keyword not found, can't search using snscrape.")
    print(
        "\nSearch_keyword = ",
        search_keyword,
        " select_top_tweets = ",
        select_top_tweets,
        nb_tweets_wanted,
    )
    print("Scraping....")
    async for result in get_sns_tweets(
        search_keyword, select_top_tweets, nb_tweets_wanted
    ):
        yield result
