from aiosow.bindings import alias
from aiosow.routines import routine, infinite_generator
from exorde_reddit import generate_subreddit_url, scrap_subreddit_url
from exorde.formated import broadcast_formated_when

alias("subreddit_url")(generate_subreddit_url)

get_reddit_post = infinite_generator(lambda: True)(scrap_subreddit_url)
routine(0.2, perpetuate=False)(broadcast_formated_when(get_reddit_post))
