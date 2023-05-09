# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 09:12:00 2023

@author: flore
"""
from aiosow.bindings import setup
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
from aiosow.bindings import autofill, make_async


with warnings.catch_warnings():
    warnings.simplefilter("ignore")


### REQUIRED CLASSES (j'ai enlevé autant de classes que possible mais celles-ci sont nécessaires x)


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
        self.pos_emb = tf.keras.layers.Embedding(input_dim=maxlen, output_dim=embed_dim)

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions


def adapter(resolve: Callable) -> Callable:
    def wrapper(function: Callable) -> Callable:
        async def caller(item, **kwargs):
            value = await autofill(resolve, args=[item], **kwargs)
            result = await autofill(function, args=[value], **kwargs)
            return result

        return caller

    return wrapper


### FUNCTIONS DEFINITION


# This method below should be called before the freshness test.
# Requires no empty string // no None text
# Order:
#     - Spotting
#     - Zero-shot classification
#     - Freshness test (does the item has been posted less thant 5 minutes ago ?)
def zero_shot(texts, labeldict, classifier, max_depth=None, depth=0):
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
    item["item"]["Content"] = preprocess_text(item["item"]["Content"], remove_stopwords)
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
    tmp["Embedding"] = tmp["Translation"].swifter.apply(lambda x: model.encode(x))

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
        repo_id="ExordeLabs/SentimentDetection", filename="emoji_unic_lexicon.json"
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
        ("HateSpeech", "ExordeLabs/HateSpeechDetection", "hateSpeechDetection.h5"),
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
    return tmp.to_dict(orient="records")


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
    test = [
        "Bitcoin hit 30.000$ last night!",
        "I like having a mojito with my breakfast",
        "Apple Inc. reports a 5% increase in revenue this quarter",
        "Get the best deal on laptops! Save up to 50% on our online store!",
        "U.S. Federal Reserve announces a 0.25% increase in interest rates",
        "Introducing our new line of skincare products - rejuvenate your skin!",
        "Microsoft acquires another startup, expanding its cloud services",
        "Try our 30-day free trial of premium membership, and enjoy unlimited access!",
        "Oil prices continue to surge amid geopolitical tensions",
        "Eager to travel again? Book your dream vacation now with our special discounts!"
        "Bitcoin hits new record high of $70,000",
        "Amazon reports record-breaking sales during Black Friday and Cyber Monday",
        "New exhibition of Van Gogh's paintings opens at the Louvre",
        "Tesla stocks reach all-time high as demand for electric cars surges",
        "World Cup 2022 tickets go on sale, with prices starting from $100",
        "Gold prices hit a 6-month high amid rising inflation concerns",
        "Facebook faces antitrust lawsuits from the US government and multiple states",
        "Olympic Games 2024 to be held in Paris, France",
        "Federal Reserve hints at potential interest rate hike in the coming months",
        "McDonald's introduces new plant-based burger to its menu",
        "Elon Musk surpasses Jeff Bezos to become the world's richest person",
        "New York Stock Exchange suspends trading due to technical glitch",
        "Walt Disney Company reports strong earnings for Q3",
        "Rafael Nadal wins his 21st Grand Slam title at the Australian Open",
        "China's economy grows by 8% in 2022, despite global pandemic",
        "Starbucks pledges to become more eco-friendly by phasing out single-use cups",
        "NFL announces new playoff format, with 14 teams qualifying",
        "UK economy shrinks by 1.5% in Q4, amid Brexit uncertainty",
        "Nike releases new line of sustainable sneakers, made from recycled materials",
        "Greta Thunberg named Time's Person of the Year for 2022",
        "FIFA World Cup 2026 to be jointly hosted by USA, Canada, and Mexico",
        "Apple unveils its new iPhone 15, with advanced AI features",
        "Facebook changes its name to Meta, focuses on virtual reality and the metaverse",
        "Novak Djokovic wins a record-breaking 10th Australian Open title",
        "Delta Airlines announces new routes and expanded services for 2023",
        "Google faces antitrust investigation from the European Union",
        "Real Madrid wins the UEFA Champions League for the 15th time",
        "US unemployment rate drops to 3.8%, lowest in 50 years",
        "Sony releases highly anticipated PS6 console, with 8K graphics",
        "McKinsey & Company accused of advising opioid makers on how to 'turbocharge' sales",
        "Tokyo Olympics officially begin, after being postponed due to COVID-19",
        "Uber and Lyft announce plans to go public in 2023",
        "Artificial intelligence surpasses human performance in complex games like Go and chess",
        "UK announces plans to ban petrol and diesel cars by 2030",
        "Netflix shares drop by 10% after Q4 earnings report misses expectations",
        "NASA launches new Mars rover, with hopes of finding signs of ancient life",
        "Jeff Bezos steps down as CEO of Amazon, to focus on space venture Blue Origin",
        "Floyd Mayweather Jr. announces his retirement from boxing",
        "Bitcoin crashes by 30% in a single day, wiping out billions in value",
        "Ford unveils its new electric F-150 Lightning pickup truck",
        "Twitter bans former US president Donald Trump, citing incitement to violence",
        "Serena Williams wins her 24th Grand Slam title at Wimbledon",
        "Microsoft announces major expansion of its data center network",
        "US government announces new infrastructure bill, with $1 trillion in spending",
        "LeBron James signs historic $200 million contract with the Los Angeles Lakers",
        "Wow, I'm so glad Bitcoin hit 30k, I was just about to use it to buy groceries.",
        "Having a mojito with breakfast? Yeah, that's definitely a great way to start your day on the right foot... or stumble.",
        "Apple's 5% increase in revenue is really going to help all those struggling millionaires out there.",
        "50% off laptops? Because who needs to pay full price for a device that will become obsolete in a year?",
        "Yay, the Federal Reserve is raising interest rates! Just what everyone needs, more debt to pay off.",
        "Oh good, because what we all need is more skincare products to clutter our bathroom shelves.",
        "Another startup for Microsoft to swallow up? How exciting, I can hardly wait for the monopolization of the entire tech industry.",
        "Unlimited access to what, exactly? More ads and spam?",
        "Oil prices are surging? Time to invest in bicycles and public transportation, folks.",
        "Special discounts on travel? Just what we all need during a global pandemic!",
        "70k for a Bitcoin? Oh boy, I can't wait to sell my kidneys for some digital currency.",
        "Record-breaking sales during Black Friday and Cyber Monday? Because nothing screams holiday spirit like capitalist excess and greed.",
        "A new exhibition of Van Gogh's paintings at the Louvre? Perfect, let's all go take selfies with them and completely miss the point of his art.",
        "Tesla stocks at an all-time high? I'm sure this is exactly what our planet needs right now.",
        "World Cup 2022 tickets starting at $100? Because nothing says fair competition like pricing out fans from lower income brackets.",
        "Gold prices hitting a 6-month high? I can't wait to trade in all my possessions for a shiny rock.",
        "Facebook facing antitrust lawsuits? Finally, some justice for all those years of invasive data mining and privacy violations.",
        "Oh good, another ad for skincare products. Because what we all need is more pressure to live up to unrealistic beauty standards.",
        "50% off laptops? Because who doesn't love buying outdated technology at a discount?",
        "Yay, more debt to pay off thanks to the Federal Reserve's interest rate increase. I can hardly contain my excitement.",
        "Get ready for the future of finance with our revolutionary new cryptocurrency, available now at an exclusive discount!",
        "Invest in our token today and watch your profits soar to the moon! Don't miss out on this once-in-a-lifetime opportunity.",
        "Our new blockchain-based platform is changing the game for businesses everywhere. Join the revolution now and reap the rewards!",
        "Want to make a quick buck? Our exclusive ICO is the perfect opportunity to get in on the ground floor of the next big thing.",
        "Looking for a new investment opportunity? Our cutting-edge technology and experienced team make us the perfect choice for your portfolio.",
    ]

    test = test[:10]
    print("Nb of text samples = ", len(test))
    tags = tag(test, init["nlp"], init["device"], init["mappings"])
    field = zero_shot(test, init["labeldict"], init["classifier"], max_depth=1)

    for sample, lbl, tag_ in zip(test, field, tags):
        print("Input = ", sample)
        top_gender = max(tag_["Gender"], key=lambda x: x[1])[0]
        top_age = max(tag_["Age"], key=lambda x: x[1])[0]
        hatespeech_max = max(tag_["HateSpeech"], key=lambda x: x[1])
        advertising = max(tag_["Advertising"], key=lambda x: x[1])
        top_emotion = max(tag_["Emotion"], key=lambda x: x[1])
        top_irony = max(tag_["Irony"], key=lambda x: x[1])
        textType = max(tag_["TextType"], key=lambda x: x[1])
        sourceType = max(tag_["SourceType"], key=lambda x: x[1])

        sentiment = tag_["Sentiment"]
        languageScore = tag_["LanguageScore"]

        print(f"\tTopic category:  **{lbl}**")
        print(f"\tTop Gender: {top_gender}")
        print(f"\tTop Age Range: {top_age}")
        print(f"\tSentiment: {sentiment}")
        print(f"\tHateSpeech: {hatespeech_max}")
        print(f"\tAdvertising: {advertising}")
        print(f"\tTop emotion: {top_emotion}")
        print(f"\tIrony: {top_irony}")
        print(f"\tText type: {textType}")
        print(f"\tLanguage Score: {languageScore}")
        print(f"\tSource type: {sourceType}")
        print()
