import logging
import yake

language = "en"
max_ngram_size_1 = 1
max_ngram_size_2 = 2
deduplication_thresold = 0.9
deduplication_algo = "seqm"
windowSize = 1
numOfKeywords_1 = 8
numOfKeywords_2 = 5

kw_extractor_1 = yake.KeywordExtractor(
    lan=language,
    n=max_ngram_size_1,
    dedupLim=deduplication_thresold,
    dedupFunc=deduplication_algo,
    windowsSize=windowSize,
    top=numOfKeywords_1,
)

kw_extractor_2 = yake.KeywordExtractor(
    lan=language,
    n=max_ngram_size_2,
    dedupLim=deduplication_thresold,
    dedupFunc=deduplication_algo,
    windowsSize=windowSize,
    top=numOfKeywords_2,
)

# 2 YAKE keywords: a) max 8 keywords with 1-gram b) max 5 keywords with 2-grams
extract_keywords_1 = lambda text: kw_extractor_1.extract_keywords(text)
extract_keywords_2 = lambda text: kw_extractor_2.extract_keywords(text)

def populate_keywords(item):
    if item["item"]["Language"] in ["en", ""]:
        try:
            # extract 2 sets of YAKE keywords: a) max 8 keywords with 1-gram b) max 5 keywords with 2-grams
            keywords_set_1 = extract_keywords_1(item["item"]["Content"])
            keywords_set_2 = extract_keywords_2(item["item"]["Content"])
            yake_keywords = list(keywords_set_1)
            # combine both list without potential duplicates
            yake_keywords.extend(x for x in keywords_set_2 if x not in yake_keywords)       
            # set tokenOfInterests to this list
            item["tokenOfInterests"] = set(yake_keywords)
        except:
            logging.error(f"Could not extract keywords for item {item}")
    return item
