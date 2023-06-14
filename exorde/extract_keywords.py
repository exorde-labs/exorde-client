import yake
import re
import string

from exorde.models import Keywords, Translation

def filter_strings(input_list):
    output_list = []
    for s in input_list:
        # Remove leading and trailing special characters
        s = re.sub('^[^A-Za-z0-9 ]+|[^A-Za-z0-9 ]+$', '', s)

        # Count the number of special characters in the string
        special_char_count = sum([1 for char in s if char in string.punctuation])

        # Check if there's any alphabetical character in the string
        contains_letter = any(char.isalpha() for char in s)

        # If the number of special characters is less than 30% of the total characters and the string contains at least one letter, add to output list
        if special_char_count / len(s) <= 0.3 and contains_letter:
            output_list.append(s)
    return output_list

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
    keywords_ = list(kx1)
    keywords_.extend(x for x in kx2 if x not in keywords_)
    keywords = filter_strings(keywords_)
    return Keywords([e[0] for e in set(keywords)])
