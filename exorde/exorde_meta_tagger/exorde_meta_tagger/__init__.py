# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 09:12:00 2023

@author: flore
"""
from huggingface_hub import hf_hub_download
import json
import numpy as np
import os
import pandas as pd
import re
import requests
from sentence_transformers import SentenceTransformer
import spacy
import swifter
import tensorflow as tf
import torch
from transformers import AutoTokenizer, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import warnings
from typing import Callable


with warnings.catch_warnings():
    warnings.simplefilter("ignore")


class TransformerBlock(tf.keras.layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1, **__kwargs__):
        super().__init__()
        self.att = tf.keras.layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.ffn = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(ff_dim, activation="relu"),
                tf.keras.layers.Dense(embed_dim),
            ]
        )
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


class TokenAndPositionEmbedding(tf.keras.layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim, **__kwargs__):
        super().__init__()
        self.token_emb = tf.keras.layers.Embedding(
            input_dim=vocab_size, output_dim=embed_dim
        )
        self.pos_emb = tf.keras.layers.Embedding(
            input_dim=maxlen, output_dim=embed_dim
        )

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions


### FUNCTIONS DEFINITION


# This method below should be called before the freshness test.
# Requires no empty string // no None text
# Order:
#     - Spotting
#     - Zero-shot classification
#     - Freshness test (does the item has been posted less thant 5 minutes ago ?)
def zero_shot(texts, labeldict, classifier, max_depth=None, depth=3):
    """
    Perform zero-shot classification on the input text using a pre-trained language model.

    Args:
    - text (str): The input text to be classified.
    - labeldict (dict): A dictionary that maps each label to its corresponding sub-labels, or None if the label has no sub-labels.
    - path (list, optional): A list containing the path of labels from the root to the current label. Defaults to None.
    - depth (int, optional): The current depth in the label hierarchy. Defaults to 0.
    - max_depth (int, optional): The maximum depth in the label hierarchy to explore. Defaults to None (i.e., explore the entire hierarchy).

    Returns:
    - path (list): A list containing the path of labels from the root to the predicted label. If the label hierarchy was not explored fully and the max_depth parameter was set, the path may not be complete.
    """
    keys = list(labeldict.keys())
    output = classifier(texts, keys, multi_label=False, max_length=32)
    labels = [output[x]["labels"][0] for x in range(len(output))]
    depth += 1
    if depth == max_depth:
        _labels = labels
        return labels
    else:
        outputs = list()

        for _t, _lab in zip(texts, labels):
            # _labels = dict()
            # for lab in _lab:
            keys = list(labeldict[_lab].keys())
            output = classifier(texts, keys, multi_label=False, max_length=32)
            _out = list()
            for x in range(len(output)):
                out = list()
                for i in range(len(output[x]["labels"])):
                    scores = (output[x]["labels"][i], output[x]["scores"][i])
                    out.append(scores)
                _out.append(out)

            # _labs = [output[x]["labels"] for x in range(len(output))]
            # _scores = [output[x]["scores"] for x in range(len(output))]

            outputs.append(_out)
    return outputs


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
    text = preprocess(text)
    text = text.lower().strip()

    if contains_only_special_chars(text):
        text = ""
    return text


def preprocess(item, remove_stopwords):
    item["item"]["Content"] = preprocess_text(
        item["item"]["Content"], remove_stopwords
    )
    return item


def get_entities(text, nlp):
    doc = nlp(text)
    return [(x.text, x.label_) for x in doc.ents]


def predict(text, pipe, tag, mappings):
    preds = pipe.predict(text, verbose=0)[0]
    result = []
    for i in range(len(preds)):
        result.append((mappings[tag][i], preds[i]))
    return result


##########################################################
def tag(documents, nlp, device, mappings):
    """
    Analyzes and tags a list of text documents using various NLP models and techniques.

    The function processes the input documents using pre-trained models for tasks such as
    sentence embeddings, text classification, sentiment analysis, and custom models for age,
    gender, and hate speech detection. It returns a list of dictionaries containing the
    processed data for each input document.

    Args:
        documents (list): A list of text documents (strings) to be analyzed and tagged.
        nlp: model
        device: device
        mappings: labels

    Returns:
        list: A list of dictionaries, where each dictionary represents a single input text and
              contains various processed data like embeddings, text classifications, sentiment, etc.,
              as key-value pairs.
    """
    # Create an empty DataFrame
    tmp = pd.DataFrame()

    # Add the original text documents
    tmp["Translation"] = documents

    # Compute sentence embeddings
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    tmp["Embedding"] = tmp["Translation"].swifter.apply(
        lambda x: model.encode(x)
    )

    # Text classification pipelines
    text_classification_models = [
        ("Advertising", "djsull/kobigbird-spam-multi-label"),
        ("Emotion", "SamLowe/roberta-base-go_emotions"),
        ("Irony", "cardiffnlp/twitter-roberta-base-irony"),
        ("LanguageScore", "salesken/query_wellformedness_score"),
        ("TextType", "marieke93/MiniLM-evidence-types"),
        ("SourceType", "alimazhar-110/website_classification"),
    ]
    for col_name, model_name in text_classification_models:
        pipe = pipeline(
            "text-classification", model=model_name, top_k=None, device=device
        )
        tmp[col_name] = tmp["Translation"].swifter.apply(
            lambda x: [(y["label"], y["score"]) for y in pipe(x)[0]]
        )
        del pipe  # free ram for latest pipe

    # Tokenization for custom models
    tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased")
    tmp["Embedded"] = tmp["Translation"].swifter.apply(
        lambda x: np.array(
            tokenizer.encode_plus(
                x,
                add_special_tokens=True,
                max_length=512,
                truncation=True,
                pad_to_max_length=True,
                return_attention_mask=False,
                return_tensors="tf",
            )["input_ids"][0]
        ).reshape(1, -1)
    )

    # Sentiment analysis using VADER
    emoji_lexicon = hf_hub_download(
        repo_id="ExordeLabs/SentimentDetection",
        filename="emoji_unic_lexicon.json",
    )
    loughran_dict = hf_hub_download(
        repo_id="ExordeLabs/SentimentDetection", filename="loughran_dict.json"
    )
    with open(emoji_lexicon) as f:
        unic_emoji_dict = json.load(f)
    with open(loughran_dict) as f:
        Loughran_dict = json.load(f)
    sentiment_analyzer = SentimentIntensityAnalyzer()
    sentiment_analyzer.lexicon.update(Loughran_dict)
    sentiment_analyzer.lexicon.update(unic_emoji_dict)
    tmp["Sentiment"] = tmp["Translation"].swifter.apply(
        lambda x: sentiment_analyzer.polarity_scores(x)["compound"]
    )

    # Custom model pipelines
    custom_model_data = [
        ("Age", "ExordeLabs/AgeDetection", "ageDetection.h5"),
        ("Gender", "ExordeLabs/GenderDetection", "genderDetection.h5"),
        (
            "HateSpeech",
            "ExordeLabs/HateSpeechDetection",
            "hateSpeechDetection.h5",
        ),
    ]

    for col_name, repo_id, file_name in custom_model_data:
        model_file = hf_hub_download(repo_id=repo_id, filename=file_name)
        custom_model = tf.keras.models.load_model(
            model_file,
            custom_objects={
                "TokenAndPositionEmbedding": TokenAndPositionEmbedding,
                "TransformerBlock": TransformerBlock,
            },
        )
        tmp[col_name] = tmp["Embedded"].swifter.apply(
            lambda x: predict(x, custom_model, col_name, mappings)
        )
        del custom_model  # free ram for latest custom_model

    # The output is a list of dictionaries, where each dictionary represents a single input text and contains
    # various processed data like embeddings, text classifications, sentiment, etc., as key-value pairs.
    return tmp.to_json() #tmp.to_dict(orient="records") #if needed in records pandas dict format for analysis


### VARIABLE INSTANTIATION
def meta_tagger_initialization():
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
        "https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/cateogry_tree.json"
    ).json()
    mappings = {
        "Gender": {0: "Female", 1: "Male"},
        "Age": {0: "<20", 1: "20<30", 2: "30<40", 3: ">=40"},
        "HateSpeech": {0: "Hate speech", 1: "Offensive", 2: "None"},
    }
    try:
        nlp = spacy.load("en_core_web_trf")
    except:
        os.system(
            "python -m spacy download en_core_web_trf"
        )  # Download the model if not present
        nlp = spacy.load("en_core_web_trf")
    return {
        "device": device,
        "classifier": classifier,
        "labeldict": labels,
        "mappings": mappings,
        "nlp": nlp,
        "max_depth": 2,
        "remove_stopwords": False,
    }


if __name__ == "__main__":
    init = meta_tagger_initialization()

    ### TEST ZONE

    test = test[:1]
    print("Nb of text samples = ", len(test))
    tags = tag(test, init["nlp"], init["device"], init["mappings"])
    field = zero_shot(test, init["labeldict"], init["classifier"], max_depth=1)
    
#     # doesn't work if in json string format
#     for sample, lbl, tag_ in zip(test, field, tags):
#         print("Input = ", sample)
#         top_gender = max(tag_["Gender"], key=lambda x: x[1])[0]
#         top_age = max(tag_["Age"], key=lambda x: x[1])[0]
#         hatespeech_max = max(tag_["HateSpeech"], key=lambda x: x[1])
#         advertising = max(tag_["Advertising"], key=lambda x: x[1])
#         top_emotion = max(tag_["Emotion"], key=lambda x: x[1])
#         top_irony = max(tag_["Irony"], key=lambda x: x[1])
#         textType = max(tag_["TextType"], key=lambda x: x[1])
#         sourceType = max(tag_["SourceType"], key=lambda x: x[1])

#         sentiment = tag_["Sentiment"]
#         languageScore = tag_["LanguageScore"]

#         print(f"\tTopic category:  **{lbl}**")
#         print(f"\tTop Gender: {top_gender}")
#         print(f"\tTop Age Range: {top_age}")
#         print(f"\tSentiment: {sentiment}")
#         print(f"\tHateSpeech: {hatespeech_max}")
#         print(f"\tAdvertising: {advertising}")
#         print(f"\tTop emotion: {top_emotion}")
#         print(f"\tIrony: {top_irony}")
#         print(f"\tText type: {textType}")
#         print(f"\tLanguage Score: {languageScore}")
#         print(f"\tSource type: {sourceType}")
#         print()

    dump_to_json_file(tags, "tags.json")
    dump_to_json_file(field, "field.json")
