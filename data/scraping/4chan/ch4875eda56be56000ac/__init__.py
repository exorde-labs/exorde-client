import hashlib
import re
from typing import AsyncGenerator
from io import StringIO
from html.parser import HTMLParser
from datetime import datetime, timedelta, date
import aiohttp
import json
import random
import logging
from random import randrange
from exorde_data import Item
from flashtext import KeywordProcessor

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

#### --------------------------------------------------------------

# List of board JSON API endpoints
board_json_api_endpoints = [
    "https://a.4cdn.org/news/catalog.json",
    "https://a.4cdn.org/biz/catalog.json",
    "https://boards.4channel.org/sci/catalog.json",
    "https://boards.4channel.org/g/catalog.json",
]

BAD_WORDS_ENDPOINT = "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/bad_words_list.txt"

#### --------------------------------------------------------------


def is_within_timeframe_seconds(datetime_str, timeframe_sec):
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


def is_within_timeframe_seconds_iso(datetime_str, timeframe_sec):
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


def convert_timestamp(timestamp):
    dt = datetime.utcfromtimestamp(int(timestamp))
    formatted_dt = dt.strftime("%Y-%m-%dT%H:%M:%S.00Z")
    return formatted_dt


########################################################################


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def gen_chan(r):
    for idx, page in enumerate(r):
        for thread in r[idx]["threads"]:
            yield thread


def get_threads(threads, key: str, default="NaN"):
    return threads.get(key, default)


def clean_text(text):
    output_text = re.sub(r">>[0-9]*", " ", text)
    output_text = re.sub(r"http\S+", " ", output_text)
    return output_text


def load_file_words(file_path):
    with open(file_path, "r") as file:
        words = [line.strip() for line in file]
    return words


def remove_substrings(substrings, main_string):
    for substring in substrings:
        pattern = re.compile(re.escape(substring), re.IGNORECASE)
        main_string = pattern.sub("*" * len(substring), main_string)
    return main_string


def strip_from_bad_words(kw_processor, post):
    keywords = kw_processor.extract_keywords(post)
    clean_post = remove_substrings(keywords, post)
    return clean_post


def has_substring(substrings, main_string):
    for substring in substrings:
        if substring in main_string:
            return True
    return False


def is_older(timestamp, min_timestamp):
    try:
        input_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        min_time = datetime.strptime(min_timestamp, "%Y-%m-%d %H:%M:%S")
    except:
        input_time = timestamp
        min_time = min_timestamp
        pass
    return input_time < min_time


def remove_identic_substrings(lst):
    cleaned_list = []
    for i, s1 in enumerate(lst):
        is_substring = False
        for j, s2 in enumerate(lst):
            if i != j and s1 in s2:
                is_substring = True
                break
        if not is_substring:
            cleaned_list.append(s1)
    return cleaned_list


def has_repetitions(string, min_repetition_length):
    string = string.lower()  # Convert the string to lowercase
    n = len(string)
    count = 1
    for i in range(1, n):
        if string[i] == string[i - 1] or not string[i].isalpha():
            count += 1
            if count >= min_repetition_length:
                return True
        else:
            count = 1
    return False


def has_higher_uppercase_percentage(string, threshold_percent):
    total_length = len(string)
    uppercase_count = sum(1 for char in string if char.isupper())
    uppercase_percentage = (uppercase_count / total_length) * 100
    return uppercase_percentage > threshold_percent


def has_similar_chars(string, min_repetition_count):
    string = string.lower()  # Convert the string to lowercase
    char_counts = {}
    for char in string:
        if char.isalpha() or char in char_counts:
            char_counts[char] = char_counts.get(char, 0) + 1
            if char_counts[char] >= min_repetition_count:
                return True
    return False


def filter_strings_multiple_words_length(
    strings, min_length, min_length_composed
):
    filtered_list = []
    for string in strings:
        if len(string) >= min_length or has_higher_uppercase_percentage(
            string, threshold_percent=90
        ):
            if len(string.split()) <= 1 or len(string) >= min_length_composed:
                filtered_list.append(string)
    return filtered_list


def write_list_to_file(strings, filename):
    with open(filename, "w", encoding="utf-8") as file:
        for string in strings:
            file.write(string + "\n")


def get_subwords(word, min_length):
    """
    Helper function to generate subwords from a word.
    """
    subwords = []
    n = len(word)

    for i in range(n):
        for j in range(i + min_length, n + 1):
            subword = word[i:j]
            subwords.append(subword)

    return subwords


def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def split_strings_with_commas(strings):
    result = []
    for string in strings:
        if "," in string:
            result.extend(string.split(", "))
        else:
            result.append(string)
    return result


def remove_duplicates(strings):
    result = list(set(map(str.lower, strings)))
    return result


def filter_substrings(texts, substrings):
    output_texts = []
    for text in texts:
        is_ok = True
        for substring in substrings:
            if substring.lower() in text.lower():
                is_ok = False
                break
        if is_ok:
            output_texts.append(text)
    return output_texts


def extract_board_name(url):
    try:
        start_index = url.index(".org/") + 5
        end_index = url.index("/catalog.json")
        board_name = url[start_index:end_index]
        words = board_name.split("/")
        if 1 <= len(words) <= 4:
            return " ".join(words)
        else:
            return "default"
    except ValueError:
        return "default"


def return_true_with_probability(k):
    random_value = random.random()  # Generate a random value between 0 and 1
    return random_value < (
        k / 100
    )  # Check if the random value is less than the specified probability


############################################################################################################
##############                          COLLECTING POSTS ON 4CHAN                   ########################
############################################################################################################


async def scrape_4chan(
    max_oldness_seconds=60 * 50,
    maximum_to_collect=25,
    min_post_len=100,
    skipping_thread_probability_percent=10,
):
    """
    Scrapes 4chan board for recent posts and yields formatted items.

    Args:
        max_oldness_seconds (int): Maximum age of posts to scrape in seconds.
        maximum_to_collect (int): Maximum number of posts to collect.
        min_post_len (int): Minimum length of post content to consider.
        skipping_thread_probability_percent (int): Probability of skipping a thread.

    Yields:
        Item: Formatted item representing a post or comment.

    """
    # Select a random board JSON API endpoint
    selected_board_endpoint = random.choice(board_json_api_endpoints)

    # Log the selected board endpoint and maximum age of posts
    logging.info(
        "Scraping 4chan board: %s for posts not older than %s seconds.",
        selected_board_endpoint,
        max_oldness_seconds,
    )

    # Extract board name from the selected endpoint
    board_name_str = extract_board_name(selected_board_endpoint)

    # Initialize variables
    r = None
    thread_posts = []
    posts = []
    yielded_objects_count = 0

    # Perform HTTP request to the selected board endpoint
    async with aiohttp.ClientSession() as session:
        async with session.get(selected_board_endpoint) as response:
            if response.status == 200:
                data = await response.text()
                r = json.loads(data)

    # Check if the response was successful
    if r is None:
        raise Exception(
            "Could not gather 4chan content from the base endpoint."
        )

    # Load the bad words from the file
    bad_words = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BAD_WORDS_ENDPOINT) as response:
                if response.status == 200:
                    data = await response.text()
                    bad_words = data.split("\n")
    except:
        try:
            bad_words = load_file_words("bad_words_list.txt")
        except Exception as e:
            logging.info("[4chan] Error loading BAD WORDS: %s", e)

    # Initialize the bad words processor
    bad_words_processor = KeywordProcessor()
    for word in bad_words:
        bad_words_processor.add_keyword(word)

    # Calculate the timestamp threshold for oldness
    current_time = datetime.now()
    oldness_th = current_time - timedelta(seconds=max_oldness_seconds)
    oldness_th_timestamp = int(round(datetime.timestamp(oldness_th), 0))

    # Iterate over the threads in the board
    for it, threads in enumerate(gen_chan(r)):
        # Skip the thread based on the probability
        if return_true_with_probability(skipping_thread_probability_percent):
            continue

        # Extract thread details
        thread_title = strip_tags(get_threads(threads, "sub"))
        thread_id_number = get_threads(threads, "no")
        com = strip_tags(get_threads(threads, "com"))
        time = get_threads(threads, "time")
        author_thread = get_threads(threads, "name")
        thread_post = clean_text(com)
        thread_title = clean_text(thread_title)
        thread_id_number = str(thread_id_number)

        # Iterate over the comments in the thread
        if "last_replies" in threads:
            for comment in threads["last_replies"]:
                com_com = strip_tags(comment.get("com", "NaN"))
                com_id_number = comment.get("no", "NaN")
                time_com = comment.get("time", "NaN")
                author = comment.get("name", "Anonymous")
                post = clean_text(com_com)

                # Check if the comment meets the criteria
                if (
                    not is_older(time_com, oldness_th_timestamp)
                    and len(post) > min_post_len
                ):
                    posts.append(post)

                    # Format the output
                    comment_text_content = str(post)
                    comment_text_content = strip_from_bad_words(
                        bad_words_processor, comment_text_content
                    )
                    author = str(author)
                    sha1 = hashlib.sha1()
                    sha1.update(author.encode())
                    author_sha1_hex = str(sha1.hexdigest())
                    comment_datetime = convert_timestamp(str(time_com))
                    comment_id = str(com_id_number)
                    comment_url = (
                        "https://boards.4channel.org/"
                        + board_name_str
                        + "/thread/"
                        + thread_id_number
                        + "#p"
                        + comment_id
                    )

                    # Yield the formatted item
                    yield Item(
                        content=Content(comment_text_content),
                        author=Author(author_sha1_hex),
                        created_at=CreatedAt(comment_datetime),
                        title=Title(""),
                        domain=Domain("4channel.org"),
                        url=Url(comment_url),
                        external_id=ExternalId(comment_id),
                        external_parent_id=ExternalParentId(thread_id_number),
                    )

                    yielded_objects_count += 1
                    if yielded_objects_count > maximum_to_collect:
                        return

        # Check if the thread meets the criteria
        if (
            not is_older(time, oldness_th_timestamp)
            and len(thread_post) > min_post_len
        ):
            thread_posts.append(thread_post)

            # Format the output
            thread_post_text_content = str(thread_post)
            thread_post_text_content = strip_from_bad_words(
                bad_words_processor, thread_post_text_content
            )
            author = str(author_thread)
            sha1 = hashlib.sha1()
            sha1.update(author.encode())
            author_sha1_hex = str(sha1.hexdigest())
            thread_post_datetime = convert_timestamp(str(time))
            thread_post_id = str(thread_id_number)
            thread_post_url = (
                "https://boards.4channel.org/"
                + board_name_str
                + "/thread/"
                + thread_id_number
            )

            # Yield the formatted item
            yield Item(
                content=Content(thread_post_text_content),
                author=Author(author_sha1_hex),
                created_at=CreatedAt(thread_post_datetime),
                title=Title(thread_title),
                domain=Domain("4channel.org"),
                url=Url(thread_post_url),
                external_id=ExternalId(thread_post_id),
                external_parent_id=ExternalParentId(thread_id_number),
            )

            yielded_objects_count += 1

        if yielded_objects_count > maximum_to_collect:
            return


async def generate_url(keyword: str = "BTC"):
    logging.info("[Pre-collect] generating 4chan target URL.")
    return "https://boards.4channel.org/biz/"


async def query(parameters: dict) -> AsyncGenerator[Item, None]:
    url = await generate_url(**parameters)
    if not has_substring(["4chan", "4channel", "4cdn"], url):
        raise ValueError("Not a 4chan URL")
    async for result in scrape_4chan(
        max_oldness_seconds=120,
        maximum_to_collect=25,
        skipping_thread_probability_percent=20,
    ):
        yield result
