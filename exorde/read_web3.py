import random
from exorde.instanciate_w3 import instanciate_w3
from web3 import AsyncWeb3


def read_web3(
    protocol_configuration, network_configuration, configuration
) -> AsyncWeb3:
    return instanciate_w3(
        random.choice(  # random ip described in `urlSkale`
            random.choice(
                network_configuration[configuration["target"]]
            )[  # random target
                "urlSkale"
            ]
        )
    )
