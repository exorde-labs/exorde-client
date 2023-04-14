import os, json, jsonschema, itertools
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
    try:
        jsonschema.validate(instance=value, schema=ipfs_schema)
    except Exception as error:
        print("value is :", value)
        print("ipfs_schema is :", ipfs_schema)
        raise (error)
    return value


def rotate_gateways():
    gateways = [
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        "http://ipfs-gateway.exorde.network/ipfs/",
        "https://w3s.link/ipfs/",
        "https://ipfs.io/ipfs/",
        "https://ipfs.eth.aragon.network/ipfs/",
        "https://api.ipfsbrowser.com/ipfs/get.php?hash=",
    ]

    return (gateways[i % len(gateways)] for i in itertools.count())


class DownloadError(Exception):
    pass


async def download_ipfs_file(hashname: str, max_attempts: int):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
        "Connection": "close",
    }

    gateways = rotate_gateways()

    async with ClientSession(headers=headers) as session:
        for __i__ in range(max_attempts):
            url = next(gateways) + hashname
            try:
                async with session.get(
                    url, timeout=3, allow_redirects=True
                ) as response:
                    if response.status == 200:
                        return await response.json()
            except:
                pass

    raise DownloadError(f"Failed to download {hashname} after {max_attempts} attempts")
