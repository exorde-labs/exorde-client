
# Exorde Open Source Bounties
<p align="center">
<img alt="logo_exorde" src="https://uploads-ssl.webflow.com/620398f412d5829aa28fbb86/62278b77803be26db0cfb903_mark-logo-color.png" style="float:left; height:69px; width:50px" /></p>

## Currently open bounties

The currently open bounties are findable in the Issues tab: https://github.com/exorde-labs/exorde-client/issues.

The open & competitive nature of Open Source development makes it likely for many developers to work on the same scraper/bounty, but only the first valid submission will be retained. Keep this in mind.

## **Introduction and Principle**

*Exorde stands as a testament to the power of decentralized data collection, and we believe that the key to unlocking its full potential lies in the hands of a decentralized community of developers and contributors. W*e celebrate the power of decentralized data collection and firmly believe that a thriving data ecosystem is built on the collective contributions of our vast community of developers and contributors. **The equation is simple: Better tools lead to more value creation, culminating in a robust data ecosystem.**

In order to lay a strong foundation for this collective effort, we at Exorde Labs have developed the **exorde-client** software, a versatile and resilient interface capable of seamless interaction with a variety of networks, including IPFS, blockchain, and the web. This platform offers developers a common playground where they can plug in and create modules.

**Exorde's architecture has two vital components:**

1. **Client core:** This is the stable part of the architecture that manages connectivity with IPFS, SKALE RPC blockchain read/write, the Exorde Protocol (smart contract interaction), and carries out regular code updates. As this part is stable and occasionally updated, it is not open to modification through this bounty program.
2. **Scrapers as plugins:** The client supports independent scrapers for each valuable data source (such as Reddit, Telegram, Twitter, Weibo, LinkedIn, etc). These operate autonomously within our architecture, ensuring that an issue with a single scraper doesn't affect the core client.

## **Pluggable Scrapers - Data Output Format & Interface**

In Exorde's architecture, scrapers function as individual plugins, each tailored to a specific data source. Designed to be stateless relative to the client core, these scrapers ensure maximum performance and scalability by minimizing dependencies and potential bottlenecks.

However, when necessary (such as for managing logins or cookies), scrapers can store state in local files, maintaining their inherent autonomy without sacrificing flexibility.

**Each scraper is required to implement an asynchronous method: `async def query(parameters: dict) -> AsyncGenerator[Item, None]`. This method takes a URL string and yields an asynchronous generator of `Item` objects. Each `Item` has a strict JSON format, as defined in** [Exorde's data schema](https://github.com/exorde-labs/exorde-client/blob/main/exorde/schema_valide.json)**.**

Please use: **`from typing import AsyncGenerator`** to use the AsyncGenerator.

## **Parameters is a dict that embed common & specific parameters for scrapers.**

**1. Common parameters:**
- **keyword** : (string) the keyword to collect data on. Depending on the searchability of the target website/platform, it could be ignored.
- **max_oldness_seconds**: (int) the max oldness of a post that is acceptable to be collected. (If timestamp/datetime of the post (comment, tweet, article, etc.) is older than this duration, throw the item)
- **maximum_items_to_collect**:  (int) maximum number of items to collect and generate before the scrapers stops.
- **min_post_length**:  (int) minimum post length (in number of characters) required to retain a post.

***Your scraper must use & respect these parameters.***

2. **Specific parameters**:
**Modules can be fed with specific parameters, if it makes sense, or parameters overriding default values of the common parameters. Modules with login-based techniques can assume to be fed their credentials in this dict (email, password, username, etc.)** 


The Scraper modules configuration (with general & specific parameters) can be found here: https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/modules_configuration.json


Expected generator output: the Item object
---

The **`Item`** class is a collection of predefined fields representing a data point's attributes. 

The data schema is enforced by the use of **madtypes** library, inside **exorde_data** local package. We suggest importing exorde_data like this:

```python
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
```

Your scraper logic must, at some point, **yield Items.** An example:

(the following example uses format_timestamp & is_within_timeframe_seconds, which high-level are suggestions)

```
content = data["data"]
item = Item(
    content=Content(content["selftext"]),
    author=Author(
        hashlib.sha1(
            bytes(content["author"], encoding="utf-8")
        ).hexdigest()
    ),
    created_at=CreatedAt(
        str(
            format_timestamp(
                content["created_utc"]
            )
        )
    ),
    title=Title(content["title"]),
    domain=Domain("reddit.com"),
    url=Url(content["url"]),
)
if is_within_timeframe_seconds(content["created_utc"],MAX_EXPIRATION_SECONDS):
    yield item
```

# **Technical Constraints**

Exorde's pluggable scrapers should adhere to specific technical constraints:

1. **Language & Libraries:** The scraper should be implemented in Python ≥3.10, and use specific libraries:
    - **aiohttp** for asynchronous HTTP requests
    - **hashlib** for secure hash and message digest algorithms
    - The user-agent used must be `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36`
    - **selenium (version 4.2.0)** & chromium+chromedriver **(REQUIRED if your scraper uses browser automation)**
        - It should collect data by scrolling uniformly, organically, and slowly, just like a human: no superfast scrolling, no dozens of tabs open at once.
        - It should use the following helper function:
            
            ```python
            def get_chrome_path():
                if os.path.isfile('/usr/bin/chromium-browser'):
                    return '/usr/bin/chromium-browser'
                elif os.path.isfile('/usr/bin/chromium'):
                    return '/usr/bin/chromium'
                elif os.path.isfile('/usr/bin/chrome'):
                    return '/usr/bin/chrome'
                elif os.path.isfile('/usr/bin/google-chrome'):
                    return '/usr/bin/google-chrome'
                else:
                    return None
            ```
            
        - It should use the following ChromeDriver options:
            
            ```python
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            <....>
            
            options = ChromeOptions()
            # driver_path = chromedriver_autoinstaller.install()
            logging.info("Adding options to Chromium Driver")
            binary_path = get_chrome_path()
            options.binary_location = binary_path
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-blink-features") # Disable features that might betray automation
            options.add_argument("--disable-blink-features=AutomationControlled") # Disables a Chrome flag that shows an 'automation' toolbar
            options.add_experimental_option("excludeSwitches", ["enable-automation"]) # Disable automation flags
            options.add_experimental_option('useAutomationExtension', False) # Disable automation extensions
            options.add_argument("--headless") # Ensure GUI is off. Essential for Docker.
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("disable-infobars")
            options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
            driver_path = '/usr/local/bin/chromedriver'
            driver = webdriver.Chrome(options=options, executable_path=driver_path)
            ```
            
    - **random** for generating random numbers
    - **logging** for event logging (normal logs to `level.INFO`, debug logs to `level.DEBUG`).
    - **Additional libraries are permitted**, as long as they don't require a refactoring of the existing client core. For automated browsers, staying with Selenium+Chromium WebDriver is recommended.
2. **Asynchronous Programming:** Leveraging Python's async and await syntax ensures non-blocking code execution and concurrent scraping, improving efficiency.
3. **Data Validation:** The data returned by the scraper must adhere to Exorde's strict JSON format. 

The execution environment is a Docker Container with a UNIX-based Python3.11 image.

# **Components**
In the following sections, we delve into a deeper understanding of the scraper structure, its essential components, and the requirements of each.

## **Scraper Interface**

The scraper interface is crucial to establish a link between the data source and Exorde's ecosystem. It is composed of three primary parts:

1. **`scrape(..)`**  This function implements the main scraping logic. You should express the main logic in this function and keep query() as simple & clear as possible, for maintenability.
    - You can split your scraping logic into multiple functions but the main logic should be in scrape(…)
2. **`query(parameters: dict):`** The main interface between the client core & your scraper.
3. **`Item Class:`** This class represents a data point to be scraped and contains the following attributes:
    - **`content`:** (**REQUIRED)** The content of the post (or comment, etc.), as a **string (str), stripped from any HTML (or equivalent) tags.**
    - **`author`: *(optional)*** The author of the post encoded in SHA1. We do not want an author's name in clear. Suggestion: *use hashlib + sha1.hexdigest()*
    - **`created_at`:** (**REQUIRED)** The timestamp of the post. This must adhere to a specific format (referenced in [Exorde's schema](https://github.com/exorde-labs/exorde-client/blob/main/exorde/schema_valide.json))
        - **ISO8601/RFC3339**
        - Regular expression: **^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(.[0-9]{1,6})?Z$**
        - **(REQUIRED) The date must be strictly UTC+0 (hence the Z in the format, for "zero hour offset" also known as "Zulu time" (UTC))**
        - Examples: “2025-08-12T12:53:12Z” or “2025-08-12T23:15:38.1234Z”
        - **Must be verifiable & real. Failure to do so will result in the entire code submission to be invalid.**
    - **`title`: *(optional)*** The title of the entity (article, post, thread, etc), if it exists
    - **`domain`:** (**REQUIRED)** The domain of the website. (example: twitter.com, reddit.com, weibo.com, linkedin.com, etc.)
    - **`url`:** (**REQUIRED)** The precise URL of the post. If the Item is a comment or a child of another entity, the URL has to reference it as precisely as possible. **The URL must be real & unique (this is critically important). Failure to do so will result in the entire code submission to be invalid.**
    - **`external_id`:** (**REQUIRED)** The external ID of the post. This ID has to be verified on the platform itself, it is not up to you. (example: 1675852288307391234 is a unique external_id of a tweet)
    - **`external_parent_id`:** ***(optional)*** The external ID of the parent post or thread. Has to be referenced if the post is a reply/child of a parent item (main article, main post, etc.) if possible.

## Code organization

**How to import exorde_data (& madtypes, used by exorde_data) during development ONLY.**

Please have exorde_data/ & madtypes/ folders in your root directory, if you fail to import it.  & install the exorde_data package:

`pip install —user exorde_data/`

.
├── exorde_data/
├── madtypes/
├── your_scraper.py

You can build & test your software like this during your development.

# Example

The following code is an example of how you can develop your scraper, which typical functions to include, how to import necessary modules.
You can observe how test_query() can work with query() and how to simulate the parameters dict, how to read values from it:

- [Hackernews forum scraper example](https://gist.github.com/MathiasExorde/104e99bcb9f87acaca7ba1c2d98c729f)

And here is a sample setup.py associated with this module:

- [Hackernews forum setup.py  example](https://gist.github.com/MathiasExorde/bc4a4670e4ba6a0fabbade76223b7eb8)

## **How to embed & test your scraper**

You should write a test_query() function that applies examples URL (or keyword) as input, to show the good behavior of your scraper.

```python
import asyncio

< your code ....>

async def test_query():
    keyword = "bitcoin"
    parameters = {'keyword':keyword,'max_oldness_seconds':180, ...}
    async for item in query(parameters):
        print("\n",item)
        assert(isinstance(item,Item))
# Run the async main function
asyncio.run(test_query())
```
A generate_scraper_url() method is usually useful to implement, to create the target URL your scraper is going to open, based on the input keyword. For example for Reddit, Twitter, LinkedIn, etc.


## **Technical Specifications**

It is crucial for developers to respect the technical guidelines provided for the implementation of the scraper:

1. **Python Version:** The code for the scraper should be written in `Python ≥ 3.10`. 
2. **Asynchronous Programming:** The code must leverage Python's **async** and **await** syntax to enable non-blocking code execution, allowing for efficient concurrent scraping of the web. In particular, the use of Async Generators allows for efficient processing of data, yielding one item at a time instead of storing all items in memory.
- **URL Validation:** The URL should be validated to contain certain domain-identifying substrings like "reddit", "reddit.com" (depending on the target website). An error should be raised if the URL doesn't meet these criteria.
- **Posts Filtering:** Posts should be filtered based on several criteria such as:
    - The post's age should not exceed a specified oldness threshold in seconds.
    - The post's length should be greater than a certain minimum length.
    - The total number of posts scraped should not exceed a specified maximum. The generator should stop when this number is reached.
- **Scraping Randomness if website not searchable:** When the target website isn’t searchable (for example on 4channel boards), and it requires a choice of “category” (board, thread, subreddit, etc), this choice has to be uniform (suggestion: use *random.choice()*)
1. **Web Request Handling:** The **aiohttp** package should be used for making and handling HTTP requests, enabling asynchronous request-response communication.
2. **Coding Standards:** The code must adhere to the best practices and standards of Python. For example, unused code must not be present in the submission, all functions and parameters must be properly named and documented, and the code should conform to PEP 8, the Python style guide.
3. **Error Handling:** The code must implement appropriate error handling to ensure that it functions correctly under different conditions and that it can fail gracefully when unexpected situations arise. The system should be able to recover from errors and continue operation where possible.
4. **Performance Considerations:** The code should be written to be as efficient as possible, taking into account factors such as memory usage, CPU utilization, and network usage. 
    1. When scraping & scrolling, if posts are ranked by post datetime, it is smart to cut the process if only old posts are found.
    2. Many optimizations such as this can be implemented to make scraping “intelligent”
5. **NO APIs**: the code is aimed at running on a decentralized network, the code should scrape the content/HTML pages itself, to be resilient and independent from central points of failures such as APIs.
6. **Credential usage**: each open-source bounty specifies clearly if the scraper has to be login-based (using credentials as input) or not. Respect this. There is a clear preference to not being logged in (if possible, of course). 

## Data Quality and Code Quality

1. The additional libraries should not require rework or refactoring of the existing client core.
2. (**REQUIRED**) The scraper should be able to **find &** **collect** at **least 100 data points (posts) per hour.** 
3. If automated browser usage is necessary, stick with Selenium+Chromium WebDriver. Switching to Playwright or other libraries is discouraged unless justified and in accordance with the scraper's design and independence principles.
4. **Code quality requirements & writing methodology:**
    - **The code has to be documented at a function level: each function must have a header, with parameters & return types + values detailed. (Classic docgen/docstring style)**
    - The code has to be expressed in English
    - Unused code must not be present in the submission. Commented code has to be properly justified to exist in the submission
    - Naming conventions should follow the Python standard: [https://peps.python.org/pep-0008/](https://peps.python.org/pep-0008/)
    - **Unit tests are not required but a test_query() combined with `asyncio.run(test_query()`) is required. (as explained above)**

A simple example of a Reddit scraper can be found here: [https://github.com/exorde-labs/exorde-client/blob/main/data/scraping/reddit/ap98j3envoubi3fco1kc/__init__.py](https://github.com/exorde-labs/exorde-client/blob/main/data/scraping/reddit/ap98j3envoubi3fco1kc/__init__.py)

## **How to submit your work**

1. **Create a dedicated folder for your scraper**: Name this folder the name of your scraper, for example, "scraper-name".
2. **Inside your scraper's folder, create another folder**: This folder should be named the 20-chars UUID identifying your scraper, for example, "**5de4869419ab11eebe56**". It must be precisely 20 chars long.
3. **Create an __init__.py  file**: Inside the "scraper-uuid" folder, create a Python file named **__init__.py**. This file should contain your scraper's code, including the **`scrape()`** and **`query()`** functions. The **`query()`** function should be located at the bottom of the file.
4. **Add a [setup.py](http://setup.py) file and README.md**: Place these two files directly under the main scraper's folder ("scraper-name"). The setup.py file should contain necessary setup instructions, while the README.md should provide high-level information about the functionality of your scraper, how to use it, and any other relevant details. setup.py should follow the standard, please click on the setup.py link to see an example.

**Here's the tree structure representing your scraper module's submission directory:**

```
scraper-name
├── scraper-identifier-uuid
│   └── __init__.py
├── [setup.py](https://github.com/exorde-labs/exorde-client/blob/main/data/scraping/reddit/setup.py)
└── README.md
```

**Once your scraper module adheres to this structure and guidelines, please submit your work to the appropriate repository: [The Exorde Data Repo](https://github.com/exorde-labs/exorde_data)**

**by performing a pull request (PR).**

# 💲Rewards - Claiming Bounty

🏆🏆🏆 A bounty of a certain EXD for the **first valid** submission of a Scraper module. The prize depend on the module importance & complexity (login-based or not), on a case-by-case basis.

**The first step is to make the first pull request on the exorde-client repository.** 

[https://github.com/exorde-labs/exorde-client/tree/main/data/scraping](https://github.com/exorde-labs/exorde_data)

1. A submission is considered **valid** if all constraints, requirements, and rules detailed above are respected. A valid submission should be testable by a team member within minutes if the **setup.py** and **init**.py files are properly written. Being first is based on the PR timestamp on the GitHub repository.
2. **Minor success:** If you are the first to submit your work on the exorde-client repository but minor changes are required, you can correct them quickly & win the prize. If major changes are required, the submission will be considered incomplete.
3. **Helper bounties**: Contributors who help fix issues on an incomplete submission will receive between 20 and 100 EXD. This will be limited to max 5 contributors per scraper module. Not on existing, integrated scrapers, new ones.
4. **Forking/Copying** the partially/incomplete contribution of another user and resubmitting it corrected will not count as a complete submission. If this corrected submission is valid, it will unlock a 20 to 100 EXD reward to the new submitter, and the main prize to the original contributor.

 **The technical specifications are detailed enough so ambiguity should not be present. If doubt persists, reach out on Discord to a core team member (NFTerraX or Mathias).**

Tip: use the checklist below to make sure you didn’t forget anything.

---

**Developers must follow these constraints and guidelines while writing a pluggable scraper. By joining us in this journey, you are contributing to Exorde's vision of a fully decentralized and high-quality data ecosystem.** 

**Let's shape the future of decentralized data collection, together!**


# 📑 "Is My Submission Valid" Checklist:

1. **Environment:**
    - Python 3.10  (UNIX container)
    - Make a PR (pull request) on https://github.com/exorde-labs/exorde-client
    Subdirectory [https://github.com/exorde-labs/exorde-client/tree/main/data/scraping](https://github.com/exorde-labs/exorde_data). Accepted file structure:
        
        ```python
        scraper-name
        ├── scraper-identifier-uuid
        │   └── __init__.py
        ├── [setup.py](https://github.com/exorde-labs/exorde-client/blob/main/data/scraping/reddit/setup.py)
        └── README.md
        ```
        
    - pip install exorde_data & have madtypes in the same directory
    - provide a standard Python module [setup.py](http://setup.py), following the standard Python practice.
2. **Language & Libraries:**
    - aiohttp for asynchronous HTTP requests
    - selenium (version 4.2.0) & chromium+chromedriver for browser automation, with required options (flags, headless, etc) & slow organic data scraping.
    - logging for event logging (INFO & DEBUG levels accepted)
3. **Asynchronous Programming:**
    - Use Python's async and await syntax for non-blocking code execution and concurrent scraping
    - Main query(..) interface: `async def query(parameters: dict) -> AsyncGenerator[Item, None]`
    - use as input the common_parameters: **`keyword`**,**`max_oldness_seconds`**, **`maximum_to_collect`**, and **`min_post_len`**
    1. Yield valid objects of **`Item`** class with attributes including **`content`**, **`author`**, **`created_at`**, **`title`**, **`domain`**, **`url`**, **`external_id`**, and **`external_parent_id`**
4. **Data Validation:**
    - Follow Exorde's strict JSON format & field data format (provide **real & unique “url”, “**created_at” must respect UTC+0 format, etc).. **Failure to do so will result in the entire code submission being invalid.**
5. **API usage:** No APIs are to be used, scrape the content of pages (HTML) directly.
6. **Credential usage:** Respect whether the scraper has to be login-based or not based on the specific bounty
7. **Avoid libraries that require refactoring of the existing client core (or generating a new docker image)**
8. **The scraper should be able to find & collect at least 100 unique data points (posts) per hour, on average**
9. **Code quality requirements:** Document the code at a function level, Write the code in English, and follow main Python PEP8 conventions.
10. **Implement a test_query() function with asyncio.run(test_query()) for testing**

## Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

- The use of sexualized language or imagery and unwelcome sexual attention or advances
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information, such as a physical or electronic address, without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

# License
All code in this repository is under the GNU General Public License v3.0.
You can find it here: [LICENSE](https://github.com/exorde-labs/exorde-client/blob/main/LICENSE)
# Attribution

This guide is written by Mathias Dail, CTO @Exorde Labs.
Website: https://exorde.network/
exorde-client repo: https://github.com/exorde-labs/exorde-client
Exorde Protocol (Testnet) repo: https://github.com/exorde-labs/TestnetProtocol
Documentation: https://docs.exorde.network/

Join our Discord, where the open source bounty & the Exorde community is discussing!

[https://discord.gg/DWfcz7ezSG](https://discord.gg/DWfcz7ezSG)


<img src="https://uploads-ssl.webflow.com/620398f412d5829aa28fbb86/6226257d5b5cb92ebbf91c26_landscape-logo-white.svg" width="400" height="400" class="center"/>
