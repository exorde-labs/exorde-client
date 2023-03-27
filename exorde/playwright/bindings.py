from aiosow.bindings import wrap, each, on, setup, option

from . import *

option(
    "no_headless",
    action="store_true",
    default=False,
    help="Wether playwright should run in headless mode",
)
option(
    "user_agent",
    default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    help="User-Agent used by playwright",
)
option("tabs", default=1, help="Amount of tabs open by playwright")
option("tab_lifetime", default=120, help="Lifetime of open tabs in seconds")

# set's up playwright
setup(setup_playwright)
pages = wrap(
    lambda pages: {"pages": {index: pages[index] for index in range(0, len(pages))}}
)


async def _tabs(tabs):
    for i in range(tabs):
        yield i


for_each_tabs = each(iter=_tabs)
page = wrap(lambda page: {"page": page, "available": True})
setup(pages(for_each_tabs(page(create_page))))
on_page_available = on(
    "pages", condition=lambda page: page["available"], singularize=True
)

# do something with the page when available
on_page_available(manage_page)
