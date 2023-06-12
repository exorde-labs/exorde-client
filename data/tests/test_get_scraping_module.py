from exorde_data import get_scraping_module_version


def test_get_scraping_module_version():
    reddit_version = get_scraping_module_version("reddit")
    assert reddit_version == "0.0.1"
