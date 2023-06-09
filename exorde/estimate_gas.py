from models import LiveConfiguration


async def estimate_gas(
    transaction, read_web3, gas_cache, configuration: LiveConfiguration
):
    async def do_estimate_gas():
        gas = configuration["default_gas_amount"]  # default gas amount
        estimate = await read_web3.eth.estimate_gas(transaction) * 1.5
        if estimate < 100_000:
            gas = estimate + 500_000
        return max(10_000_000, gas)

    function_bytecode = str(transaction["data"])[2:10]
    data_length = len(str(transaction["data"]))
    gas_key = (function_bytecode, data_length)
    if gas_key in gas_cache:
        transaction["gas"] = gas_cache[gas_key]
    else:
        estimate = await do_estimate_gas()
        gas_cache[gas_key] = estimate
        transaction["gas"] = gas_cache[gas_key]
    return transaction
