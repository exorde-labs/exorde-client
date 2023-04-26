from aiosow.bindings import setup, alias
from aiosow.routines import routine, infinite_generator
from exorde.reddit import generate_reddit_url, scrap_reddit_url
from exorde.formated import broadcast_formated_when

alias("reddit_url")(generate_reddit_url)
setup(scrap_reddit_url)

get_reddit_post = infinite_generator(lambda: True)(scrap_reddit_url)
routine(0.2, perpetuate=False)(broadcast_formated_when(get_reddit_post))
