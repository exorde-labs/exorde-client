import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
import json

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import SpanKind
# Initialize the tracer provider
resource = Resource(attributes={
    "service.name": "reddit-quality"
})
trace.set_tracer_provider(TracerProvider(resource=resource))
# Configure the OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
# Use SimpleSpanProcessor to stream spans immediately
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
# Use the tracer for application-specific tracing
tracer = trace.get_tracer("reddit")


############################################################
####################################################################################################################################################################################
####################################################################################################################################################################################
############################################################
def find_reddit_post_on_direct_url(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.3"
    last_p_block_text = ""
    def get_reddit_post_id(url):
        parts = url.split("/")
        if parts[-1] == "":
            post_id = parts[-2]
        else:
            post_id = parts[-1]
        return post_id
    
    post_id = get_reddit_post_id(url)

    # request the URL with user-agent:
    headers = {
    'User-Agent': user_agent
    }
    response = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(response.content, "html.parser")
    # find first div with id="thing_t1_POSTID"

    try:
        class_substring = "thing_t1_{}".format(post_id)
        r = soup.find("div", {"id": class_substring})
        # print("[Reddit] Found div with id = ",r["id"]," and class = ",r["class"])
        last_p_block_text = r.find_all("p")[-1].get_text()
        # print("[Reddit] Text found = ",last_p_block_text,"\n")
    except Exception as e:
        print("[Reddit] Error: ",e)
        return None
    
    return last_p_block_text

def convert_to_old_url(url):
    # Parse the input URL
    parsed_url = urlparse(url)
    # Check if the netloc (domain) starts with "www."
    if parsed_url.netloc.startswith("www."):
        # Remove "www." from the netloc
        netloc = parsed_url.netloc[4:]
    else:
        netloc = parsed_url.netloc
    # Check if the URL already starts with "https://old.reddit.com"
    if parsed_url.netloc == "old.reddit.com":
        return url  # It's already in the old format
    # Create the old Reddit URL by replacing the netloc and scheme
    old_reddit_url = urlunparse(
        (
            "https",
            "old.reddit.com",
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        )
    )
    return old_reddit_url


def find_batch_reddit_posts_on_direct_urls(urls):
    """
    Fill a dict mapping url -> reddit post
    """
    items = {}
    with tracer.start_as_current_span(
        "reddit_subprocess", kind=SpanKind.SERVER
    ) as main_span:
        main_span.set_attribute("url_amount", len(urls))
        for url in urls:
            with tracer.start_as_current_span(
                "find_reddit_post_on_url"
            ) as find_reddit_post_on_url_span:
                find_reddit_post_on_url_span.set_attribute("url", url)
                items[url] = find_reddit_post_on_direct_url(
                    convert_to_old_url(url)
                )
    return items





# MAIN BLOCK
if __name__ == '__main__':
    reddit_sample_url = [
        "https://www.reddit.com/r/FreeKarma4All/comments/169y82p/comment/jz4dwh3/",
        "https://www.reddit.com/r/texas/comments/169uya8/comment/jz4cfuj/",
        "https://www.reddit.com/r/texas/comments/169uya8/comment/jz4bxqd/",
        "https://www.reddit.com/r/splatoon/comments/169uflc/comment/jz4cad6/",
        "https://www.reddit.com/r/splatoon/comments/169uflc/comment/jz49xjz/", 
        "https://www.reddit.com/r/splatoon/comments/169uflc/comment/jz4bvwv/",
        "https://www.reddit.com/r/DBZDokkanBattle/comments/169qhxh/comment/jz4eaaf/",
        "https://www.reddit.com/r/soccer/comments/169xdku/comment/jz4ial9/"
    ]

    urls_content_map = find_batch_reddit_posts_on_direct_urls(reddit_sample_url)

    for url in urls_content_map:
        print("[reddit] url = ",url," and content = ",urls_content_map[url])
