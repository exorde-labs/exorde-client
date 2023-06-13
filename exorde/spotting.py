import logging

from exorde.models import Processed


from exorde.prepare_batch import prepare_batch
from exorde.process_batch import process_batch
from exorde.spot_data import spot_data

from exorde.get_transaction_receipt import get_transaction_receipt
from exorde.ipfs import download_ipfs_file, upload_to_ipfs


async def spotting(live_configuration, static_configuration):
    batch: list[Processed] = await prepare_batch(
        static_configuration,
        live_configuration,
    )
    if len(batch) != live_configuration["batch_size"]:
        logging.warning("Something weird is going on, batch ignored")
        return
    try:
        logging.info("Processing batch")
        processed_batch = await process_batch(batch, static_configuration)
    except:
        logging.exception("An error occured during batch processing")
        return
    try:
        cid = await upload_to_ipfs(processed_batch)
        post_upload_file = await download_ipfs_file(cid)
        item_count = len(post_upload_file["items"])
    except:
        logging.exception("An error occured during IPFS uploading")
        return
    if item_count == 0:
        logging.error(
            "All items of previous batch are already discovered, skipped."
        )
        return
    try:
        logging.info("Building a spot-data transaction")
        transaction_hash, previous_nonce = await spot_data(
            cid,
            static_configuration["worker_account"],
            live_configuration,
            static_configuration["gas_cache"],
            static_configuration["contracts"],
            static_configuration["read_web3"],
            static_configuration["write_web3"],
        )
    except:
        logging.exception("An error occured during transaction building")
        return
    try:
        logging.info("Looking for transaction receipt")
        await get_transaction_receipt(
            transaction_hash, previous_nonce, static_configuration
        )
    except:
        logging.exception("An error occured during transaction validation")
        return
    logging.info("+ A receipt for previous transaction has been confirmed")
