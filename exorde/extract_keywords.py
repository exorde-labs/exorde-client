import yake
import re
import string
from keybert import KeyBERT
try:
    import nltk
    nltk.download()
except:
    print("nltk already downloaded or error")
from exorde.models import Keywords, Translation


def is_good_1gram(word):
    special_chars = set(string.punctuation.replace("-", ""))
    length = len(word)
    
    if length <= 3:
        return all(char == "-" or char not in special_chars for char in word)
    else:
        return all(char not in special_chars for char in word)


def filter_strings(input_list):
    output_list = []
    for s in input_list:
        if not isinstance(s, str):  # Check if s is a string
            continue  # Skip this iteration of the loop if s is not a string
        if not is_good_1gram(s):
            continue # skip if bad word, bad!
        # Count the number of special characters in the string
        special_char_count = sum([1 for char in s if (char in string.punctuation or char.isnumeric() or not char.isalpha())])

        # Remove leading and trailing special characters
        s = re.sub('^[^A-Za-z0-9 ]+|[^A-Za-z0-9 ]+$', '', s)
        s = re.sub(r'\\u[\da-fA-F]{4}', '', s)

        # Check if there's any alphabetical character in the string
        contains_letter = any(char.isalpha() for char in s)

        # If the number of special characters is less than 30% of the total characters and the string contains at least one letter, add to output list
        if len(s) > 0 and special_char_count * 100 / len(s) <= 20 and contains_letter:
            if s not in output_list:
                output_list.append(s)

    return output_list

### YAKE PARAMETERS

language = "en"
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
max_ngram_size_1 = 1 # 1-grams are enough for most use cases
numOfKeywords_1 = 20 # important to keep high enough

kw_extractor1 = yake.KeywordExtractor(
    lan=language,
    n=max_ngram_size_1,
    dedupLim=deduplication_thresold,
    dedupFunc=deduplication_algo,
    windowsSize=windowSize,
    top=numOfKeywords_1,
)

_extract_keywords1 = lambda text: kw_extractor1.extract_keywords(text)

_kw_bert_model = KeyBERT(model='all-MiniLM-L6-v2')
th_kw_bert = 0.175
_extract_keywords2 = lambda text: [keyword[0] for keyword in _kw_bert_model.extract_keywords(text) if keyword[1] > th_kw_bert]

def get_extra_special_keywords(text):
    def is_valid_keyword(word):
        uppercase_count = sum(1 for char in word if char.isupper())
        isalpha_count = sum(1 for char in word if char.isalpha())
        total_chars = len(word)
        punctuation = re.compile(r'[^\w\s,]')
        return (uppercase_count / total_chars >= 0.3) and (punctuation.search(word) is not None) and (isalpha_count>1)
    
    words = nltk.word_tokenize(text)
    filtered_words = filter(is_valid_keyword, words)
    return list(filtered_words)

def extract_keywords(translation: Translation) -> Keywords:
    content: str = translation.translation       
    kx1 = _extract_keywords1(content)
    keywords_weighted = list(set(kx1))
    keywords_ = [e[0] for e in set(keywords_weighted)]
    keywords_.extend(_extract_keywords2(content))
    keywords_ = filter_strings(keywords_)
    try:
        bonus_keywords = get_extra_special_keywords(content)
        keywords_.extend(bonus_keywords)
    except Exception as e:
        print(f"Error in get_extra_special_keywords: {e}")
    return Keywords(list(set(keywords_)))
