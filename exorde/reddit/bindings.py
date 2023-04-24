from aiosow.bindings import setup, alias
from exorde.reddit import generate_reddit_url, scrap_reddit_url, set_keyword


setup(set_keyword)
alias("reddit_url")(generate_reddit_url)
setup(scrap_reddit_url)
