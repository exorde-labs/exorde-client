from exorde.models import StaticConfiguration
import logging

async def faucet(static_configuration: StaticConfiguration):
    """
    Legacy function - no longer needed without blockchain.
    """
    logging.info("Skipping faucet (no blockchain)")
    pass
