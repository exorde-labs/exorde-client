import random
from exorde.instanciate_w3 import instanciate_w3


def write_web3(protocol_configuration, network_configuration, configuration):
    return instanciate_w3(
        random.choice(network_configuration[configuration["target"]])[
            "_urlTxSkale"
        ]
    )
