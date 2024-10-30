import re
from exorde_data import Content


def preprocess_text(text: str, remove_stopwords: bool) -> str:
    """This utility function sanitizes a string by:
    - removing links
    - removing special characters
    - removing numbers
    - removing stopwords
    - transforming in lowercase
    - removing excessive whitespaces
    Args:
        text (str): the input text you want to clean
        remove_stopwords (bool): whether or not to remove stopwords
    Returns:
        str: the cleaned text
    """

    def remove_unicode_escapes(s):
        return re.sub(r"\\u[\da-fA-F]{4}", "", s)

    def contains_only_special_chars(s):
        pattern = r"^[^\w\s]+$"
        return bool(re.match(pattern, s))

    def preprocess(text):
        new_text = [
            wrd
            for wrd in text.split(" ")
            if wrd.startswith("@") == False and wrd.startswith("http") == False
        ]
        return " ".join(new_text)

    text = text.replace("#", "")
    texst = remove_unicode_escapes(text)
    text = preprocess(text)
    text = text.strip()

    if contains_only_special_chars(text):
        text = ""
    return text


def preprocess(item, remove_stopwords):
    item.content = Content(preprocess_text(item.content, remove_stopwords))
    item.content = Content(item.content.replace("\n", " "))
    return item
