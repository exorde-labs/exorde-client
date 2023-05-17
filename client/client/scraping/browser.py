from aiosow.bindings import wrap, each, on, setup
from aiosow.routines import routine
from . import *


def build_pages(pages):
    return {"pages": {index: pages[index] for index in range(0, len(pages))}}


organize_pages = wrap(build_pages)


async def _tabs(__browser__, tabs):
    for i in range(tabs):
        yield i


for_each_tabs = each(iter=_tabs)
page = wrap(lambda page: {"page": page, "available": True})
on_page_available = on(
    "pages", condition=lambda page: page["available"], singularize=True
)

setup(setup_playwright)
routine(60)(setup_playwright)
on("browser")(organize_pages(for_each_tabs(page(create_page))))

# do something with the page when available
on_page_available(manage_page)
