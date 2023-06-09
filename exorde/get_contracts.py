import logging


def contract(
    name, read_w3, contracts_and_abi, protocol_configuration, configuration
):
    abi_cnf = contracts_and_abi["abi_cnf"]
    contracts_cnf = contracts_and_abi["contracts_cnf"]
    try:
        return read_w3.eth.contract(
            contracts_cnf[configuration["target"]][name],
            abi=abi_cnf[name]["abi"],
        )
    except:
        logging.info(f"Skipped contract instanciation for {name}")
        return None


def get_contracts(
    read_w3, contracts_and_abi, protocol_configuration, configuration
):
    return {
        name: contract(
            name,
            read_w3,
            contracts_and_abi,
            protocol_configuration,
            configuration,
        )
        for name in contracts_and_abi["contracts_cnf"][configuration["target"]]
    }
