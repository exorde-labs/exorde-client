import os
import requests
import spacy
import torch
from transformers import pipeline
from argostranslate import translate as _translate


def lab_initialization():
    device = torch.cuda.current_device() if torch.cuda.is_available() else -1
    try:
        nlp = spacy.load("en_core_web_trf")
    except:
        os.system(
            "python -m spacy download en_core_web_trf"
        )  # Download the model if not present
        nlp = spacy.load("en_core_web_trf")
    installed_languages = _translate.get_installed_languages()
    return {
        "device": device,
        "nlp": nlp,
        "max_depth": 2,
        "remove_stopwords": False,
        "installed_languages": installed_languages,
        "max_token_count": 500,
    }
