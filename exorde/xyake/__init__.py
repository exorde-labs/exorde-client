import logging
import yake

language = "en"
max_ngram_size = 3
deduplication_thresold = 0.9
deduplication_algo = "seqm"
windowSize = 1
numOfKeywords = 20

kw_extractor = yake.KeywordExtractor(
    lan=language,
    n=max_ngram_size,
    dedupLim=deduplication_thresold,
    dedupFunc=deduplication_algo,
    windowsSize=windowSize,
    top=numOfKeywords,
)

extract_keywords = lambda text: kw_extractor.extract_keywords(text)


def populate_keywords(item):
    if item["item"]["Language"] in ["en", ""]:
        try:
            item["tokenOfInterests"] = list(
                set(extract_keywords(item["item"]["Content"]))
            )
        except:
            logging.error(f"Could not extract keywords for item {item}")
    return item
