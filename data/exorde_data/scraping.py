import logging

try:
    import ap98j3envoubi3fco1kc as reddit
except:
    logging.exception("An error occured loading reddit")

try:
    import a7df32de3a60dfdb7a0b as twitter
except:
    logging.exception("An error occured loading twitter")

try:
    import ch4875eda56be56000ac as boards
except:
    logging.exception("An error loading 4chat")

__all__ = ["reddit", "twitter", "boards"]
