from exorde.models import StaticConfiguration


async def get_balance(static_configuration: StaticConfiguration):
    worker_balance_wei = await static_configuration[
        "read_web3"
    ].eth.get_balance(static_configuration["worker_account"].address)
    worker_balance = round(int(worker_balance_wei) / (10**18), 5)
    return worker_balance
