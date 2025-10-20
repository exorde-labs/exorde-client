from exorde.models import LiveConfiguration, StaticConfiguration
import argparse, logging

async def verify_balance(
    static_configuration: StaticConfiguration,
    live_configuration: LiveConfiguration,
    command_line_arguments: argparse.Namespace,
):
    """
    Legacy function - no longer needed without blockchain.
    Kept as stub for compatibility.
    """
    logging.info("Skipping balance verification (no blockchain)")
    pass
