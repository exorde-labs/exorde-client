from ipfs import upload_to_ipfs
import logging

from models import Processed


from prepare_batch import prepare_batch
from process_batch import process_batch
from spot_data import spot_data

from get_transaction_receipt import get_transaction_receipt


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
    cid = await upload_to_ipfs(processed_batch)
    post_upload_file = await download_ipfs_file(cid)
    item_count = len(post_uploaf_file["items"])
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
