import logging
import time
import tiktoken

def evaluate_token_count(
    item_content_string: str, encoding_name: str = "r50k_base"
) -> int:
    """Returns the number of tokens in a text string."""
    try:
        if item_content_string is None or len(item_content_string) <= 1:
            logging.info(f"[evaluate_token_count] the content is empty")
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(item_content_string))
    except Exception as e:
        logging.info(f"[evaluate_token_count] error: {e}")
        num_tokens = 0
    return num_tokens
