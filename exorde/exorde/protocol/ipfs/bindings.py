from madframe.bindings import setup, wrap, wire

from exorde.protocol.ipfs import (
    # validate_batch_schema,
    upload_to_ipfs,
    create_session,
)


# setup an aiohttp session for ipfs upload
setup(wrap(lambda session: {"session": session})(create_session))


def spot_block(entities):
    return entities


broadcast_new_valid_batch, on_new_valid_batch_do = wire()

# batching
# broadcast_batch_ready, on_batch_ready_do = wire()
push_to_ipfs = broadcast_new_valid_batch(spot_block)

# validation is skipped, added no value and fricition
# when a batch is ready, upload it to ipfs
# on_batch_ready_do(broadcast_new_valid_batch(validate_batch_schema))

broadcast_new_cid, on_new_cid_do = wire(perpetual=True)
on_new_valid_batch_do(broadcast_new_cid(upload_to_ipfs))
