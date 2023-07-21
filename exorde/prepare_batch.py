import logging
import time
from wtpsplit import WtP
from exorde.item import get_item
from exorde.models import Processed, LiveConfiguration
from exorde.process import process, TooBigError
from exorde_data import Item, Content
from typing import AsyncGenerator
import tiktoken
from ftlangdetect import detect as lang_detect

wtp = WtP("wtp-canine-s-1l")

def evaluate_token_count(item_content_string: str, encoding_name: str = "r50k_base") -> int:
    """Returns the number of tokens in a text string."""
    try:
        if item_content_string is None or len(item_content_string)<=1:
            logging.info(f"[evaluate_token_count] the content is empty")
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(item_content_string))
    except Exception as e:
        logging.info(f"[evaluate_token_count] error: {e}")
        num_tokens = 0
    return num_tokens

def split_in_sentences(string: str):
    sentences = []    
    detected_language = lang_detect(string, low_memory=False)
    try:
        try:
            sents = wtp.split(string, lang_code=detected_language)
        except:
            logging.info(f"WTP: could not split with lang: {detected_language}, trying with English...")
            sents = wtp.split(string, lang_code='en')

        for doc in sents:
            sentences.append(doc)
    except Exception as e:
        logging.info(f"[Sentence splitter] error: {e}")
        sentences = []
    
    sentences = [x for x in sentences if x and len(x)>5]
    logging.info(f"Debug sentences : {sentences})
    return sentences

def aggregate_sents_into_paragraphs(sentences: list[str], chunk_size: int = 500):
    paragraphs = []
    current_paragraph = []
    token_count = 0

    try:
        for sent in  sentences:
            sent_ = str(sent).replace("\n", "")
            sent_tokens_count = int(evaluate_token_count(str(sent_)))
            # Check if adding the current sentence exceeds the maximum token count
            if token_count + sent_tokens_count > chunk_size:
                current_paragraph_str = " ".join(current_paragraph)
                paragraphs.append(current_paragraph_str)
                current_paragraph = []
                token_count = 0
                
            current_paragraph.append(sent_)
            token_count += sent_tokens_count

        # Add the last remaining paragraph
        if len(current_paragraph) > 0:
            current_paragraph_str = " ".join(current_paragraph)
            paragraphs.append(current_paragraph_str)

        logging.info(f"[Paragraph aggregator] Made {len(paragraphs)} paragraphs ({chunk_size} tokens long)")
    except Exception as e:
        logging.info(f"[Paragraph aggregator] error: {e}")
        paragraphs = []
    
    paragraphs = [x for x in paragraphs if x and len(x)>5]
    return paragraphs

def split_string_into_chunks(string: str, chunk_size: int):
    ## 1) Split main text in sentences
    sentences = split_in_sentences(string)
    ## 2) a) Recompose paragraphs from sentences
    ##    b) while keeping each paragram token count under "max_token_count"
    paragraphs = aggregate_sents_into_paragraphs(sentences, chunk_size)
    return paragraphs

def split_item(item: Item, max_token_count: int) -> list[Item]:
    if not item.content or len(str(item.content)) <= max_token_count:
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
                str(item.content), max_token_count
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
                    live_configuration["max_token_count"]
                )
                for chunk in splitted:
                    processed_chunk: Processed = await process(
                        chunk, lab_configuration, max_depth_classification
                    )
                    batch.append((item_id, processed_chunk))
            end_time: float = time.perf_counter()
            item_token_count = evaluate_token_count(str(item.content))
            exec_time_s: float = end_time - start_time
            logging.info(
                f" + A new item has been processed {len(batch)}/{live_configuration['batch_size']} - ({exec_time_s} s) - Source = {str(item['domain'])} -  token count = {item_token_count}"
            )
            max_batch_total_tokens_ = int(live_configuration["batch_size"]) \
                                      *  int(static_configuration["lab_configuration"]["max_token_count"])

            if (
                # If we have enough items of each enough tokens
                sum([evaluate_token_count(str(item.item.content)) for (__id__, item) in batch]) 
                > max_batch_total_tokens_
                # Or If we have enough items overall
                or len(batch) >= live_configuration["batch_size"]
            ):
                await generator.aclose()
                return batch
        except:
            logging.info("An error occured while processing an item")
    return []
