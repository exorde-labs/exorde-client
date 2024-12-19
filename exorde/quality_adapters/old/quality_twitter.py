import asyncio
from pyppeteer import launch
import json

BATCH_SIZE = 10
PAGE_RESOLVE_TIME_MS = 1400

def preprocess_content(text):
    # remove \n into spaces
    text = text.replace("\n", " ")
    return text

async def extract_text(page, result_mapping):
    try:
        # Extract text from the tweetText div if available
        tweet_text = await page.waitForSelector('div[data-testid="tweetText"]', timeout=PAGE_RESOLVE_TIME_MS)
        text_content = await page.evaluate('(element) => element.textContent', tweet_text)
        result_mapping[page.url] = text_content
    except Exception:
        # If tweetText div is not found, store an empty string in the result_mapping
        print(f'{page.url}: Error finding tweet content, must be deleted or not real')
        result_mapping[page.url] = ""

async def open_tabs(urls):
    result_mapping = {}
    total_urls = len(urls)
    # split the urls into batches of BATCH_SIZE
    batches = [urls[i:i + BATCH_SIZE] for i in range(0, total_urls, BATCH_SIZE)]
    # browser = await launch()
    browser = await launch(
        {
            'headless': True, 'args': ['--no-sandbox', '--disable-gpu'], 'ignoreHTTPSErrors': True
        },
        userAgent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    )

    for batch_index, batch in enumerate(batches, start=1):

        try:
            print(f"[Twitter Adapter] Processing Tweets URLs Batch {batch_index}/{len(batches)}")
            pages = await asyncio.gather(*[browser.newPage() for _ in batch])
        except Exception as e:
            print(f"[Twitter Adapter] Error creating new pages: {e}")
            continue

        for i, page in enumerate(pages):
            try:
                await page.goto(batch[i])
                await extract_text(page, result_mapping)
            except Exception as e:
                print(f"[Twitter Adapter] Error opening page: {e}")
                continue
            try:
                await browser.close()
                browser = await launch()
            except Exception as e:
                print(f"[Twitter Adapter] Error closing browser: {e}")
                continue
        
        await browser.close()

        return result_mapping

def extract_tweets_content_from_URLs(urls):
    result_mapping = asyncio.get_event_loop().run_until_complete(open_tabs(urls))
    return result_mapping

############################################################
####################################################################################################################################################################################
####################################################################################################################################################################################
############################################################

# MAIN BLOCK
if __name__ == '__main__':
        
    urls = [
        "http://twitter.com/nyutralkart/status/1701525624840704412",
        "https://twitter.com/IGInternational/status/1701525620549706160",
        "https://twitter.com/Tanlea_mk99/status/1701525616263073794",
        "https://twitter.com/TradersgurukulC/status/1701525611209277880",
        "https://twitter.com/RTTNews/status/1701525609166622864"
        "https://twitter.com/PenkeTrading/status/1701525604074455464",
        "https://twitter.com/lrobertsonTewks/status/1701525603218813249",
        "https://twitter.com/Mexc_Volume/status/1701525601411080416",
        "https://twitter.com/followin_io/status/1701525717916541030",
        "https://twitter.com/proforlax/status/1701525713910649142",
        "https://twitter.com/TAYYABANJUM13/status/1701525659997139227",
        "https://twitter.com/TradingMisa/status/1701525652334334184",
        "https://twitter.com/offixialfd_/status/1701525646776680948",
        "https://twitter.com/Chirp_Crypto/status/1701525475687113210"
    ]

   
    # measure time
    import time
    start_time = time.time()
    # Run the event loop to open tabs in batches
    result_mapping = extract_tweets_content_from_URLs(urls)

    end_time = time.time()

    # Print the URL -> Text Content mapping
    for i, (url, text_content) in enumerate(result_mapping.items()):
        print(f'[{i}] {url}: "{preprocess_content(text_content)}"')

    # print how many tweets were extracted vs how many were requested
    non_empty_tweets = 0
    for text_content in result_mapping.values():
        if text_content != "":
            non_empty_tweets += 1
    print(f"\nExtracted {non_empty_tweets} tweets out of {len(result_mapping)} requested.")
    print(f"\nTook {end_time - start_time} seconds to open {len(urls)} tabs in batches of {BATCH_SIZE}.")
