import json
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline
from huggingface_hub import hf_hub_download
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import tensorflow as tf
import swifter
from .models import (
    LanguageScore,
    Sentiment,
    Embedding,
    SourceType,
    TextType,
    Emotion,
    Irony,
    Age,
    Gender,
    Analysis,
)


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


def tag(texts, nlp, device, mappings):
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

    def predict(text, pipe, tag, mappings):
        preds = pipe.predict(text, verbose=0)[0]
        result = []
        for i in range(len(preds)):
            result.append((mappings[tag][i], float(preds[i])))
        return result

    # get text content attribute from all items
    documents = [item.content for item in texts]
    print(documents)
    for doc in documents:
        assert isinstance(doc, str)

    # Create an empty DataFrame
    tmp = pd.DataFrame()

    # Add the original text documents
    tmp["Translation"] = documents

    assert tmp["Translation"] is not None
    assert len(tmp["Translation"]) > 0
    print(tmp["Translation"])

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
            "text-classification",
            model=model_name,
            top_k=None,
            device=device,
            max_length=512,
            padding=True,
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

    _out = []
    for i in range(len(tmp)):
        language_score = LanguageScore(tmp[i]["LanguageScore"][0][1])

        sentiment = Sentiment(tmp[i]["Sentiment"])

        embedding = Embedding(tmp[i]["Embedding"])

        gender = Gender(
            male=tmp[i]["Gender"][0][1], female=tmp[i]["Gender"][1][1]
        )

        sources = {item[0]: item[1] for item in tmp[i]["SourceType"]}
        sourceType = SourceType(
            social=sources["Social Networking and Messaging"],
            computers=sources["Computers and Technology"],
            games=sources["Games"],
            business=sources["Business/Corporate"],
            streaming=sources["Streaming Services"],
            ecommerce=sources["E-Commerce"],
            forums=sources["Forums"],
            photography=sources["Photography"],
            travel=sources["Travel"],
            adult=sources["Adult"],
            law=sources["Law and Government"],
            sports=sources["Sports"],
            education=sources["Education"],
            food=sources["Food"],
            health=sources["Health and Fitness"],
            news=sources["News"],
        )
        types = {item[0]: item[1] for item in tmp[i]["TextType"]}
        textType = TextType(
            assumption=types["Assumption"],
            anecdote=types["Anecdote"],
            none=types["None"],
            definition=types["Definition"],
            testimony=types["Testimony"],
            other=types["Other"],
            study=types["Statistics/Study"],
        )

        emotions = {item[0]: item[1] for item in tmp[i]["Emotion"]}
        emotion = Emotion(
            love=emotions["love"],
            admiration=emotions["admiration"],
            joy=emotions["joy"],
            approval=emotions["approval"],
            caring=emotions["caring"],
            excitement=emotions["excitement"],
            gratitude=emotions["gratitude"],
            desire=emotions["desire"],
            anger=emotions["anger"],
            optimism=emotions["optimism"],
            disapproval=emotions["disapproval"],
            grief=emotions["grief"],
            annoyance=emotions["annoyance"],
            pride=emotions["pride"],
            curiosity=emotions["curiosity"],
            neutral=emotions["neutral"],
            disgust=emotions["disgust"],
            disappointment=emotions["disappointment"],
            realization=emotions["realization"],
            fear=emotions["fear"],
            relief=emotions["relief"],
            confusion=emotions["confusion"],
            remorse=emotions["remorse"],
            embarrassement=emotions["embarrassment"],
            surprise=emotions["surprise"],
            sadness=emotions["sadness"],
            nervousness=emotions["nervousness"],
        )

        ironies = {item[0]: item[1] for item in tmp[i]["Irony"]}

        irony = Irony(irony=ironies["irony"], non_irony=ironies["non_irony"])

        ages = {item[0]: item[1] for item in tmp[i]["Age"]}

        age = Age(
            below_twenty=ages["<20"],
            twenty_thirty=ages["20<30"],
            thirty_forty=ages["30<40"],
            forty_more=ages[">=40"],
        )

        analysis = Analysis(
            langage_score=language_score,
            sentiment=sentiment,
            embedding=embedding,
            gender=gender,
            source_type=sourceType,
            text_type=textType,
            emotion=emotion,
            irony=irony,
            age=age,
        )

        _out.append(analysis)

        # item.translation = tmp[i]["Translation"]
        # item.embedding = tmp[i]["Embedding"]
        # item.sentiment = tmp[i]["Sentiment"]
        # item.emotion = tmp[i]["Emotion"]
        # item.age.below_twenty = tmp[i]["Age"][0][1]
        # item.age.twenty_thirthy = tmp[i]["Age"][1][1]
        # item.age.thirty_forty = tmp[i]["Age"][2][1]
        # item.age.forty_more = tmp[i]["Age"][3][1]
        # item.gender.female = tmp[i]["Gender"][0][1]
        # item.gender.male = tmp[i]["Gender"][1][1]
        # item.irony.irony = tmp[i]["Irony"][0][1]
        # item.irony.non_irony = tmp[i]["Irony"][1][1]
        # item.language_score = tmp[i]["LanguageScore"]  # ??
        # item.text_type = tmp[i]["TextType"]
        # item.source_type = tmp[i]["SourceType"]

    return _out
