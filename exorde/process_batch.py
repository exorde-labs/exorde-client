import logging
from importlib import metadata
from datetime import datetime
import numpy as np
from exorde.models import (
    Domain,
    ProtocolItem,
    ProtocolAnalysis,
    ProcessedItem,
    Batch,
    BatchKindEnum,
    CollectionClientVersion,
    CollectedAt,
    CollectionModule,
    Processed,
    Analysis,
)
from exorde.models import (
    Classification,
    Keywords,
    LanguageScore,
    Sentiment,
    Embedding,
    SourceType,
    TextType,
    Emotion,
    Irony,
    Analysis
)
from exorde_data import Url

from exorde.tag import tag
from collections import Counter


def Most_Common(lst):
    data = Counter(lst)
    return data.most_common(1)[0][0]


def merge_chunks(chunks: list[ProcessedItem]) -> ProcessedItem:
    try:
        ## Check if chunks is a list of 1 item, if so, just return it as is
        if len(chunks) == 1:
            return chunks[0]

        #### MERGING for items with more than 1 chunks

        categories_list = []
        top_keywords_list = []
        sentiment_list = []
        source_type_list = []
        text_type_list = []
        emotion_list = []
        language_score_list = []
        irony_list = []
        embedding_list = []

        logging.info(f"[Item merging] Merging {len(chunks)} chunks.")
        for processed_item in chunks:
            item_analysis_ = processed_item.analysis
            categories_list.append(item_analysis_.classification)
            top_keywords_list.append(item_analysis_.top_keywords)
            sentiment_list.append(item_analysis_.sentiment)
            source_type_list.append(item_analysis_.source_type)
            text_type_list.append(item_analysis_.text_type)
            emotion_list.append(item_analysis_.emotion)
            language_score_list.append(item_analysis_.language_score)
            irony_list.append(item_analysis_.irony)
            embedding_list.append(item_analysis_.embedding)

        ## AGGREGATED VALUES
        ## -> classification: take the majority
        most_common_category = Most_Common([x.label for x in categories_list])
        category_aggregated = Classification(
            label=most_common_category,
            score=max([x.score for x in categories_list]),
        )
        ## -> top_keywords: concatenate lists
        top_keywords_aggregated = list()
        for top_keywords in top_keywords_list:
            top_keywords_aggregated.extend(top_keywords)
        top_keywords_aggregated = Keywords(
            list(set(top_keywords_aggregated))
        )  # filter duplicates
        ## -> sentiment: Take the median all sentiments
        sentiment_aggregated = Sentiment(np.median(sentiment_list))
        ## -> source_type: Take the majority of source_type (if there is a tie, take "social"). Possible values = "social" or "news"
        source_type_aggregated =  SourceType(
            Most_Common(source_type_list)
        )
        
        ## -> text_type: Take the median
        text_type_aggregated = TextType(
            assumption=np.median([tt.assumption for tt in text_type_list]),
            anecdote=np.median([tt.anecdote for tt in text_type_list]),
            none=np.median([tt.none for tt in text_type_list]),
            definition=np.median([tt.definition for tt in text_type_list]),
            testimony=np.median([tt.testimony for tt in text_type_list]),
            other=np.median([tt.other for tt in text_type_list]),
            study=np.median([tt.study for tt in text_type_list]),
        )
        ## -> emotion: Take the median
        emotion_aggregated = Emotion(
            love=np.median([e.love for e in emotion_list]),
            admiration=np.median([e.admiration for e in emotion_list]),
            joy=np.median([e.joy for e in emotion_list]),
            approval=np.median([e.approval for e in emotion_list]),
            caring=np.median([e.caring for e in emotion_list]),
            excitement=np.median([e.excitement for e in emotion_list]),
            gratitude=np.median([e.gratitude for e in emotion_list]),
            desire=np.median([e.desire for e in emotion_list]),
            anger=np.median([e.anger for e in emotion_list]),
            optimism=np.median([e.optimism for e in emotion_list]),
            disapproval=np.median([e.disapproval for e in emotion_list]),
            grief=np.median([e.grief for e in emotion_list]),
            annoyance=np.median([e.annoyance for e in emotion_list]),
            pride=np.median([e.pride for e in emotion_list]),
            curiosity=np.median([e.curiosity for e in emotion_list]),
            neutral=np.median([e.neutral for e in emotion_list]),
            disgust=np.median([e.disgust for e in emotion_list]),
            disappointment=np.median([e.disappointment for e in emotion_list]),
            realization=np.median([e.realization for e in emotion_list]),
            fear=np.median([e.fear for e in emotion_list]),
            relief=np.median([e.relief for e in emotion_list]),
            confusion=np.median([e.confusion for e in emotion_list]),
            remorse=np.median([e.remorse for e in emotion_list]),
            embarrassment=np.median([e.embarrassment for e in emotion_list]),
            surprise=np.median([e.surprise for e in emotion_list]),
            sadness=np.median([e.sadness for e in emotion_list]),
            nervousness=np.median([e.nervousness for e in emotion_list]),
        )
        ## -> language_score: Take the median
        language_score_aggregated = LanguageScore(
            np.median(language_score_list)
        )
        ## -> irony: Take the median
        irony_aggregated = Irony(
            irony=np.median([i.irony for i in irony_list]),
            non_irony=np.median([i.non_irony for i in irony_list]),
        )
        ## -> embedding: take closest vector to centroid
        centroid_vector = np.median(embedding_list, axis=0)
        # Calculate the closest vector in embedding_list to the centroid_vector
        closest_embedding = Embedding(
            min(
                embedding_list,
                key=lambda x: np.linalg.norm(x - centroid_vector),
            )
        )
        ####   --- REBUILD MERGED ITEM
        merged_item = ProcessedItem(
            item=chunks[0].item,
            analysis=ProtocolAnalysis(
                classification=category_aggregated,
                top_keywords=top_keywords_aggregated,
                language_score=language_score_aggregated,
                sentiment=sentiment_aggregated,
                embedding=closest_embedding,
                source_type=source_type_aggregated,
                text_type=text_type_aggregated,
                emotion=emotion_aggregated,
                irony=irony_aggregated,
            ),
            collection_client_version=chunks[0].collection_client_version,
            collection_module=chunks[0].collection_module,
            collected_at=chunks[0].collected_at,
        )
    except Exception as e:
        logging.exception(f"[Merging items chunks] ERROR:\n {e}")
        merged_item = None
    return merged_item


SOCIAL_DOMAINS = [
    "4chan",
    "4channel.org",
    "reddit.com",
    "twitter.com",
    "t.com",
    "x.com",
    "youtube.com",
    "yt.co",
    "mastodon.social",
    "mastodon",
    "weibo.com",
    "nostr.social",
    "nostr.com",
    "jeuxvideo.com",
    "forocoches.com",
    "bitcointalk.org",
    "ycombinator.com",
    "tradingview.com",
    "followin.in",
    "seekingalpha.io",
]


def get_source_type(item: ProtocolItem) -> SourceType:
    if item.domain in SOCIAL_DOMAINS:
        return SourceType("social")
    return SourceType("news")


async def process_batch(
    batch: list[tuple[int, Processed]], static_configuration
) -> Batch:
    lab_configuration: dict = static_configuration["lab_configuration"]
    logging.info(f"running batch for {len(batch)}")
    analysis_results: list[Analysis] = tag(
        [processed.translation.translation for (__id__, processed) in batch],
        lab_configuration,
    )
    complete_processes: dict[int, list[ProcessedItem]] = {}
    for (id, processed), analysis in zip(batch, analysis_results):
        prot_item: ProtocolItem = ProtocolItem(
            created_at=processed.item.created_at,
            domain=processed.item.domain,
            url=Url(processed.item.url),
            language=processed.translation.language,
        )

        if processed.item.title:
            prot_item.title = processed.item.title
        if processed.item.summary:
            prot_item.summary = processed.item.summary
        if processed.item.picture:
            prot_item.picture = processed.item.picture
        if processed.item.author:
            prot_item.author = processed.item.author
        if processed.item.external_id:
            prot_item.external_id = processed.item.external_id
        if processed.item.external_parent_id:
            prot_item.external_parent_id = processed.item.external_parent_id
        completed: ProcessedItem = ProcessedItem(
            item=prot_item,
            analysis=ProtocolAnalysis(
                classification=processed.classification,
                top_keywords=processed.top_keywords,
                language_score=analysis.language_score,
                sentiment=analysis.sentiment,
                embedding=analysis.embedding,
                source_type=get_source_type(prot_item),
                text_type=analysis.text_type,
                emotion=analysis.emotion,
                irony=analysis.irony,
            ),
            collection_client_version=CollectionClientVersion(
                f"exorde:v.{metadata.version('exorde_data')}"
            ),
            collection_module=CollectionModule("unknown"),
            collected_at=CollectedAt(datetime.now().isoformat() + "Z"),
        )
        if not complete_processes.get(id, {}):
            complete_processes[id] = []
        complete_processes[id].append(completed)
    aggregated = []
    for __key__, values in complete_processes.items():
        merged_ = merge_chunks(values)
        if merged_ is not None:
            aggregated.append(merged_)
    result_batch: Batch = Batch(items=aggregated, kind=BatchKindEnum.SPOTTING)
    return result_batch
