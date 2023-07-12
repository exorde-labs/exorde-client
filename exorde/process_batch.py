import logging
from importlib import metadata
from datetime import datetime
import numpy as np
from exorde.models import (
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
    Translation,
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

from exorde.tag import tag
from collections import Counter

def Most_Common(lst):
    data = Counter(lst)
    return data.most_common(1)[0][0]

def merge_chunks(chunks: list[ProcessedItem]) -> ProcessedItem:
    logging.info("Merging chunks")
    try:
        # MERGE RULE HERE
            categories_list = []
            top_keywords_list = []
            gender_list = []
            sentiment_list = []
            source_type_list = []
            text_type_list = []
            emotion_list = []
            language_score_list = []
            irony_list = []
            age_list = []
            embedding_list = []
            for processed_item in chunks:
                item_analysis_ = processed_item.analysis
                categories_list.append(item_analysis_.classification)
                top_keywords_list.append(item_analysis_.top_keywords)
                gender_list.append(item_analysis_.gender)
                sentiment_list.append(item_analysis_.sentiment)
                source_type_list.append(item_analysis_.source_type)
                text_type_list.append(item_analysis_.text_type)
                emotion_list.append(item_analysis_.emotion)
                language_score_list.append(item_analysis_.language_score)
                irony_list.append(item_analysis_.irony)
                age_list.append(item_analysis_.age)
                embedding_list.append(item_analysis_.embedding)

            logging.info("DEBUG merge_chunks")
            ## AGGREGATED VALUES
            ## -> classification: take the majority
            classification_label_list = [x.label for x in categories_list]
            category_agg = Most_Common(classification_label_list)
            ## -> top_keywords: concatenate lists
            keywords_agg = list()
            for top_keywords in top_keywords_list:
                keywords_agg.extend(top_keywords)
            keywords_agg = Keywords(keywords_agg)
            ## -> gender: average tuple
            gender_male_list = [x.male for x in gender_list]
            gender_female_list = [x.female for x in gender_list]
            gender_agg = ()
            for top_keywords in top_keywords_list:
                keywords_agg.extend(top_keywords)
            ## -> sentiment: average all sentiments, or take the MAX/MIN and make the average
            ## -> source_type: average
            ## -> text_type: average
            ## -> emotion: average
            ## -> language_score: average
            ## -> irony: average
            ## -> age: average
            ## -> embedding: average
            mean_embedding = np.mean(annotation, axis=0)
            ####   --- REBUILD MERGED ITEM
            merged_item = ProcessedItem(
                    item= chunks[0].item,
                    analysis=ProtocolAnalysis(
                        classification=category_agg,
                        top_keywords=processed.top_keywords,
                        # language_score=analysis.language_score,
                        # gender=analysis.gender,
                        # sentiment=analysis.sentiment,
                        # embedding=analysis.embedding,
                        # source_type=analysis.source_type,
                        # text_type=analysis.text_type,
                        # emotion=analysis.emotion,
                        # irony=analysis.irony,
                        # age=analysis.age,
                    ),
                    collection_client_version=chunks[0].collection_client_version,
                    collection_module=chunks[0].collection_module,
                    collected_at=chunks[0].collected_at,
                )
    except Exception as e:
        logging.info(f"[Merging items chunks] error: {e}")
    return merged_item

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
            url=processed.item.url,
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
                gender=analysis.gender,
                sentiment=analysis.sentiment,
                embedding=analysis.embedding,
                source_type=analysis.source_type,
                text_type=analysis.text_type,
                emotion=analysis.emotion,
                irony=analysis.irony,
                age=analysis.age,
            ),
            collection_client_version=CollectionClientVersion(
                f"exorde:v.{metadata.version('exorde_data')}"
            ),
            collection_module=CollectionModule("unknown"),
            collected_at=CollectedAt(datetime.now().isoformat() + "Z"),
        )
        if not complete_processes[id]:
            complete_processes[id] = []
        complete_processes[id].append(completed)
    aggregated = []
    for __key__, values in complete_processes.items():
        aggregated.append(merge_chunks(values))
    result_batch: Batch = Batch(items=aggregated, kind=BatchKindEnum.SPOTTING)
    return result_batch
