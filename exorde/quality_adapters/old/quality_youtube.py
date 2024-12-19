
import json
import requests
from bs4 import BeautifulSoup
import re
import json
import dateparser
import time
import logging
from itertools import islice
from urllib.parse import urlparse, parse_qs
import json
import time
import csv


from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import SpanKind
# Initialize the tracer provider
resource = Resource(attributes={
    "service.name": "youtube-qualiy"
})
trace.set_tracer_provider(TracerProvider(resource=resource))
# Configure the OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
# Use SimpleSpanProcessor to stream spans immediately
span_processor = SimpleSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
# Use the tracer for application-specific tracing
tracer = trace.get_tracer("youtube")



"""
- Fetch https://www.youtube.com/results?search_query={KEYWORD} example: https://www.youtube.com/results?search_query=bitcoin
- Get all video URLs + their titles
- use youtube-comment library to extract all comments (with id, timestamp, and text)
- rebuild comment URLs from id, select those with recent timestamp
- add title to comment text (as first sentence).
- that's all folks
"""

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v={youtube_id}'
YOUTUBE_CONSENT_URL = 'https://consent.youtube.com/save'
BASE_EMBED_ENDPOINT = "https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v="

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

headers = {
    'User-Agent': USER_AGENT
}

SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

YT_CFG_RE = r'ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;'
YT_INITIAL_DATA_RE = r'(?:window\s*\[\s*["\']ytInitialData["\']\s*\]|ytInitialData)\s*=\s*({.+?})\s*;\s*(?:var\s+meta|</script|\n)'
YT_HIDDEN_INPUT_RE = r'<input\s+type="hidden"\s+name="([A-Za-z0-9_]+)"\s+value="([A-Za-z0-9_\-\.]*)"\s*(?:required|)\s*>'


class YoutubeCommentDownloader:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = USER_AGENT
        self.session.cookies.set('CONSENT', 'YES+cb', domain='.youtube.com')                
        self.MAX_ITERATIONS_CONTINUATIONS_AJAX = 1000

    def ajax_request(self, endpoint, ytcfg, retries=5, sleep=7):
        url = 'https://www.youtube.com' + endpoint['commandMetadata']['webCommandMetadata']['apiUrl']

        data = {'context': ytcfg['INNERTUBE_CONTEXT'],
                'continuation': endpoint['continuationCommand']['token']}

        for _ in range(retries):
            response = self.session.post(url, params={'key': ytcfg['INNERTUBE_API_KEY']}, json=data)
            if response.status_code == 200:
                return response.json()
            if response.status_code in [403, 413]:
                return {}
            else:
                # print("Response status code: %d. Retrying in %d seconds" % (response.status_code, sleep))
                time.sleep(sleep)

    def get_comments(self, youtube_id, *args, **kwargs):
        return self.get_comments_from_url(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id), *args, **kwargs)

    def get_comments_from_url(self, youtube_url, sort_by=SORT_BY_RECENT, language=None, sleep=0.4):
        response = self.session.get(youtube_url)

        if 'consent' in str(response.url):
            # We may get redirected to a separate page for cookie consent. If this happens we agree automatically.
            params = dict(re.findall(YT_HIDDEN_INPUT_RE, response.text))
            params.update({'continue': youtube_url, 'set_eom': False, 'set_ytc': True, 'set_apyt': True})
            response = self.session.post(YOUTUBE_CONSENT_URL, params=params)

        html = response.text
        ytcfg = json.loads(self.regex_search(html, YT_CFG_RE, default=''))
        if not ytcfg:
            return  # Unable to extract configuration
        if language:
            ytcfg['INNERTUBE_CONTEXT']['client']['hl'] = language

        data = json.loads(self.regex_search(html, YT_INITIAL_DATA_RE, default=''))

        item_section = next(self.search_dict(data, 'itemSectionRenderer'), None)
        renderer = next(self.search_dict(item_section, 'continuationItemRenderer'), None) if item_section else None
        if not renderer:
            # Comments disabled?
            return

        sort_menu = next(self.search_dict(data, 'sortFilterSubMenuRenderer'), {}).get('subMenuItems', [])
        if not sort_menu:
            # No sort menu. Maybe this is a request for community posts?
            section_list = next(self.search_dict(data, 'sectionListRenderer'), {})
            continuations = list(self.search_dict(section_list, 'continuationEndpoint'))
            # Retry..
            data = self.ajax_request(continuations[0], ytcfg) if continuations else {}
            sort_menu = next(self.search_dict(data, 'sortFilterSubMenuRenderer'), {}).get('subMenuItems', [])
        if not sort_menu or sort_by >= len(sort_menu):
            raise RuntimeError('Failed to set sorting')
        continuations = [sort_menu[sort_by]['serviceEndpoint']]

        while continuations:
            continuation = continuations.pop()
            response = self.ajax_request(continuation, ytcfg)

            if not response or self.MAX_ITERATIONS_CONTINUATIONS_AJAX == 0:
                break
            self.MAX_ITERATIONS_CONTINUATIONS_AJAX -= 1

            error = next(self.search_dict(response, 'externalErrorMessage'), None)
            if error:
                raise RuntimeError('Error returned from server: ' + error)

            actions = list(self.search_dict(response, 'reloadContinuationItemsCommand')) + \
                      list(self.search_dict(response, 'appendContinuationItemsAction'))
            for action in actions:
                for item in action.get('continuationItems', []):
                    if action['targetId'] in ['comments-section',
                                              'engagement-panel-comments-section',
                                              'shorts-engagement-panel-comments-section']:
                        # Process continuations for comments and replies.
                        continuations[:0] = [ep for ep in self.search_dict(item, 'continuationEndpoint')]
                    if action['targetId'].startswith('comment-replies-item') and 'continuationItemRenderer' in item:
                        # Process the 'Show more replies' button
                        continuations.append(next(self.search_dict(item, 'buttonRenderer'))['command'])

            for comment in reversed(list(self.search_dict(response, 'commentRenderer'))):
                result = {'cid': comment['commentId'],
                          'text': ''.join([c['text'] for c in comment['contentText'].get('runs', [])]),
                          'time': comment['publishedTimeText']['runs'][0]['text'],
                          'author': comment.get('authorText', {}).get('simpleText', ''),
                          'channel': comment['authorEndpoint']['browseEndpoint'].get('browseId', ''),
                          'votes': comment.get('voteCount', {}).get('simpleText', '0'),
                          'photo': comment['authorThumbnail']['thumbnails'][-1]['url'],
                          'heart': next(self.search_dict(comment, 'isHearted'), False),
                          'reply': '.' in comment['commentId']}

                try:
                    result['time_parsed'] = dateparser.parse(result['time'].split('(')[0].strip()).timestamp()
                except AttributeError:
                    pass

                paid = (
                    comment.get('paidCommentChipRenderer', {})
                    .get('pdgCommentChipRenderer', {})
                    .get('chipText', {})
                    .get('simpleText')
                )
                if paid:
                    result['paid'] = paid
                
                yield result
            # print("Sleeping for %s seconds" % sleep)
            time.sleep(sleep)

    @staticmethod
    def regex_search(text, pattern, group=1, default=None):
        match = re.search(pattern, text)
        return match.group(group) if match else default

    @staticmethod
    def search_dict(partial, search_key):
        stack = [partial]
        while stack:
            current_item = stack.pop()
            if isinstance(current_item, dict):
                for key, value in current_item.items():
                    if key == search_key:
                        yield value
                    else:
                        stack.append(value)
            elif isinstance(current_item, list):
                stack.extend(current_item)
                

def fetch_yt_comments_by_video(video_url, comment_ids):
    """
    Args:
    url: The youtube thread URL.

    Returns:
    The first class in the HTML that has "jy27lmt" as a substring of the class.
    """
    yt_comment_dl = YoutubeCommentDownloader()

    def get_youtube_video_id(url):
        parts = url.split("/")
        if parts[-1] == "":
            video_id = parts[-2]
        else:
            video_id = parts[-1]
        # now post_id is of the form watch?v=7EFMIpTtrAk&lc=UgzkZdq7btS4OGyqxt94AaABAg
        # extract the part after watch?v= and before the &lc= and return it
        try:
            video_id = video_id.split("watch?v=")[1].split("&lc=")[0]   
        except:
            pass
        return video_id
    
    video_id = get_youtube_video_id(video_url)
    # print("[Youtube Quality Check] [Metadata] Video ID = ",video_id, " Comment IDs = ",comment_ids)
    # check if the video is real first
    # we add the post_id to the endpoint and make a request, if it's "Bad Request","Unauthorized" or "Not Found", then it's not a real video
    embed_checking_endpoint = BASE_EMBED_ENDPOINT + video_id
    print("[Youtube Quality Check] [Initial Video Realness check] Video Realness Endpoint = ",embed_checking_endpoint)
    # print("[Youtube Quality Check] embed_checking_endpoint = ",embed_checking_endpoint)
    response = requests.get(embed_checking_endpoint, headers=headers, timeout=20)

    empty_comment_typles_list = []
    # put the comment_ids in a list of lists, each list is a tuple of the form [comment_id, comment_text]
    for comment_id in comment_ids:
        empty_comment_typles_list.append([comment_id,""])

    if response.status_code == 400 or response.status_code == 404 or response.status_code == 401:
        print("[Youtube Quality Check] [Initial Video Realness check] Video not found / not allowed to access")
        return empty_comment_typles_list
    # check if "Not Found" or Bad Request:
    if "Not Found" in response.text or "Bad Request" in response.text or "Unauthorized" in response.text:
        print("[Youtube Quality Check] [Initial Video Realness check] Video {} not found".format(video_id))
        return empty_comment_typles_list

    # rebuild the video URL 
    video_URL = YOUTUBE_VIDEO_URL.format(youtube_id = video_id)
    
    # find the title in the json, if json is valid
    try:
        json_response = response.json()
        title = json_response["title"]
        print("[Youtube Quality Check] [Metadata] Video Title = ",title, "URL = ",video_URL)
    except Exception as e:
        print("[Youtube Quality Check] [Metadata] Video Title check FAILURE = ",e)
        return empty_comment_typles_list
    
    # FETCH THE COMMENTS
    comments_list = []
    try:
        comments_list = yt_comment_dl.get_comments_from_url(video_URL)
    except Exception as e:      
        logging.exception(f"[Youtube] get_comments_from_url - error: {e}")
    
    # turn generator into list
    comments_list = list(comments_list)
    print("[Youtube Quality Check] Fetched ",len(comments_list)," comments for that video")
    # find comment with the same comment_id, write a flag to 1 if found and break or else continue
    status = False
    comment_texts = []
    # check if the comment, iteratively, is in the comments_list, if so print them, add them to comment_texts and break
    for comment in comments_list:
        if comment['cid'] in comment_ids:
            status = True
            comment_texts.append([comment['cid'],comment['text']])
        # break if we found all comments    
        if status == True and len(comment_texts) == len(comment_ids):
            break
    # for the remaining comments_id not in comment_texts, add them with empty text
    for comment_id in comment_ids:
        if comment_id not in [comment[0] for comment in comment_texts]:
            comment_texts.append([comment_id,""])
    
    return comment_texts

def extract_video_comment_ids(comment_urls):
    video_comment_mapping = {}
    for url in comment_urls:
        # Parse the URL to extract query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        # Extract the video ID (v) and comment ID (lc) from the query parameters
        # Case 1: normal video with youtube.com/watch?v=VIDEO_ID&lc=COMMENT_ID
        if parsed_url.hostname == 'www.youtube.com' and parsed_url.path == '/watch':
            video_id = query_params.get('v', [None])[0]
            video_id = YOUTUBE_VIDEO_URL.format(youtube_id=video_id)
            comment_id = query_params.get('lc', [None])[0]

            if video_id and comment_id:
                # Check if the video ID is already in the mapping, and append the comment ID
                if video_id in video_comment_mapping:
                    video_comment_mapping[video_id].append(comment_id)
                else:
                    # If the video ID is not in the mapping, create a new entry
                    video_comment_mapping[video_id] = [comment_id]
                    
        # Case 2: short video with youtube.com/shorts/VIDEO_ID&lc=COMMENT_ID
        elif  '/shorts/' in parsed_url.path:
            # get the video_id from the url right after /shorts/ and before the &lc=
            video_id = url.split("/shorts/")[1].split("&lc=")[0]
            # fetch the commend_id from the parsed_url.path
            comment_id = parsed_url.path.split("&lc=")[1]


            if video_id and comment_id:
                # Check if the video ID is already in the mapping, and append the comment ID
                if video_id in video_comment_mapping:
                    video_comment_mapping[video_id].append(comment_id)
                else:
                    # If the video ID is not in the mapping, create a new entry
                    video_comment_mapping[video_id] = [comment_id]
        

    return video_comment_mapping


# Group the comments by video ID, ex https://www.youtube.com/watch?v=8fQ4QEGR1UI&lc=UgxG_Q_qDpkC0pdIXlR4AaABAg, we want to group by 8fQ4QEGR1UI
# We want to group by the video ID, so we split the URL at the '&' character and keep only the first part
# And make a list of lists, where each list is a list of comments for a given video ID:
# [ [comment1, comment2, comment3], [comment4, comment5, comment6], [comment7, comment8, comment9] ]

def clean_youtube_comment_url(url):
    # Transform short URLs into normal URLs    
    if not 'watch?v=' in url and 'shorts' in url:
        # get the video_id from the url right after /shorts/ and before the &lc=
        video_id = url.split("/shorts/")[1].split("&lc=")[0]
        # fetch the commend_id from the parsed_url.path
        comment_id = url.split("&lc=")[1]
        # rebuild the url
        url = YOUTUBE_VIDEO_URL.format(youtube_id = video_id) + "&lc=" + comment_id

    # remove, if any, if the urls contain a dot after the &lc=, then keep only the part before the dot
    # Split the URL by "&lc=" to separate the comment ID
    parts = url.split("&lc=")
    
    # Check if there is a dot ('.') in the comment ID
    if '.' in parts[1]:
        # If there is a dot, remove the part after it
        cleaned_url = parts[0] + "&lc=" + parts[1].split('.')[0]
    else:
        # If there is no dot, the URL is already clean
        cleaned_url = url    
    return cleaned_url

def map_comments(comment_urls, comments):
    comment_dict = {}
    # map the comment_urls to the comments based on the comment_id alone, and the complete url
    # comment_urls = [url1, url2, url3] and comments = [[comment_id1, comment_text1], [comment_id2, comment_text2], [comment_id3, comment_text3]]
    for url in comment_urls:
        for comment in comments:
            comment_id = comment[0].split(".")[0]
            if comment[0] in url:
                comment_dict[url] = comment[1]
                break

    return comment_dict

def fetch_youtube_comments(comment_urls):
    with tracer.start_as_current_span(
        "youtube_subprocess", kind=SpanKind.SERVER
    ) as main_span:
        main_span.set_attribute("comment_urls", str(comment_urls))
        # remove, if any, if the urls contain a dot after the &lc=, then keep only the part before the dot
        # check if the last part has a dot in it, if so, remove it (and everything after it)
        comment_urls = [clean_youtube_comment_url(url) for url in comment_urls]
        grouped_comments = extract_video_comment_ids(comment_urls)

        comment_texts_list = []
        for video_url, comment_ids in grouped_comments.items():
            time.sleep(1)
            comment_tuples  = fetch_yt_comments_by_video(video_url, comment_ids)
            if comment_tuples: # if not False
                comment_texts_list.extend(comment_tuples)
            if len(comment_tuples) == 0:
                print(
                    "[Youtube Quality Check] Comment(s) not found on video ",video_url," with comment_ids = ", 
                    comment_ids
                )
        return comment_texts_list


##############################################################################################################################################################

# read the file youtube_urls.csv, read one URL per line, up to 50 lines and put them in comments_urls
# read from folder logs and open 50 of the last files by timestamp (events_TIMESTAMP.json)
# get the first 50 youtube urls in youtube_urls.csv
def get_some_URLs(n=10):
    comments_urls = []
    with open('youtube_urls.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        import random
        counter = 0
        for row in reader:
            # add rows randomly to comments_urls
            if random.random() < 0.25:
                counter += 1
                comments_urls.append(row[0])
            if counter == n:
                break

    return comments_urls

def get_youtube_comments_by_URL(comments_urls):
    comments = fetch_youtube_comments(comments_urls)
    print(f"fetched {len(comments)} comments")
    # count how many comments are empty (2nd part of each tuple)
    empty_comments = [comment for comment in comments if comment[1] == ""]
    comment_map = map_comments(comments_urls, comments)
    print("\n[Youtube Quality Check] Number of to-verify-comments we could not fetch = ",len(empty_comments), "out of ",len(comments))
    return comment_map


def run(urls: str) -> bytes:
    return json.dumps(
        get_youtube_comments_by_URL(json.loads(urls)), ensure_ascii=False
    ).encode("utf-8")

# MAIN BLOCK
if __name__ == '__main__':
    # get the first 50 youtube urls in youtube_urls.csv
    comments_urls = [
        "https://www.youtube.com/watch?v=YF5_7eWzOe4&lc=UgzZiZd0_MHu_nKIspp4AaABAg",
        "https://www.youtube.com/watch?v=YF5_7eWzOe4&lc=UgyehJfEOFYSDZBh4CJ4AaABAg",
        "https://www.youtube.com/watch?v=6VZfeexme4c&lc=Ugzkk7FsbYPdIdtu8-R4AaABAg",
        "https://www.youtube.com/watch?v=6VZfeexme4c&lc=UgzQjHu9pN-sHq4gBNB4AaABAg",
        "https://www.youtube.com/watch?v=6VZfeexme4c&lc=UgyMY2gPRTazyLieDK54AaABAg",
        "https://www.youtube.com/watch?v=6VZfeexme4c&lc=UgxKjE6h_Vx40smSvYN4AaABAg",
        "https://www.youtube.com/watch?v=6VZfeexme4c&lc=Ugw8Bxein0ywE5dJcyd4AaABAg",
        "https://www.youtube.com/watch?v=6VZfeexme4c&lc=UgyKynuNbVZijtK65h94AaABAg",
        "https://www.youtube.com/watch?v=6VZfeexme4c&lc=UgwD_tEGZjSmQ-ZzTmd4AaABAg",
        "https://www.youtube.com/watch?v=6VZfeexme4c&lc=UgyjiEtzAnZqoZJj4aZ4AaABAg"
    ]

    for comment_url in comments_urls:
        print("[Youtube Quality Check] Comment URL = ",comment_url)
    print()
    comment_map = get_youtube_comments_by_URL(comments_urls)
    # Print the result
    for url, comment in comment_map.items():
        print(f"URL: {url}\nComment: {comment}\n")
