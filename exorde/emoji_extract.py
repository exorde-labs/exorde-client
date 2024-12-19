# Emoji extraction

import emoji
from typing import Tuple, List

def extract_emojis(text: str) -> Tuple[str, List[str]]:
    # Extract all emojis from the text
    extracted_emojis = [char for char in text if char in emoji.EMOJI_DATA]

    # Create a cleaned version of the text without emojis
    cleaned_text = ''.join(char for char in text if char not in emoji.EMOJI_DATA)

    return cleaned_text, extracted_emojis

if __name__ == '__main__':
    # Example usage
    text = "I love programming 😍👨💻!"
    cleaned_text, emojis = extract_emojis(text)

    print("Cleaned text:", cleaned_text)  # Output: Cleaned text: I love programming !
    print("Extracted emojis:", emojis)    # Output: Extracted emojis: ['😍', '👨💻']

