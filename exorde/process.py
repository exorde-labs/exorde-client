import json, logging


from exorde.preprocess import preprocess
from exorde.translate import translate
from exorde.extract_keywords import extract_keywords
from exorde.zero_shot import zero_shot
from exorde.models import Classification, Translation, Keywords, Processed, Item


async def process(item: Item, lab_configuration) -> Processed:
    try:
        try:
            item = preprocess(item, False)
        except Exception as err:
            logging.error("An error occured pre-processing an item")
            logging.error(err)
            logging.error(json.dumps(item, indent=4))
            raise err

        try:
            translation: Translation = translate(
                item, lab_configuration["installed_languages"]
            )
            if translation.translation == "":
                raise ValueError("No content to work with")
        except Exception as err:
            logging.error("An error occured translating an item")
            logging.error(err)
            logging.error(json.dumps(item, indent=4))
            raise err

        try:
            top_keywords: Keywords = extract_keywords(translation)
        except Exception as err:
            logging.error("An error occured populating keywords for an item")
            logging.error(err)
            logging.error(json.dumps(translation, indent=4))
            raise err

        try:
            classification: Classification = zero_shot(
                translation, lab_configuration
            )
        except Exception as err:
            logging.error("An error occured classifying an item")
            logging.error(err)
            logging.error(json.dumps(translation, indent=4))
            raise err
        return Processed(
            item=item,
            translation=translation,
            top_keywords=top_keywords,
            classification=classification,
        )
    except Exception as err:
        raise (err)
