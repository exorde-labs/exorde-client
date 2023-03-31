import os, json, jsonschema
from aiohttp import ClientSession


def create_session(*__args__, **__kwargs__):
    return ClientSession()


async def load_json_schema():
    with open(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "schema.json")), "r"
    ) as f:
        return json.load(f)


async def upload_to_ipfs(value, ipfs_path, session):
    async with session.post(
        ipfs_path,
        data=json.dumps(value),
        headers={"Content-Type": "application/json"},
    ) as resp:
        if resp.status == 200:
            response = await resp.json()
            return response
        else:
            content = await resp.text()
            raise Exception(f"Failed to upload to IPFS ({resp.status}) -> {content}")


async def validate_batch_schema(value, ipfs_schema):
    jsonschema.validate(instance=value, schema=ipfs_schema)
    return value
