import logging
import time
from exorde.item import get_item
from exorde.models import Processed, LiveConfiguration
from exorde.process import process, TooBigError
from exorde_data import Item, Content
from typing import AsyncGenerator
from spacy import load as spacy_load
from spikex.pipes import SentX
from spikex.defaults import spacy_version
import tiktoken

nlp_sentencer = spacy_load("en_core_web_trf")
sentx_pipe = SentX() if spacy_version < 3 else "sentx"
## 1 ) Split in sentences
nlp_sentencer.add_pipe(sentx_pipe, before="parser")

def evaluate_token_count(__item__: Processed, encoding_name = "r50k_base") -> int:
    """Returns the number of tokens in a text string."""
    item_content_string = __item__.content
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(item_content_string))
    except Exception as e:
        logging.info(f"[evaluate_token_count] error: {e}, \
                     setting a default item count (250)...")
        num_tokens = 250
    return num_tokens

def split_in_sentences(string):
    sentences = []
    try:
        doc = nlp_sentencer(string)
        for doc in doc.sents:
            sentences.append(doc)
    except Exception as e:
        logging.info(f"[Sentence splitter] error: {e}")
        sentences = []
    return sentences

def aggregate_sents_into_paragraphs(sentences, chunk_size = 500):
    paragraphs = []
    current_paragraph = []
    token_count = 0

    try:
        for sent in  sentences:
            sent_tokens_count = int(evaluate_token_count(str(sent)))
            # Check if adding the current sentence exceeds the maximum token count
            if token_count + sent_tokens_count > chunk_size:
                paragraphs.append(current_paragraph)
                current_paragraph = []
                token_count = 0

            sent_ = str(sent).rstrip("\n").replace("\r\n", "").replace("\n", "")
            current_paragraph.append(sent_)
            token_count += sent_tokens_count

        # Add the last remaining paragraph
        if current_paragraph and len(current_paragraph) > 0:
            merged_paragraph = " ".join(current_paragraph)
            paragraphs.append(merged_paragraph)

        logging.info(f"[Paragraph aggregator] aggregated into ")
    except Exception as e:
        logging.info(f"[Paragraph aggregator] error: {e}")
        paragraphs = []
    return paragraphs

def split_string_into_chunks(string, chunk_size):
    ## 1) Split main text in sentences
    sentences = split_in_sentences(string)
    ## 2) a) Recompose paragraphs from sentences
    ##    b) while keeping each paragram token count under "max_token_count"
    paragraphs = aggregate_sents_into_paragraphs(sentences, chunk_size)
    return paragraphs

def split_item(item: Item, max_token_count: int) -> list[Item]:
    if not item.content or len(item.content) <= max_token_count:
        return [item]
    else:
        return [
            Item(
                content=Content(chunk),
                author=item.author,
                created_at=item.created_at,
                domain=item.domain,
                url=item.url,
            )
            for chunk in split_string_into_chunks(
                item.content, max_token_count
            )
        ]
    

async def prepare_batch(
    static_configuration, live_configuration: LiveConfiguration
) -> list[tuple[int, Processed]]:
    max_depth_classification: int = live_configuration["max_depth"]
    batch: list[tuple[int, Processed]] = []  # id, item
    generator: AsyncGenerator[Item, None] = get_item()
    lab_configuration: dict = static_configuration["lab_configuration"]
    item_id = -1
    async for item in generator:
        item_id = item_id + 1
        try:
            start_time: float = time.perf_counter()
            try:
                processed_item: Processed = await process(
                    item, lab_configuration, max_depth_classification
                )
                batch.append((item_id, processed_item))
            except TooBigError:
                splitted: list[Item] = split_item(
                    item,
                    static_configuration["lab_configuration"][
                        "max_token_count"
                    ],
                )
                for chunk in splitted:
                    processed_chunk: Processed = await process(
                        chunk, lab_configuration, max_depth_classification
                    )
                    batch.append((item_id, processed_chunk))
            end_time: float = time.perf_counter()
            exec_time_s: float = end_time - start_time
            logging.info(
                f" + A new item has been processed {len(batch)}/{live_configuration['batch_size']} - ({exec_time_s} s) - Source = {str(item['domain'])}"
            )
            max_batch_total_tokens_ = int(live_configuration["batch_size"]) \
                                      *  int(static_configuration["lab_configuration"]["max_token_count"])
            if (
                # If we have enough items of each enough tokens
                sum([evaluate_token_count(item) for (__id__, item) in batch]) 
                > max_batch_total_tokens_
                # Or If we have enough items overall
                or len(batch) >= live_configuration["batch_size"]
            ):
                await generator.aclose()
                return batch
        except:
            logging.exception("An error occured while processing an item")
    return []
