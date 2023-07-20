import os
import requests
import spacy
import torch
from transformers import pipeline
from argostranslate import translate as _translate


def lab_initialization():
    device = torch.cuda.current_device() if torch.cuda.is_available() else -1
    classifier = pipeline(
        "zero-shot-classification",
        model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
        device=device,
        batch_size=16,
        top_k=None,
        max_length=64,
    )
    labels = requests.get(
        "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/class_names.json"
    ).json()
    mappings = {
        "Gender": {0: "Female", 1: "Male"},
        "Age": {0: "<20", 1: "20<30", 2: "30<40", 3: ">=40"},
        # "HateSpeech": {0: "Hate speech", 1: "Offensive", 2: "None"},
    }
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
        "classifier": classifier,
        "labeldict": labels,
        "mappings": mappings,
        "nlp": nlp,
        "max_depth": 2,
        "remove_stopwords": False,
        "installed_languages": installed_languages,
        "max_token_count": 500,
    }
