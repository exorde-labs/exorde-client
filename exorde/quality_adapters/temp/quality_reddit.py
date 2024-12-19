
import json
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

async def find_reddit_post_on_direct_url(app, url):
    last_p_block_text = ""

    def convert_to_old_url(url):
        # Parse the input URL
        parsed_url = urlparse(url)
        # Check if the netloc (domain) starts with "www."
        if parsed_url.netloc.startswith("www."):
            # Remove "www." from the netloc
            netloc = parsed_url.netloc[4:]
        else:
            netloc = parsed_url.netloc
        # Check if the URL already starts with "https://old.reddit.com"
        if parsed_url.netloc == "old.reddit.com":
            return url  # It's already in the old format
        # Create the old Reddit URL by replacing the netloc and scheme
        old_reddit_url = urlunparse(
            (
                "https",
                "old.reddit.com",
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            )
        )
        return old_reddit_url

    def get_reddit_post_id(url):
        parts = url.split("/")
        if parts[-1] == "":
            post_id = parts[-2]
        else:
            post_id = parts[-1]
        return post_id

    post_id = get_reddit_post_id(convert_to_old_url(url))
    print("POST_ID IS {}".format(post_id))
    # request the URL with user-agent:
    response = await app["fetch"](convert_to_old_url(url))
    soup = BeautifulSoup(response, "html.parser")
    # find first div with id="thing_t1_POSTID"
    try:
        class_substring = "thing_t1_{}".format(post_id)
        r = soup.find("div", {"id": class_substring})
        last_p_block_text = r.find_all("p")[-1].get_text()
    except Exception as e:
        print("[Reddit] Error: ", e)
        raise(e)
    return last_p_block_text


async def processing_interface(app, args: dict) -> dict:
    url = args["url"]
    content = await find_reddit_post_on_direct_url(app, url)

    return { "adapter": content }
