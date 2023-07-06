import os
import re
import hashlib
import random
import datetime
from datetime import datetime as datett
from datetime import timedelta, date, timezone
from time import sleep
import pytz
import pandas as pd
import snscrape.modules
import dotenv
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from typing import AsyncGenerator
import pickle
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
import chromedriver_autoinstaller
import subprocess
import signal

# import geckodriver_autoinstaller

global driver
driver = None


MAX_EXPIRATION_HARDCODED_SECONDS = 90

#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################


def is_within_timeframe_seconds_snscrape(dt, timeframe_sec):
    # Get the current datetime in UTC
    current_dt = datett.now(timezone.utc)

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
    dt = datett.strptime(datetime_str, "%Y-%m-%d %H:%M:%S%z")
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
        logging.info(
            "[Twitter Snscrape] Attempt on keywords = %s", search_keyword
        )
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
        tr_post["external_parent_id"] = str(post["conversationId"])

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
            newness = is_within_timeframe_seconds_snscrape(
                tr_post["creationDateTime"], MAX_EXPIRATION_HARDCODED_SECONDS
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
        if (
            len(tr_post["content"]) >= 20
        ):  # yield only tweets with >=25 real text characters
            new_tweet_item = Item(
                content=Content(tr_post["content"]),
                author=Author(tr_post["author"]),
                created_at=CreatedAt(
                    convert_datetime(tr_post["creationDateTime"])
                ),
                title=Title(tr_post["title"]),
                domain=Domain("twitter.com"),
                url=Url(tr_post["url"]),
                external_id=ExternalId(tr_post["external_id"]),
                external_parent_id=ExternalParentId(
                    tr_post["external_parent_id"]
                ),
            )
            logging.info("[Twitter Snscrape] Found tweet: %s", new_tweet_item)
            yield new_tweet_item


def check_env():
    # Check if the .env file exists
    if not os.path.exists("/.env"):
        logging.info("/.env file does not exist.")
        return False

    # Read the .env file
    with open("/.env", "r") as f:
        content = f.read()

    # Split the content into lines
    lines = content.split("\n")

    # Define a dictionary to hold the keys and values
    keys = {
        "SCWEET_EMAIL": None,
        "SCWEET_PASSWORD": None,
        "SCWEET_USERNAME": None,
    }

    # Parse each line
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            if key in keys and value != "":
                keys[key] = value

    # Check if all keys have non-null values
    for key in keys:
        if keys[key] is None:
            return False

    # If all checks pass, return True
    return True


#############################################################################
#############################################################################
#############################################################################


current_dir = Path(__file__).parent.absolute()
# env_file = os.getenv("SCWEET_ENV_FILE", current_dir.parent.joinpath(".env"))
# dotenv.load_dotenv(env_file, verbose=True)


def load_env_variable(key, default_value=None, none_allowed=False):
    v = os.getenv(key, default=default_value)
    if v is None and not none_allowed:
        raise RuntimeError(f"{key} returned {v} but this is not allowed!")
    return v


def get_email(env):
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("SCWEET_EMAIL", none_allowed=True)


def get_password(env):
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("SCWEET_PASSWORD", none_allowed=True)


def get_username(env):
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("SCWEET_USERNAME", none_allowed=True)


def get_proxy(env):
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("HTTP_PROXY", none_allowed=True)


# import undetected_chromedriver as uc
# chromedriver_autoinstaller.install()

# current_dir = pathlib.Path(__file__).parent.absolute()


def get_data(card):
    """Extract data from tweet card"""
    image_links = []

    try:
        username = card.find_element(by=By.XPATH, value=".//span").text
    except:
        return

    try:
        handle = card.find_element(
            by=By.XPATH, value='.//span[contains(text(), "@")]'
        ).text
    except:
        return

    try:
        postdate = card.find_element(
            by=By.XPATH, value=".//time"
        ).get_attribute("datetime")
    except:
        return

    try:
        # text = card.find_element(by=By.XPATH, value='.//div[2]/div[2]/div[1]').text
        text = card.find_element(
            by=By.XPATH, value='.//div[@data-testid="tweetText"]'
        ).text
    except:
        text = ""

    try:
        embedded = card.find_element(
            by=By.XPATH, value=".//div[2]/div[2]/div[2]"
        ).text
    except:
        embedded = ""

    # text = comment + embedded

    try:
        reply_cnt = card.find_element(
            by=By.XPATH, value='.//div[@data-testid="reply"]'
        ).text
    except:
        reply_cnt = 0

    try:
        retweet_cnt = card.find_element(
            by=By.XPATH, value='.//div[@data-testid="retweet"]'
        ).text
    except:
        retweet_cnt = 0

    try:
        like_cnt = card.find_element(
            by=By.XPATH, value='.//div[@data-testid="like"]'
        ).text
    except:
        like_cnt = 0

    try:
        elements = card.find_elements(
            by=By.XPATH,
            value='.//div[2]/div[2]//img[contains(@src, "https://pbs.twimg.com/")]',
        )
        for element in elements:
            image_links.append(element.get_attribute("src"))
    except:
        image_links = []

    # if save_images == True:
    # 	for image_url in image_links:
    # 		save_image(image_url, image_url, save_dir)
    # handle promoted tweets

    try:
        promoted = (
            card.find_element(
                by=By.XPATH, value=".//div[2]/div[2]/[last()]//span"
            ).text
            == "Promoted"
        )
    except:
        promoted = False
    if promoted:
        return

    # get a string of all emojis contained in the tweet
    try:
        emoji_tags = card.find_elements(
            by=By.XPATH, value='.//img[contains(@src, "emoji")]'
        )
    except:
        return
    emoji_list = []
    for tag in emoji_tags:
        try:
            filename = tag.get_attribute("src")
            emoji = chr(
                int(
                    re.search(r"svg\/([a-z0-9]+)\.svg", filename).group(1),
                    base=16,
                )
            )
        except AttributeError:
            continue
        if emoji:
            emoji_list.append(emoji)
    emojis = " ".join(emoji_list)

    # tweet url
    try:
        element = card.find_element(
            by=By.XPATH, value='.//a[contains(@href, "/status/")]'
        )
        tweet_url = element.get_attribute("href")
    except:
        return

    tweet = (
        username,
        handle,
        postdate,
        text,
        embedded,
        emojis,
        reply_cnt,
        retweet_cnt,
        like_cnt,
        image_links,
        tweet_url,
    )
    return tweet


user_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
]


def get_chrome_path():
    if os.path.isfile("/usr/bin/chromium-browser"):
        return "/usr/bin/chromium-browser"
    elif os.path.isfile("/usr/bin/chromium"):
        return "/usr/bin/chromium"
    elif os.path.isfile("/usr/bin/chrome"):
        return "/usr/bin/chrome"
    elif os.path.isfile("/usr/bin/google-chrome"):
        return "/usr/bin/google-chrome"
    else:
        return None


def init_driver(
    headless=True,
    proxy=None,
    show_images=False,
    option=None,
    firefox=False,
    env="/.env",
):
    """initiate a chromedriver or firefoxdriver instance
    --option : other option to add (str)
    """
    global driver
    http_proxy = get_proxy(env)
    options = ChromeOptions()
    # driver_path = chromedriver_autoinstaller.install()
    logging.info("Adding options to Chromium Driver")
    binary_path = get_chrome_path()
    options.binary_location = binary_path
    logging.info(f"\tSelected Chrome executable path = {binary_path}")
    options.add_argument("--no-sandbox")
    options.add_argument(
        "--disable-blink-features"
    )  # Disable features that might betray automation
    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )  # Disables a Chrome flag that shows an 'automation' toolbar
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"]
    )  # Disable automation flags
    options.add_experimental_option(
        "useAutomationExtension", False
    )  # Disable automation extensions
    logging.info("\tDisable automation extensions & flags")
    options.add_argument(
        "--headless"
    )  # Ensure GUI is off. Essential for Docker.
    logging.info("\tHeadless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("disable-infobars")
    selected_user_agent = random.choice(user_agents)
    options.add_argument(f"user-agent={selected_user_agent}")
    logging.info("\tselected_user_agent :  %s", selected_user_agent)

    # add proxy if available
    if http_proxy is not None and len(http_proxy) > 6:
        logging.info("\tAdding a HTTP Proxy server: %s", http_proxy)
        options.add_argument("--proxy-server=%s" % http_proxy)
    if headless is True:
        options.add_argument("--disable-gpu")
        options.headless = True
    else:
        options.headless = False
    options.add_argument("log-level=3")
    if show_images == False and firefox == False:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    if option is not None:
        options.add_argument(option)

    driver_path = "/usr/local/bin/chromedriver"
    logging.info(f"Opening driver from path = {driver_path}")
    driver = webdriver.Chrome(options=options, executable_path=driver_path)

    driver.set_page_load_timeout(7)
    return driver


def log_search_page(
    since,
    until_local,
    lang,
    display_type,
    word,
    to_account,
    from_account,
    mention_account,
    hashtag,
    filter_replies,
    proximity,
    geocode,
    minreplies,
    minlikes,
    minretweets,
):
    """Search for this query between since and until_local"""
    global driver
    logging.info("Log search page =  %s", driver)
    # format the <from_account>, <to_account> and <hash_tags>
    from_account = (
        "(from%3A" + from_account + ")%20" if from_account is not None else ""
    )
    to_account = (
        "(to%3A" + to_account + ")%20" if to_account is not None else ""
    )
    mention_account = (
        "(%40" + mention_account + ")%20"
        if mention_account is not None
        else ""
    )
    hash_tags = "%20(%23" + hashtag + ")%20" if hashtag is not None else ""

    since = ""  # "since%3A" + since + "%20"

    if display_type == "Latest" or display_type == "latest":
        display_type = "&f=live"
    # proximity
    if proximity == True:
        proximity = "&lf=on"  # at the end
    else:
        proximity = ""

    path = (
        "https://twitter.com/search?q="
        + word
        + hash_tags
        + since
        + "&src=typed_query"
        + display_type
        + proximity
    )
    driver.get(path)
    return path


def type_slow(string, element):
    for character in str(string):
        element.send_keys(character)
        sleep(random.uniform(0.05, 0.37))


def print_first_and_last(s):
    if len(s) < 2:
        return s
    else:
        return s[0] + "***" + s[-1]


def check_and_kill_processes(process_names):
    for process_name in process_names:
        try:
            # Find processes by name
            result = subprocess.check_output(["pgrep", "-f", process_name])
            # If the previous command did not fail, we have some processes to kill
            if result:
                logging.info(
                    f"[Chrome] Killing old processes for: {process_name}"
                )
                subprocess.run(["pkill", "-f", process_name])
        except subprocess.CalledProcessError:
            # If pgrep fails to find any processes, it throws an error. We catch that here and assume no processes are running
            logging.info(
                f"[Chrome] No running processes found for: {process_name}"
            )


def save_cookies(driver_):
    # Save cookies
    pickle.dump(driver_.get_cookies(), open("cookies.pkl", "wb"))
    logging.info("[Twitter Chrome] Saved cookies.")


def clear_cookies():
    try:
        open("cookies.pkl", "wb").close()
        logging.info("Cleared cookies.")
    except Exception as e:
        logging.info("Clear cookies error: %s", e)


def log_in(env="/.env", wait=4):
    global driver

    cookies_added = 0
    driver.get("https://www.twitter.com/")
    target_home_url = "https://twitter.com/home"
    target_broad = "twitter.com/home"
    try:
        # Load cookies if they exist
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
        except:
            logging.info("[Cookies] File not found, no cookies.")

        logging.info("[Twitter Chrome] loading existing cookies... ")
        for cookie in cookies:
            logging.info("\t-%s", cookie)
            # Add each cookie to the browser
            # Check if the cookie is expired
            if (
                "expiry" in cookie
                and datett.fromtimestamp(cookie["expiry"]) < datett.now()
            ):
                logging.info("Cookie expired")
            else:
                try:
                    driver.add_cookie(cookie)
                    cookies_added += 1
                except exceptions.InvalidCookieDomainException as e:
                    logging.info(
                        "[Twitter Chrome] Not importable cookie: %s", e
                    )
                except:
                    logging.info(
                        "[Twitter Chrome] Error for cookie %s", cookie
                    )
                    cookies_not_imported += 1
    except Exception as e:
        logging.exception("An error occured retrieving cookies: %s", e)

    logging.info("[Twitter Chrome] refreshing to Home after cookie import.")
    sleep(random.uniform(1, 4))
    driver.get(target_home_url)
    logging.info("[Twitter Chrome] Checking if we are on same URL...")
    sleep(random.uniform(1, 5))
    # Check if we are indeed on the target URL
    logging.info("[Twitter Chrome] Current URL = %s", str(driver.current_url))
    if not target_broad in driver.current_url:
        logging.info("[Twitter] Not on target, let's log in...")
        clear_cookies()
        email = get_email(env)  # const.EMAIL
        password = get_password(env)  # const.PASSWORD
        username = get_username(env)  # const.USERNAME

        logging.info("\t[Twitter] Email provided =  %s", email)
        logging.info(
            "\t[Twitter] Password provided =  %s",
            print_first_and_last(password),
        )
        logging.info("\t[Twitter] Username provided =  %s", username)

        driver.get("https://twitter.com/i/flow/login")

        email_xpath = '//input[@autocomplete="username"]'
        password_xpath = '//input[@autocomplete="current-password"]'
        username_xpath = '//input[@data-testid="ocfEnterTextTextInput"]'

        sleep(random.uniform(wait, wait + 1))

        # enter email
        logging.info("Entering Email..")
        email_el = driver.find_element(by=By.XPATH, value=email_xpath)
        sleep(random.uniform(wait, wait + 1))
        # email_el.send_keys(email)
        type_slow(email, email_el)

        sleep(random.uniform(wait, wait + 1))
        email_el.send_keys(Keys.RETURN)
        sleep(random.uniform(wait, wait + 1))
        # in case twitter spotted unusual login activity : enter your username
        if check_exists_by_xpath(username_xpath, driver):
            logging.info("Unusual Activity Mode")
            username_el = driver.find_element(
                by=By.XPATH, value=username_xpath
            )
            sleep(random.uniform(wait, wait + 1))
            logging.info("\tEntering username..")
            # username_el.send_keys(username)
            type_slow(username, username_el)
            sleep(random.uniform(wait, wait + 1))
            username_el.send_keys(Keys.RETURN)
            sleep(random.uniform(wait, wait + 1))
        # enter password
        password_el = driver.find_element(by=By.XPATH, value=password_xpath)
        # password_el.send_keys(password)
        logging.info("\tEntering password...")
        type_slow(password, password_el)
        sleep(random.uniform(wait, wait + 1))
        password_el.send_keys(Keys.RETURN)
        sleep(random.uniform(wait, wait + 1))
        save_cookies(driver)
    else:
        logging.info("[Twitter] We are already logged in")


def is_within_timeframe_seconds(dt_str, timeframe_sec):
    # Convert the datetime string to a datetime object
    dt = datett.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Make it aware about timezone (UTC)
    dt = dt.replace(tzinfo=timezone.utc)

    # Get the current datetime in UTC
    current_dt = datett.now(timezone.utc)

    # Calculate the time difference between the two datetimes
    time_diff = current_dt - dt

    # Check if the time difference is within the specified timeframe in seconds
    if abs(time_diff) <= timedelta(seconds=timeframe_sec):
        return True
    else:
        return False


max_old_tweets_successive = 3


def keep_scroling(
    data,
    tweet_ids,
    scrolling,
    tweet_parsed,
    limit,
    scroll,
    last_position,
    save_images=False,
):
    """scrolling function for tweets crawling"""
    global driver

    save_images_dir = "/images"
    if save_images == True:
        if not os.path.exists(save_images_dir):
            os.mkdir(save_images_dir)

    successsive_old_tweets = 0
    while scrolling and tweet_parsed < limit:
        sleep(random.uniform(0.5, 1.5))
        # get the card of tweets

        page_cards = driver.find_elements(
            by=By.XPATH, value='//article[@data-testid="tweet"]'
        )  # changed div by article
        for card in page_cards:
            tweet = get_data(card)
            if tweet:
                # check if the tweet is unique
                tweet_id = "".join(tweet[:-2])
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    data.append(tweet)
                    last_date = str(tweet[2])
                    if is_within_timeframe_seconds(
                        last_date, MAX_EXPIRATION_HARDCODED_SECONDS
                    ):
                        logging.info(
                            "[Twitter Selenium] Found Tweet:  %s", tweet
                        )
                        tweet_parsed += 1
                        successsive_old_tweets = 0
                    else:
                        successsive_old_tweets += 1
                    if (
                        successsive_old_tweets >= max_old_tweets_successive
                        or tweet_parsed >= limit
                    ):
                        return (
                            data,
                            tweet_ids,
                            scrolling,
                            tweet_parsed,
                            scroll,
                            last_position,
                        )
        scroll_attempt = 0
        while tweet_parsed < limit:
            # check scroll position
            scroll += 1
            sleep(random.uniform(0.5, 1.5))
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1
                # end of scroll region
                if scroll_attempt >= 2:
                    scrolling = False
                    break
                else:
                    sleep(random.uniform(0.5, 1.5))  # attempt another scroll
            else:
                last_position = curr_position
                break
    return data, tweet_ids, scrolling, tweet_parsed, scroll, last_position


def check_exists_by_link_text(text, driver):
    try:
        driver.find_element_by_link_text(text)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_xpath(xpath, driver):
    timeout = 3
    try:
        driver.find_element(by=By.XPATH, value=xpath)
    except NoSuchElementException:
        return False
    return True


def extract_tweet_info(tweet_tuple):
    content = tweet_tuple[3]
    author = tweet_tuple[0]
    created_at = tweet_tuple[2]
    title = tweet_tuple[0]
    domain = "twitter.com"
    url = tweet_tuple[-1]
    external_id = url.split("/")[
        -1
    ]  # This assumes that the tweet ID is always the last part of the URL.

    return content, author, created_at, title, domain, url, external_id


async def scrape_(
    until=None,
    keyword="bitcoin",
    to_account=None,
    from_account=None,
    mention_account=None,
    interval=5,
    lang=None,
    headless=True,
    limit=float("inf"),
    display_type="latest",
    resume=False,
    proxy=None,
    hashtag=None,
    max_items_to_collect=100,
    show_images=False,
    save_images=False,
    save_dir="outputs",
    filter_replies=False,
    proximity=False,
    max_search_page_tries=3,
    geocode=None,
    minreplies=None,
    minlikes=None,
    minretweets=None,
) -> AsyncGenerator[Item, None]:
    """
    Asynchronously scrape data from twitter using requests, starting from <since> until <until>. The program make a search between each <since> and <until_local>
    until it reaches the <until> date if it's given, else it stops at the actual date.

    Yields:
    Item: containing all tweets scraped with the associated features.
    """
    global driver
    logging.info("\tScraping latest tweets on keyword =  %s", keyword)
    # ------------------------- Variables :
    # list that contains all data
    data = []
    # unique tweet ids
    tweet_ids = set()
    # start scraping from <since> until <until>
    since = datetime.date.today().strftime("%Y-%m-%d")
    # add the <interval> to <since> to get <until_local> for the first refresh
    until_local = datetime.datetime.strptime(
        since, "%Y-%m-%d"
    ) + datetime.timedelta(days=interval)
    # if <until>=None, set it to the actual date
    if until is None:
        until = datetime.date.today().strftime("%Y-%m-%d")
    since = until
    # set refresh at 0. we refresh the page for each <interval> of time.
    refresh = 0

    # ------------------------- start scraping : keep searching until until
    # open the file
    logging.info("\tStart collecting tweets....")
    nb_search_tries = 0
    # log search page for a specific <interval> of time and keep scrolling unltil scrolling stops or reach the <until>
    while True:
        if (
            nb_search_tries >= max_search_page_tries
            or len(data) >= max_items_to_collect
        ):
            break

        scroll = 0
        if type(since) != str:
            since = datetime.datetime.strftime(since, "%Y-%m-%d")
        if type(until_local) != str:
            until_local = datetime.datetime.strftime(until_local, "%Y-%m-%d")

        # logging.info("Start log_search_page....")
        nb_search_tries += 1
        path = log_search_page(
            word=keyword,
            since=since,
            until_local=until_local,
            to_account=to_account,
            from_account=from_account,
            mention_account=mention_account,
            hashtag=hashtag,
            lang=lang,
            display_type=display_type,
            filter_replies=filter_replies,
            proximity=proximity,
            geocode=geocode,
            minreplies=minreplies,
            minlikes=minlikes,
            minretweets=minretweets,
        )
        refresh += 1
        # logging.info("Start execute_script....")
        last_position = driver.execute_script("return window.pageYOffset;")
        scrolling = True
        # logging.info("looking for tweets between " + str(since) + " and " + str(until_local) + " ...")
        logging.info("\tURL being parsed :  %s", str(path))
        tweet_parsed = 0
        sleep(random.uniform(0.5, 1.5))
        # logging.info("Start scrolling & get tweets....")
        (
            data,
            tweet_ids,
            scrolling,
            tweet_parsed,
            scroll,
            last_position,
        ) = keep_scroling(
            data,
            tweet_ids,
            scrolling,
            tweet_parsed,
            limit,
            scroll,
            last_position,
        )

        if scroll > 50:
            logging.debug("\tReached 50 scrolls: breaking")
            break
        if type(since) == str:
            since = datetime.datetime.strptime(
                since, "%Y-%m-%d"
            ) + datetime.timedelta(days=interval)
        else:
            since = since + datetime.timedelta(days=interval)
        if type(since) != str:
            until_local = datetime.datetime.strptime(
                until_local, "%Y-%m-%d"
            ) + datetime.timedelta(days=interval)
        else:
            until_local = until_local + datetime.timedelta(days=interval)

        for tweet_tuple in data:
            # ex: ('xxxxx', '@xxxx', '2023-06-16T10:10:59.000Z',
            # 'xx\n@xxxx\n·\nJun 16', '#Criptomoedas #Bitcoin\nNesta quinta-feira, 15,
            # a BlackRock solicitou a autorização para ofertar um fundo negociado em bolsa (ETF) de bitcoin nos Estados Unidos.\nSe aprovado, o
            # ETF será o primeiro dos Estados Unidos de bitcoin à vista.', '', '1', '', '1',
            # ['https://pbs.twimg.com/card_img/12.21654/zd45zz5?format=jpg&name=small'], 'https://twitter.com/xxxxx/status/1231456479')
            # Create a new sha1 hash
            (
                content_,
                author_,
                created_at_,
                title_,
                domain_,
                url_,
                external_id_,
            ) = extract_tweet_info(tweet_tuple)
            if (
                keyword.lower() in author_.lower()
                and not keyword.lower() in content_.lower()
            ):
                logging.info(
                    "Keyword not found in text, but in author's name, skipping this false positive."
                )
                continue
            sha1 = hashlib.sha1()
            # Update the hash with the author string encoded to bytest
            try:
                author_ = author_
            except:
                author_ = "unknown"
            sha1.update(author_.encode())
            author_sha1_hex = sha1.hexdigest()

            new_tweet_item = Item(
                content=Content(content_),
                author=Author(author_sha1_hex),
                created_at=CreatedAt(created_at_),
                title=Title(title_),
                domain=Domain(domain_),
                url=Url(url_),
                external_id=ExternalId(external_id_),
            )
            yield new_tweet_item


#############################################################################
#############################################################################
#############################################################################


def convert_spaces_to_percent20(input_string):
    return input_string.replace(" ", "%20")


async def generate_url(keyword: str = "BTC", live=True):
    logging.info("[Pre-collect] generating Twitter target URL.")
    base_url = f"https://twitter.com/search?q={convert_spaces_to_percent20(keyword)}&src=typed_query"
    if live:
        base_url = base_url + "&f=live"
    return base_url


async def query(parameters: dict) -> AsyncGenerator[Item, None]:
    global driver
    url = await generate_url(**parameters["url_parameters"])
    url_parts = url.split("twitter.com/")[1].split("&")
    search_keyword = ""
    if url_parts[0].startswith("search"):
        search_keyword = url_parts[0].split("q=")[1]

    if len(search_keyword) == 0:
        logging.info("keyword not found, can't search tweets using snscrape.")
        search_keyword = "crypto"

    search_keyword = convert_spaces_to_percent20(search_keyword)
    logging.info("[Twitter] internal Keyword used = %s", search_keyword)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    select_login_based_scraper = False
    if check_env():
        select_login_based_scraper = True
    if select_login_based_scraper:
        # Selenium track A: login based
        try:
            # Usage
            check_and_kill_processes(
                ["chromium", "chromedriver", "google-chrome"]
            )
            try:
                logging.info("[Twitter] Open driver")
                driver = init_driver(
                    headless=True, show_images=False, proxy=None
                )
                logging.info("[Twitter] Chrome Selenium Driver =  %s", driver)
                logging.info("[TWITTER LOGIN] Trying...")
                log_in()
                logging.info("[Twitter] Logged in.")
            except Exception as e:
                logging.debug("Exception during Twitter Init:  %s", e)

            try:
                nb_tweets_wanted = 50
                async for result in scrape_(
                    keyword=search_keyword,
                    display_type="latest",
                    limit=nb_tweets_wanted,
                ):
                    yield result
            except Exception as e:
                logging.info("Failed to scrape_() tweets. Error =  %s", e)
                pass
        except Exception as e:
            logging.info("[Twitter] Exception in during execution =  %s", e)
        finally:
            try:
                if driver is not None:
                    logging.info("[Twitter] Close driver")
                    driver.close()
                    sleep(3)  # the 3 seconds rule
                    logging.info("[Twitter] Quit driver")
                    driver.quit()
            except Exception as e:
                logging.info(
                    "[Twitter Driver] Exception while closing/quitting driver =  %s",
                    e,
                )

    else:
        logging.getLogger("snscrape").setLevel(logging.WARNING)
        # SNSCRAPE track b
        nb_tweets_wanted = 30
        select_top_tweets = False
        if "f=live" not in url_parts:
            select_top_tweets = True

        async for result in get_sns_tweets(
            search_keyword, select_top_tweets, nb_tweets_wanted
        ):
            yield result
