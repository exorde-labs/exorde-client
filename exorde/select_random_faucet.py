import random


def select_random_faucet():
    private_key_base = (
        "deaddeaddeaddead5fb92d83ed54c0ea1eb74e72a84ef980d42953caaa6d"
    )
    ## faucets private keys are ["Private_key_base"+("%0.4x" % i)] with i from 0 to 499. Last 2 bytes is the selector.

    selected_faucet_index = random.randrange(
        0, 499 + 1, 1
    )  # [select index between 0 & 499 (500 faucets)]

    hex_selector_bytes = "%0.4x" % selected_faucet_index
    faucet_private_key = private_key_base + hex_selector_bytes
    return selected_faucet_index, faucet_private_key
