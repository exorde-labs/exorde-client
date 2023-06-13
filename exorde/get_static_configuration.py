from exorde.select_random_faucet import select_random_faucet
from exorde.get_contracts import get_contracts
from exorde.read_web3 import read_web3 as _read_web3
from exorde.write_web3 import write_web3 as _write_web3
from exorde.get_worker_account import get_worker_account
from exorde.get_protocol_configuration import get_protocol_configuration
from exorde.get_contracts_and_abi_cnf import get_contracts_and_abi_cnf
from exorde.get_network_configuration import get_network_configuration
from exorde.models import StaticConfiguration
from argparse import Namespace
from exorde.lab_initialization import lab_initialization


async def get_static_configuration(
    command_line_arguments: Namespace, live_configuration
) -> StaticConfiguration:
    main_address: str = command_line_arguments.main_address
    protocol_configuration: dict = get_protocol_configuration()
    network_configuration: dict = await get_network_configuration()
    contracts_and_abi = await get_contracts_and_abi_cnf(
        protocol_configuration, live_configuration
    )
    read_web3 = _read_web3(
        protocol_configuration, network_configuration, live_configuration
    )
    contracts = get_contracts(
        read_web3,
        contracts_and_abi,
        protocol_configuration,
        live_configuration,
    )
    worker_account = get_worker_account("some-worker-name")
    gas_cache = {}
    write_web3 = _write_web3(
        protocol_configuration, network_configuration, live_configuration
    )
    lab_configuration = lab_initialization()
    selected_faucet = select_random_faucet()
    return StaticConfiguration(
        main_address=main_address,
        worker_account=worker_account,
        protocol_configuration=protocol_configuration,
        network_configuration=network_configuration,
        contracts=contracts,
        contracts_and_abi=contracts_and_abi,
        read_web3=read_web3,
        write_web3=write_web3,
        lab_configuration=lab_configuration,
        selected_faucet=selected_faucet,
        gas_cache=gas_cache,
    )
