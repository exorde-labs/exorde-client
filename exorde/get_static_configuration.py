from exorde.get_protocol_configuration import get_protocol_configuration
from exorde.models import StaticConfiguration
from argparse import Namespace
from exorde.lab_initialization import lab_initialization
import logging, os

async def do_get_static_configuration(
    command_line_arguments: Namespace, live_configuration
) -> StaticConfiguration:
    main_address: str = command_line_arguments.main_address
    protocol_configuration: dict = get_protocol_configuration()
    
    # Initialize lab configuration (ML models, etc.)
    lab_configuration = lab_initialization()
    
    return StaticConfiguration(
        main_address=main_address,
        protocol_configuration=protocol_configuration,
        lab_configuration=lab_configuration,
    )

async def get_static_configuration(
    command_line_arguments: Namespace, live_configuration
) -> StaticConfiguration:
    try:
        static_configuration: StaticConfiguration = (
            await do_get_static_configuration(
                command_line_arguments, live_configuration
            )
        )
        return static_configuration
    except:
        logging.exception(
            "An error occured retrieving static configuration, exiting"
        )
        os._exit(1)
