from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.middleware.async_cache import (
    _async_simple_cache_middleware as cache_middleware,
)


def instanciate_w3(url) -> AsyncWeb3:
    w3_instance = AsyncWeb3(AsyncHTTPProvider(url))
    w3_instance.middleware_onion.add(cache_middleware)
    return w3_instance
