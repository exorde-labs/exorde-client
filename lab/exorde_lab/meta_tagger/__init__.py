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
from exorde_data import Item


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
def zero_shot(item, labeldict, classifier, max_depth=None, depth=0):
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
    text_ = item.content
    texts = [text_]
    keys = list(labeldict.keys())
    output = classifier(texts, keys, multi_label=False, max_length=32)

    labels_list = list()

    for i in range(len(texts)):
        labels = [
            output[i]["labels"][x]
            for x in range(len(output[i]["labels"]))
            if output[i]["scores"][x] > 0.1
        ]
        labels_list.append(labels)

    depth += 1
    if depth == max_depth:
        _labels = labels
        return labels
    else:
        output_list = list()

        for _t, item_ in zip(texts, labels_list):
            outputs = dict()

            for _lab in item_:
                # _labels = dict()
                # for lab in _lab:
                keys = list(labeldict[_lab].keys())
                output = classifier(
                    texts, keys, multi_label=False, max_length=32
                )
                _out = dict()
                for x in range(len(output)):
                    for i in range(len(output[x]["labels"])):
                        if output[x]["scores"][i] > 0.1:
                            _out[output[x]["labels"][i]] = output[x]["scores"][
                                i
                            ]
                # _labs = [output[x]["labels"] for x in range(len(output))]
                # _scores = [output[x]["scores"] for x in range(len(output))]

                outputs[_lab] = _out
            output_list.append(outputs)
    # fill the classification field with the output
    item.classification = output_list
    return item


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
    item.content = preprocess_text(item.content, remove_stopwords)
    item.content = item.content.replace(
        "\n", ""
    )  # review-me: added by 6r17 to fix `predict porcess one line at a time (remove '\n') ; remove comment if OK
    return item


def get_entities(text, nlp):
    doc = nlp(text)
    return [(x.text, x.label_) for x in doc.ents]


def predict(text, pipe, tag, mappings):
    preds = pipe.predict(text, verbose=0)[0]
    result = []
    for i in range(len(preds)):
        result.append((mappings[tag][i], float(preds[i])))
    return result


##########################################################
def tag(items, nlp, device, mappings):
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
    # get text content attribute from all items
    documents = [item.content for item in items]

    # Create an empty DataFrame
    tmp = pd.DataFrame()

    # Add the original text documents
    tmp["Translation"] = documents

    # Compute sentence embeddings
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    tmp["Embedding"] = tmp["Translation"].swifter.apply(
        lambda x: list(model.encode(x).astype(float))
    )

    # Text classification pipelines
    text_classification_models = [
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
            lambda x: [(y["label"], float(y["score"])) for y in pipe(x)[0]]
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
        lambda x: float(sentiment_analyzer.polarity_scores(x)["compound"])
    )

    # Custom model pipelines
    custom_model_data = [
        ("Age", "ExordeLabs/AgeDetection", "ageDetection.h5"),
        ("Gender", "ExordeLabs/GenderDetection", "genderDetection.h5"),
        # (
        #     "HateSpeech",
        #     "ExordeLabs/HateSpeechDetection",
        #     "hateSpeechDetection.h5",
        # ),
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

    del tmp["Embedded"]
    # The output is a list of dictionaries, where each dictionary represents a single input text and contains
    # various processed data like embeddings, text classifications, sentiment, etc., as key-value pairs.
    # Update the items with processed data
    tmp = tmp.to_dict(orient="records")
    for i, item in enumerate(items):
        for _k in item.keys():
            if(_k in ["Translation", "Embedding", "Sentiment"]):
                setattr(item, _k.lower(), tmp[i][_k])
            elif(_k == "LanguageScore"):
                item.languages_score = tmp[i][_k]
            elif(_k == "Age"):
                for j in range(len(tmp[i][_k])):
                    if(tmp[i][_k][j][0] == "<20"):
                        item.age.below_twenty = tmp[i][_k][j][1]
                    elif(tmp[i][_k][j][0] == "20<30"):
                        item.age.twenty_thirthy = tmp[i][_k][j][1]
                    elif(tmp[i][_k][j][0] == "30<40"):
                        item.age.thirty_forty = tmp[i][_k][j][1]
                    else:
                        item.age.forty_more = tmp[i][_k][j][1]
            else:
                for k in range(len(tmp[i][_k])):
                    if(hasattr(item, k):
                       setattr(item._k, _k.lower(), tmp[i][_k][k][1]
                       
        #item.translation = tmp[i]["Translation"]
        #item.embedding = tmp[i]["Embedding"]
        #item.sentiment = tmp[i]["Sentiment"]
        #item.emotion = tmp[i]["Emotion"]
        #item.age.below_twenty = tmp[i]["Age"][0][1]
        #item.age.twenty_thirthy = tmp[i]["Age"][1][1]
        #item.age.thirty_forty = tmp[i]["Age"][2][1]
        #item.age.forty_more = tmp[i]["Age"][3][1]
        #item.gender.female = tmp[i]["Gender"][0][1]
        #item.gender.male = tmp[i]["Gender"][1][1]
        #item.irony.irony = tmp[i]["Irony"][0][1]
        #item.irony.non_irony = tmp[i]["Irony"][1][1]
        #item.language_score = tmp[i]["LanguageScore"]  # ??
        #item.text_type = tmp[i]["TextType"]
        #item.source_type = tmp[i]["SourceType"]

    return items


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
        # "HateSpeech": {0: "Hate speech", 1: "Offensive", 2: "None"},
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
