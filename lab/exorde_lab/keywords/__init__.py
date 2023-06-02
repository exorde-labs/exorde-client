import yake

from exorde_data.models import Item
from .models import TopKeywords

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


def populate_keywords(item: Item) -> TopKeywords:
    content: str = item.translation.translation
    return TopKeywords(
        top_keywords=[e[0] for e in set(extract_keywords(content))]
    )
