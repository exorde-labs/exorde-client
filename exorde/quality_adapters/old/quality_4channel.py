
import json
import requests
import re
from bs4 import BeautifulSoup

timeout_base = 50000 # 20s in milisecond
BATCH_SIZE = 10
MAX_RETRIES = 3
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"


############################################################
####################################################################################################################################################################################
####################################################################################################################################################################################
############################################################
from typing import Generator


def find_4chan_post_per_thread(urls) -> Generator[dict[str, str], None, None]:

    def get_thread_id(url):
        # if of the form "https://boards.4channel.org/sp/thread/134706613"
        if "/thread/" in url and not "#" in url:
            parts = url.split("/")
            thread_id = parts[-1]
        # if of the form "https://boards.4channel.org/sp/thread/134706613#p134728567"
        elif "#p" in url:
            parts = url.split("#p")
            # then split again with "/"
            parts = parts[0].split("/")
            thread_id = parts[-1]
        return thread_id

    def get_post_id(url):
        # if of the form "https://boards.4channel.org/sp/thread/134706613"
        if "/thread/" in url and not "#" in url:
            parts = url.split("/")
            post_id = parts[-1]
        # if of the form "https://boards.4channel.org/sp/thread/134706613#p134728567"
        elif "#p" in url:
            parts = url.split("#p")
            post_id = parts[-1]
        return post_id
    
    def clean_4chan_text(text):
        # remove "">>123456789" >> followed by 9 digits at most
        text = re.sub(r'>>[0-9]{1,9}', '', text)
        return text

    # get unique thread_URLs from urls
    # by removing the #pXXXXXX part (if present)
    unique_thread_urls = []
    for str in urls:
        str_ = str
        if "#p" in str: # remove what's after the # (including the #)
            # check if the # is not the last char or if there is any # in the remaining string
            if str.index("#") < len(str)-1 and "#" in str[str.index("#")+1:]:
                str_ = str[:str.index("#")]
            else:
                str_ = str[:str.index("#")]
        unique_thread_urls.append(str_)
            
    # get only unique thread URLs
    unique_thread_urls = set(unique_thread_urls)

    all_posts_ids = []
    for url in urls:
        all_posts_ids.append(get_post_id(url))
    
    # group URLs by thread
    threads_id_comment_id_map = {}
    comment_id_URL_map = {}
    for url in urls:
        thread_id = get_thread_id(url)
        if thread_id in threads_id_comment_id_map:
            threads_id_comment_id_map[thread_id].append(get_post_id(url))
        else:
            threads_id_comment_id_map[thread_id] = [get_post_id(url)]
        comment_id_URL_map[get_post_id(url)] = url

    # request the URL with user-agent:
    headers = {
    'User-Agent': user_agent
    }   
    urls_content_map = {}

    # GET THE COMMENTS OR POST
    for thread_url in unique_thread_urls:
        # print("\n\n***** [4chan] thread_url = ",thread_url)
        # fetch page html for each thread
        response = requests.get(thread_url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.content, "html.parser")
        # get all the posts in the thread & check if the post_id is in the list of posts we want to get
        for post_id in all_posts_ids:
            if post_id in threads_id_comment_id_map[get_thread_id(thread_url)]:
                # print("CHECKING POST ID = ",post_id," IN THREAD = ",thread_url)
                try:
                    # looking for a "blockquote" tag with class "postMessage" and "id" = "mPOSTID"
                    class_substring = "m{}".format(post_id)
                    blockquote = soup.find(
                        "blockquote", {"class": "postMessage", "id": class_substring}
                    )
                    if blockquote is None:
                        print("[4chan] COMMENT NOT FOUND IN THREAD = ",get_thread_id(thread_url)," AND POST ID = ",post_id,". SKIPPING...")
                        continue
                    post_text = blockquote.get_text(strip=True)
                    post_text = clean_4chan_text(post_text)
                    # print( "[4chan] Text found = ",post_text,"\n")
                    
                    initial_URL = thread_url    
                    if post_id in comment_id_URL_map:
                        initial_URL = comment_id_URL_map[post_id]
                    urls_content_map[initial_URL] = post_text
                    yield { initial_URL: post_text }
                except Exception as e:
                    print("[4chan] Error: ",e)
        
        # remaining empty urls with content:
        for url in urls:
            if url not in urls_content_map:
                urls_content_map[url] = ""

   



# MAIN BLOCK
if __name__ == '__main__':
    list = [
        "https://boards.4channel.org/sp/thread/134706613#p134717196",
        "https://boards.4channel.org/sp/thread/134706613#p134717196",
        "https://boards.4channel.org/sp/thread/134706613#p134712262",
        "https://boards.4channel.org/sp/thread/134706613#p134724278",
        "https://boards.4channel.org/sp/thread/134706613#p134724278",
        "https://boards.4channel.org/biz/thread/56055485",
        "https://boards.4channel.org/biz/thread/56055485#p56055496",
        "https://boards.4channel.org/biz/thread/56055485#p56056102"
    ]
    urls_content_map = find_4chan_post_per_thread(list)


    for url in urls_content_map:
        print("[4chan] url = ",url," and content = ",urls_content_map[url])
