#! python3.10

import json
import logging
import asyncio
from importlib import metadata
from datetime import datetime
from madtypes import MadType

from configuration import Configuration, get_configuration
from item import get_item, Item
from protocol import (
    spot_data,
    get_transaction_receipt,
    get_worker_account,
    get_protocol_configuration,
    get_contracts_and_abi_cnf,
    get_network_configuration,
)
from ipfs import upload_to_ipfs

from exorde_lab.preprocess import preprocess
from exorde_lab.keywords import populate_keywords
from exorde_lab.keywords.models import Keywords
from exorde_lab.translation import translate
from exorde_lab.translation.models import Translation
from exorde_lab.classification import zero_shot
from exorde_lab.classification.models import Classification
from exorde_lab.analysis.models import Analysis
from exorde_lab.analysis import tag
from exorde_lab.startup import lab_initialization


from models import (
    ProtocolItem,
    ProtocolAnalysis,
    ProcessedItem,
    Batch,
    BatchKindEnum,
    CollectionClientVersion,
    CollectedAt,
    CollectionModule,
)


class Processed(dict, metaclass=MadType):
    translation: Translation
    top_keywords: Keywords
    classification: Classification
    item: Item


async def process_batch(batch: list[Processed], lab_configuration):
    logging.info(f"running batch for {len(batch)}")
    analysis_results: list[Analysis] = tag(
        [processed.translation.translation for processed in batch],
        lab_configuration,
    )
    complete_processes: list[ProcessedItem] = []
    for processed, analysis in zip(batch, analysis_results):
        prot_item = ProtocolItem(
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
        completed = ProcessedItem(
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
        complete_processes.append(completed)
    result_batch: Batch = Batch(
        items=complete_processes, kind=BatchKindEnum.SPOTTING
    )
    return result_batch


async def process(item: Item, lab_configuration) -> Processed:
    try:
        try:
            item = preprocess(item, False)
        except Exception as err:
            logging.error("An error occured pre-processing an item")
            logging.error(err)
            logging.error(json.dumps(item, indent=4))
            raise err

        try:
            translation: Translation = translate(
                item, lab_configuration["installed_languages"]
            )
            if translation.translation == "":
                raise ValueError("No content to work with")
        except Exception as err:
            logging.error("An error occured translating an item")
            logging.error(err)
            logging.error(json.dumps(item, indent=4))
            raise err

        try:
            top_keywords: Keywords = populate_keywords(translation)
        except Exception as err:
            logging.error("An error occured populating keywords for an item")
            logging.error(err)
            logging.error(json.dumps(translation, indent=4))
            raise err

        try:
            classification: Classification = zero_shot(
                translation, lab_configuration
            )
        except Exception as err:
            logging.error("An error occured classifying an item")
            logging.error(err)
            logging.error(json.dumps(translation, indent=4))
            raise err
        return Processed(
            item=item,
            translation=translation,
            top_keywords=top_keywords,
            classification=classification,
        )
    except Exception as err:
        raise (err)


async def prepare_batch(
    batch_size: int, lab_configuration, configuration: Configuration
) -> list[Processed]:
    batch: list[Processed] = []
    generator = get_item()
    async for item in generator:
        try:
            processed_item: Processed = await process(item, lab_configuration)
            batch.append(processed_item)
            logging.info(
                f" + A new item has been processed {len(batch)}/{configuration['batch_size']}"
            )
            if len(batch) == batch_size:
                await generator.aclose()
                return batch
        except:
            logging.exception("An error occured while processing an item")
    return []


from protocol import (
    _read_web3,
    _write_web3,
    get_contracts,
    select_random_faucet,
    faucet,
)


async def main():
    configuration: Configuration = await get_configuration()
    protocol_configuration: dict = get_protocol_configuration()
    network_configuration: dict = await get_network_configuration()
    contracts_and_abi = await get_contracts_and_abi_cnf(
        protocol_configuration, configuration
    )
    read_web3 = _read_web3(
        protocol_configuration, network_configuration, configuration
    )
    contracts = get_contracts(
        read_web3, contracts_and_abi, protocol_configuration, configuration
    )
    worker_account = get_worker_account("some-worker-name")
    gas_cache = {}
    write_web3 = _write_web3(
        protocol_configuration, network_configuration, configuration
    )
    lab_configuration = lab_initialization()
    selected_faucet = select_random_faucet()
    await faucet(None, write_web3, read_web3, selected_faucet, worker_account)
    logging.info("Initialization is complete")

    cursor = 0

    while True:
        cursor += 1
        if cursor % 10 == 0:
            configuration: Configuration = await get_configuration()
        if configuration["online"]:
            batch: list[Processed] = await prepare_batch(
                configuration["batch_size"], lab_configuration, configuration
            )
            if len(batch) != configuration["batch_size"]:
                logging.warning("Something weird is going on")
            try:
                processed_batch = await process_batch(batch, lab_configuration)
            except:
                logging.exception("An error occured during batch processing")
                continue
            cid = await upload_to_ipfs(processed_batch)
            transaction_hash, previous_nonce = await spot_data(
                cid,
                worker_account,
                configuration,
                gas_cache,
                contracts,
                read_web3,
                write_web3,
            )
            await get_transaction_receipt(
                transaction_hash, previous_nonce, worker_account, read_web3
            )
        await asyncio.sleep(configuration["inter_spot_delay_seconds"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
