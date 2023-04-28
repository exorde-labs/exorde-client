from aiosow.bindings import setup, alias


from exorde.browser import (
    get_page_websocket_url,
    launch_browser,
    create_websocket_client,
    enable_network,
    run_websocket_client,
    intercept,
    goto,
    evaluate_expression,
)

setup(launch_browser)
alias("page_websocket_url")(get_page_websocket_url)
setup(create_websocket_client)
setup(enable_network)
setup(run_websocket_client)

__all__ = ["intercept", "goto", "evaluate_expression"]
