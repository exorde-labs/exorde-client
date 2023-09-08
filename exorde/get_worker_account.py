import json, random, logging, string, os
from pathlib import Path
from eth_account import Account


def get_worker_account(worker_name: str) -> Account:
    """Return a worker key based on a name, key stored in .config"""
    keys_file = Path.home() / ".config" / "exorde" / f"{worker_name}.json"
    logging.info(
        f"config directory is : {Path.home() / '.config' / 'exorde' }"
    )
    if keys_file.exists():
        with open(keys_file, "r") as f:
            keys = json.load(f)
            logging.debug('Loaded key "%s" from file', keys["address"])
            return Account.from_key(keys["privateKey"])

    # Generate new keys if the file does not exist
    random.seed(random.random())
    base_seed = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=256)
    )
    acct = Account.create(base_seed)

    # Save the new keys to the file
    os.makedirs(keys_file.parent, exist_ok=True)
    with open(keys_file, "w") as f:
        keys = {
            "address": acct.address,
            "privateKey": acct.key.hex(),
        }
        json.dump(keys, f, indent=4)
        logging.debug('Saved key "%s" to file', keys["address"])

    return acct
