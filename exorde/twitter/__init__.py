from dateutil import parser


def generate_twitter_url() -> str:
    return "https://twitter.com/search?q=BTC&src=typed_query&f=live"


twitter_to_exorde_format = lambda data: {
    "entities": [],
    "item": {
        "Author": "",
        "Content": data["full_text"].replace("\n", "").replace("'", "''"),
        "Controversial": data.get("possibly_sensitive", False),
        "CreationDateTime": parser.parse(data["created_at"]).isoformat(),
        "Description": "",
        "DomainName": "twitter.com",
        "Language": data["lang"],
        "Reference": "",
        "Title": "",
        "Url": f"https://twitter.com/a/status/{data['id_str']}",
        "internal_id": str(data["id"]),
        "internal_parent_id": None,
        "mediaType": "",
        # "source": data['source'], # new
        # "nbQuotes": data['quote_count'], # new
        "nbComments": data["reply_count"],
        "nbLiked": data["favorite_count"],
        "nbShared": data["retweet_count"],
        # "isQuote": data['is_quote_status'] # new
    },
    "keyword": "",
    "links": [],
    "medias": [],
    "spotterCountry": "",
    "tokenOfInterest": [],
}
