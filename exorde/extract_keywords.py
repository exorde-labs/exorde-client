import yake

from exorde.models import Keywords, Translation

language = "en"
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
max_ngram_size_1 = 1
max_ngram_size_2 = 2
numOfKeywords_1 = 5
numOfKeywords_2 = 3

kw_extractor1 = yake.KeywordExtractor(
    lan=language,
    n=max_ngram_size_1,
    dedupLim=deduplication_thresold,
    dedupFunc=deduplication_algo,
    windowsSize=windowSize,
    top=numOfKeywords_1,
)

kw_extractor2 = yake.KeywordExtractor(
    lan=language,
    n=max_ngram_size_2,
    dedupLim=deduplication_thresold,
    dedupFunc=deduplication_algo,
    windowsSize=windowSize,
    top=numOfKeywords_2,
)

_extract_keywords1 = lambda text: kw_extractor1.extract_keywords(text)
_extract_keywords2 = lambda text: kw_extractor2.extract_keywords(text)

def extract_keywords(translation: Translation) -> Keywords:
    content: str = translation.translation        
    kx1 = _extract_keywords1(content)
    kx2 = _extract_keywords2(content)
    kx = list(kx1)
    kx.extend(x for x in kx2 if x not in kx)
    return Keywords([e[0] for e in set(kx)])
