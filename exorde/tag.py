import json
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from finvader import finvader
from huggingface_hub import hf_hub_download
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import tensorflow as tf
import swifter
from exorde.models import (
    Translation,
    Classification,
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


def tag(documents: list[str], lab_configuration):
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
    nlp = lab_configuration["nlp"]
    device = lab_configuration["device"]
    mappings = lab_configuration["mappings"]

    def predict(text, pipe, tag, mappings):
        preds = pipe.predict(text, verbose=0)[0]
        result = []
        for i in range(len(preds)):
            result.append((mappings[tag][i], float(preds[i])))
        return result

    # get text content attribute from all items
    for doc in documents:
        assert isinstance(doc, str)

    # Create an empty DataFrame
    tmp = pd.DataFrame()

    # Add the original text documents
    tmp["Translation"] = documents

    assert tmp["Translation"] is not None
    assert len(tmp["Translation"]) > 0

    # Compute sentence embeddings
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    tmp["Embedding"] = tmp["Translation"].swifter.apply(
        lambda x: list(model.encode(x).astype(float))
    )

    # Text classification pipelines
    text_classification_models = [
        ("Emotion", "SamLowe/roberta-base-go_emotions"),
        ("Classification", "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33"),
        ("Irony", "cardiffnlp/twitter-roberta-base-irony"),
        ("TextType", "marieke93/MiniLM-evidence-types"),
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
                padding="max_length",
                return_attention_mask=False,
                return_tensors="tf",
            )["input_ids"][0]
        ).reshape(1, -1)
    )

    sentiment_analyzer = SentimentIntensityAnalyzer()
    try:
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
        sentiment_analyzer.lexicon.update(Loughran_dict)
        sentiment_analyzer.lexicon.update(unic_emoji_dict)
    except Exception as e:
        logging.info("[TAGGING] Error loading Loughran_dict & unic_emoji_dict for sentiment_analyzer. Doing without.")

    
    ############################
    # financial distilroberta
    fdb_tokenizer = AutoTokenizer.from_pretrained("mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
    fdb_model = AutoModelForSequenceClassification.from_pretrained("mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
    ############################
    # distilbert sentiment
    gdb_tokenizer = AutoTokenizer.from_pretrained("lxyuan/distilbert-base-multilingual-cased-sentiments-student")
    gdb_model = AutoModelForSequenceClassification.from_pretrained("lxyuan/distilbert-base-multilingual-cased-sentiments-student")
    ############################

    fdb_pipe = pipeline(
        "text-classification",
        model=fdb_model,
        tokenizer=fdb_tokenizer,
        top_k=None, 
        max_length=512,
        padding=True,
    )

    gdb_pipe = pipeline(
        "text-classification",
        model=gdb_model,
        tokenizer=gdb_tokenizer,
        top_k=None, 
        max_length=512,
        padding=True,
    )

    def vader_sentiment(text):
        # predict financial sentiment 
        return round(sentiment_analyzer.polarity_scores(text)["compound"],2)
    
    def fin_vader_sentiment(text):
        # predict general sentiment 
        return round(finvader(text, 
                        use_sentibignomics = True, 
                        use_henry = True, 
                        indicator = 'compound' ),2)

    def fdb_sentiment(text):
        prediction = fdb_pipe(text)
        fdb_sentiment_dict = {}
        for e in prediction[0]:
            if e["label"] == "negative":
                fdb_sentiment_dict["negative"] = round(e["score"],3)
            elif e["label"] == "neutral":
                fdb_sentiment_dict["neutral"] =  round(e["score"],3)
            elif e["label"] == "positive":
                fdb_sentiment_dict["positive"] =  round(e["score"],3)
        # compounded score
        fdb_compounded_score = round((fdb_sentiment_dict["positive"] - fdb_sentiment_dict["negative"]),3)
        return fdb_compounded_score

    def gdb_sentiment(text):
        # predict general sentiment 
        prediction = gdb_pipe(text)
        gen_distilbert_sent = {}
        for e in prediction[0]:
            if e["label"] == "negative":
                gen_distilbert_sent["negative"] = round(e["score"],3)
            elif e["label"] == "neutral":
                gen_distilbert_sent["neutral"] =  round(e["score"],3)
            elif e["label"] == "positive":
                gen_distilbert_sent["positive"] =  round(e["score"],3)
        # compounded score
        gdb_score = round((gen_distilbert_sent["positive"] - gen_distilbert_sent["negative"]),3)
        return gdb_score
    
    def compounded_financial_sentiment(text):
        #  65% financial distil roberta model + 35% fin_vader_score
        fin_vader_sent = fin_vader_sentiment(text)
        fin_distil_score = fdb_sentiment(text)
        fin_compounded_score = round((0.70 * fin_distil_score + 0.30 * fin_vader_sent),2)
        return fin_compounded_score
        
    def compounded_sentiment(text):
        # compounded_total_score: gen_distilbert_sentiment * 60% + vader_sentiment * 20% + compounded_fin_sentiment * 20%
        gen_distilbert_sentiment = gdb_sentiment(text)
        vader_sent = vader_sentiment(text)
        compounded_fin_sentiment = compounded_financial_sentiment(text)
        if abs(compounded_fin_sentiment) >= 0.6:
            compounded_total_score = round((0.30 * gen_distilbert_sentiment + 0.10 * vader_sent + 0.60 * compounded_fin_sentiment),2)
        elif abs(compounded_fin_sentiment) >= 0.4:
            compounded_total_score = round((0.40 * gen_distilbert_sentiment + 0.20 * vader_sent + 0.40 * compounded_fin_sentiment),2)
        elif abs(compounded_fin_sentiment) >= 0.1:
            compounded_total_score = round((0.60 * gen_distilbert_sentiment + 0.25 * vader_sent + 0.15 * compounded_fin_sentiment),2)
        else:  # if abs(compounded_fin_sentiment) < 0.1, so no apparent financial component
            compounded_total_score = round((0.60 * gen_distilbert_sentiment + 0.40 * vader_sent),2)
        return compounded_total_score

    # sentiment swifter apply compounded_sentiment
    tmp["Sentiment"] = tmp["Translation"].swifter.apply(compounded_sentiment)
    
    # financial sentiment swifter apply compounded_financial_sentiment
    tmp["FinancialSentiment"] = tmp["Translation"].swifter.apply(compounded_financial_sentiment)

    del tmp["Embedded"]
    # The output is a list of dictionaries, where each dictionary represents a single input text and contains
    # various processed data like embeddings, text classifications, sentiment, etc., as key-value pairs.
    # Update the items with processed data
    tmp = tmp.to_dict(orient="records")

    _out = []
    for i in range(len(tmp)):

        # add Sentiment
        sentiment = Sentiment(tmp[i]["Sentiment"])

        # add Embedding
        embedding = Embedding(tmp[i]["Embedding"])

        # add Classification
        classification_data = {item[0]: item[1] for item in tmp[i]["Classification"]}
        # Get the label and score of the top classification
        top_label = classification_data["labels"][0]
        top_score = round(classification_data["scores"][0], 4)
        # Create the classification dictionary in the desired format
        classification = Classification(label=top_label, score=top_score)
        
        # mock gender
        gender = Gender(male=0.5, female=0.5)
        types = {item[0]: item[1] for item in tmp[i]["TextType"]}
        text_type = TextType(
            assumption=types["Assumption"],
            anecdote=types["Anecdote"],
            none=types["None"],
            definition=types["Definition"],
            testimony=types["Testimony"],
            other=types["Other"],
            study=types["Statistics/Study"],
        )

        # Emotions
        emotions = {item[0]: item[1] for item in tmp[i]["Emotion"]}
        # round all values to 4 decimal places
        emotions = {k: round(v, 4) for k, v in emotions.items()}
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
            embarrassment=emotions["embarrassment"],
            surprise=emotions["surprise"],
            sadness=emotions["sadness"],
            nervousness=emotions["nervousness"],
        )

        # Irony
        ironies = {item[0]: item[1] for item in tmp[i]["Irony"]}
        irony = Irony(irony=ironies["irony"], non_irony=ironies["non_irony"])
        # Age (untrained model)
        age = Age(below_twenty=0.0, twenty_thirty=0.0, thirty_forty=0.0, forty_more=0.0)
        # Language score (untrained model)
        language_score = LanguageScore(int(1)) # default value
        # Add the analysis to the output list
        analysis = Analysis(
            classification=classification,
            language_score=language_score,
            sentiment=sentiment,
            embedding=embedding,
            gender=gender,
            text_type=text_type,
            emotion=emotion,
            irony=irony,
            age=age,
        )

        _out.append(analysis)
    return _out
