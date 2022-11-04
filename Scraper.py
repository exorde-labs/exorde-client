# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 15:37:49 2022

@author: flore
"""

# import boto3
# import csv
# import datetime as dt
# from datetime import timezone
# from dateutil.parser import parse
# from ftlangdetect import detect
# import html
# import json
# import numpy as np
# import os
# import pandas as pd
# import pickle
# import psycopg2 as ps
# import pytz
# import random
# import re
# import requests
# from scipy.special import softmax, expit
# import shutil
# import snscrape.modules
# import string
# import sys
# import threading
# import time
# import transformers
# from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig, TFAutoModelForSequenceClassification
# import urllib.request
# import warnings
# import web3
# from web3 import Web3, HTTPProvider
# import yake


### Initiliazing variables
#print("[INFO --- {}] Initializing variables".format(dt.datetime.now(pytz.timezone('Europe/Paris'))))

#warnings.simplefilter(action='ignore')
CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

netConfig = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/NetworkConfig.txt").json()
w3 = Web3(Web3.HTTPProvider(netConfig["_urlSkale"]))



def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext


def preprocess(text):
    new_text = [
    ]
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def generateFileName():
    random.seed(random.random())
    baseSeed = ''.join(random.choices(string.ascii_uppercase + string.digits, k=256))
    fileName = baseSeed + '.txt'
    return fileName

def filebase_upload(content: str, bucket_name: str):
    
    s3 = boto3.resource(
        's3',
        endpoint_url = 'https://s3.filebase.com',
        region_name='us-east-1',
        aws_access_key_id='24C83682E3758DA63DD9',
        aws_secret_access_key='B149EQGd1WwGLpuWHgPGT5wQ5OqgXPq3AOQtTeBr'
    )
    response = s3.Object(bucket_name, generateFileName()).put(Body=content)

    return response["ResponseMetadata"]["HTTPHeaders"]['x-amz-meta-cid']


def gen_chan(r):
    for idx, page in enumerate(r):
        for thread in r[idx]['threads']:
            yield thread
            
def get_threads(threads, key: str, default='NaN'):
    return threads.get(key, default)

def downloadFile(hashname: str, name: str):

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
        'pinata_api_key': "19d2b24b75ad7253aebf",  # "0a3c682cdac6f59c497f",
        # "d17b895242d8913b5c5a8dc9933a11223fc5f81696705c78bce150083ad2341d"
        'pinata_secret_api_key': "f69150422667f79ce5a7fb0997bfdbb3750894cd1734275f77d867647e4f3df4"
        # 'Authorization': "Bearer MjRDODM2ODJFMzc1OERBNjNERDk6QjE0OUVRR2QxV3dHTHB1V0hnUEdUNXdRNU9xZ1hQcTNBT1F0VGVCcjpleG9yZGUtc3BvdHMtMQ=="
    }

    url = "https://ipfs.filebase.io/ipfs/" + hashname
    r = requests.get(url, headers=headers, allow_redirects=True,
                     stream=True, timeout=1200)

    try:
        os.mkdir("ExordeWD")
    except:
        pass

    open('ExordeWD\\'+name, 'wb').write(r.content)

def downloadFile2Data2(hashname: str):

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
        #'pinata_api_key': "19d2b24b75ad7253aebf",  # "0a3c682cdac6f59c497f",
        #'pinata_secret_api_key': "f69150422667f79ce5a7fb0997bfdbb3750894cd1734275f77d867647e4f3df4"
        # 'Authorization': "Bearer MjRDODM2ODJFMzc1OERBNjNERDk6QjE0OUVRR2QxV3dHTHB1V0hnUEdUNXdRNU9xZ1hQcTNBT1F0VGVCcjpleG9yZGUtc3BvdHMtMQ=="
    }
    #hashname = "QmdwoHTfa2EHHxH1NVZvaBsE7hQm7aWzKHEMXPLS1VRSZH"
    #url = "https://" + hashname + ".ipfs.w3s.link/"
    #url = url+hashname
    url = "https://w3s.link/ipfs/" + hashname
    #print("Downloading from: ", url)

    trials = 0

    while trials < 5:
        #print("Trials:", trials)
        try:
            r = requests.get(url, timeout=(0.5,3))
            #print(r)
            if (r.status_code == 200):
                try:
                    return r.json()
                except Exception as e:
                    pass
                    #print(e)
            else:
                pass
        except requests.exceptions.Timeout:
            #print("timeout")
            trials += 1
    # Maybe set up for a retry, or continue in a retry loop
        except requests.exceptions.TooManyRedirects:
            #print("redirect")
            trials += 1
    # Tell the user their URL was bad and try a different one
        except requests.exceptions.RequestException as e:
            #print("request", e)
            trials += 1
    # catastrophic error. bail.
        except Exception as e:
            #print(e)
            trials += 1
            pass
    if (trials >= 5):
        return None
    
class Scraper():
    
    def __init__(self, app):

        r = requests.get("https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv").text.split("\n")
        names = r[0]
        data = r[1:]
                
        self.app = app
        self.langcodes = pd.DataFrame(data)
        self.langcodes = pd.DataFrame(self.langcodes[0].str.split(",").values.tolist()).reset_index(drop=True)
        self.langcodes = self.langcodes[self.langcodes.columns[:-1]]
        self.langcodes.columns=names.split(",")
        # self.languageIndex = requests.get("https://ipfs.io/ipfs/Qma8Vh9RwSZqgtF7YnwktmJqCyQosjDc3MdoArXKPQXaUc", allow_redirects=True, stream=True, timeout=(1,5)).json()["Content"]
        # self.lang_registry = dict()
        # self.lang_registry["en"] = requests.get("https://ipfs.io/ipfs/"+self.languageIndex["en"], allow_redirects=True, stream=True, timeout=(1,5)).json()["Content"]
        self.stopWords = dict()
        self.stopWords["en"] = requests.get("https://raw.githubusercontent.com/LIAAD/yake/master/yake/StopwordsList/stopwords_{}.txt".format("en"), allow_redirects=True, stream=True, timeout=(1,5)).text.replace("\r","").split("\n")
        self.models = dict()
        self.languages = dict()
        self.threads = list()
        self.pendingBlocks = list()
        self.lastBatchSize = 100
        self.nbItems = 0
        
        self.keywords = list()
            
        goingOn = True

        try:
            os.mkdir("ExordeWD")
        except:
            pass

        trial = 0
        while (os.path.exists('ExordeWD\\lang.json') == False and trial < 3):
            downloadFile("QmQK6M7pum6W2ZRLdhgzEw7vH8GYMmvwR3aX3hFkMXWrus", "lang.json")
        with open('ExordeWD\\lang.json', "r") as file:
            self.lang_table = json.load(file)["langlist"]
        if (os.path.exists('ExordeWD\\lang.json') == False):
            goingOn = False
        self.listlang = self.lang_table
        
    def manage_scraping(self):
        #print("Scraper manage_scraping started")
        sender = threading.Thread(target=self.manage_sending)
        
        sender.daemon = True
        sender.start()
        
        try:
            while True:
    
                try:
    
                    threads= list()
                    removal = list()
                    
                    for i in range(len(self.threads)):
                        
                        if(self.threads[i].is_alive() == True):
                            #threads.append(self.threads[i])
                            removal.append(self.threads[i])
                        else:
                            removal.append(self.threads[i])
                            
                    self.threads = threads
                    while(len(removal) > 0):
                        del removal[0]
                            
                    
        
                    # if(len(self.keywords) > 0):
                        
                    #     print("[INFO --- {}] Current active threads:".format(dt.datetime.now(pytz.timezone('Europe/Paris'))), len(self.threads))
                    #     print("[INFO --- {}] Starting scraping -".format(dt.datetime.now(pytz.timezone('Europe/Paris'))), "Keywords:", self.keywords)
        
                    keywords = [x.replace(" ","%20") for x in self.keywords]
                    
                    
                    # for i in range(len(keywords)):
                    #     keywords[i] = keywords[i].replace(" ","%20")
                    # tk.messagebox.showwarning("New scraping session",
                    #                           ','.join(keywords))
                    
                    for target in ["4chan", "twitter", "reddit"]: 
                        
                        # if(target == "4chan"):
                        #     x = threading.Thread(target=self.scrape, args=(target, keywords))
                        #     x.start()
                        #     self.threads.append(x)
                        
                        if(target == "twitter"):
                            x = threading.Thread(target=self.scrape, args=("twitter1", keywords))
                            x.daemon = True
                            x.start()
                            self.threads.append(x)
                            y = threading.Thread(target=self.scrape, args=("twitter2", keywords))
                            y.daemon = True
                            y.start()
                            self.threads.append(x)
                                    
                        if(target == "reddit"):
                            x = threading.Thread(target=self.scrape, args=("reddit1", keywords))
                            x.daemon = True
                            x.start()
                            self.threads.append(x)
                            y = threading.Thread(target=self.scrape, args=("reddit2", keywords))
                            y.daemon = True
                            y.start()
                            self.threads.append(y)
                            z = threading.Thread(target=self.scrape, args=("reddit3", keywords))
                            z.daemon = True
                            z.start()
                            self.threads.append(z)
                            a = threading.Thread(target=self.scrape, args=("reddit4", keywords))
                            a.daemon = True
                            a.start()
                            self.threads.append(a)
                            
                    if(len(self.keywords) > 0):
                        time.sleep(2.5*60)
                    else:
                        time.sleep(2.5*60)
                except Exception as e:
                    #print("inner manage_scraping", e)
                    pass
        except Exception as e:
            #print("manage_scraping",e)
            pass
            
    def scrape(self, target: str, keywords: list):

        try:
            results = dict()
            
            try:
                exd_token = random.choice(list(pd.DataFrame([x.strip().lower() for x in requests.get("https://raw.githubusercontent.com/exorde-labs/TestnetProtocol/main/targets/keywords.txt").text.replace("\n","").split(",") if x != ""])[0]))
            except:
                exd_token = "bitcoin"

            if scrape_printing_enabled:
                print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"COLLECT DATA", "scrape", "KEYWORDS  = [{}]\n".format(exd_token)))
            if(exd_token not in keywords):
                keywords.append(exd_token)

            if(target == "4chan"):
                
                try:
    
                    for p in range(1, 10):
                        #print(p)
                        for endpoint in [f"https://a.4cdn.org/biz/{p}.json", f"https://a.4cdn.org/news/{p}.json"]:
            
                            r = requests.get(endpoint)
                            r = json.loads(r.text)
                                                                                            
                            for post in gen_chan(r):
            
                                for key in post:
                                    
                                    threads = post[key][0]
                                    
                                    no = get_threads(threads,'no')
                                    time = get_threads(threads,'time')
                                    com = cleanhtml(html.unescape(get_threads(threads,'com')))
                                    name = get_threads(threads,'name')
                                    ids = get_threads(threads,'id')
                                    filename = html.unescape(get_threads(threads,'filename')) + html.unescape(get_threads(threads,'ext'))
                                    replies = get_threads(threads,'replies')
                                    images = get_threads(threads,'images')
                                    url = re.search("(?P<url>https?://[^\s]+)", get_threads(threads,'com')).group("url") if re.search("(?P<url>https?://[^\s]+)", get_threads(threads,'com')) != None else None
                                    
                                    tr_post = dict()
                                                        
                                    tr_post["internal_id"] = str(no)
                                    tr_post["internal_parent_id"] = None
                                    
                                    tr_post["keyword"] = ""
                                    tr_post["mediaType"] = "Social_Networks"
                                    tr_post["domainName"] = "4channel.org"
                                    tr_post["url"] = "https://boards.4channel.org/biz/thread/" + str(no)
                                    tr_post["author"] = name
                                    tr_post["authorLocation"] = ""
                                    tr_post["creationDateTime"] = dt.datetime.fromtimestamp(time,pytz.timezone('UTC'))
                                    if(tr_post["creationDateTime"] >= (dt.datetime.now(pytz.timezone('UTC')) - dt.timedelta(minutes=5))):
                                    #print(tr_post["creationDateTime"])
                                        #print(tr_post["url"])
                                        tr_post["lang"] = detect(text=com.replace("\n",""), low_memory=False)["lang"]
                                        if(tr_post["lang"] in self.languages):
                                            self.languages[tr_post["lang"]] += 1
                                        else:
                                            self.languages[tr_post["lang"]] = 1
                                        tr_post["title"] = ''
                                        tr_post["description"] = ''
                                        tr_post["content"] = com.replace("\n","").replace("'","''")
                                        if(tr_post["content"] in ("","[removed]") and tr_post["title"] not in ("","[deleted]")):
                                            tr_post["content"] = tr_post["title"]
                                           
                                        # tokens = cat_tokenizer(tr_post["content"][:500], return_tensors='pt')
                                        # output = cat_model(**tokens)
                                        # scores = output[0][0].detach().numpy()
                                        # scores = expit(scores)
                                        # predictions = (scores >= 0.5) * 1
                                        # cat_results = list()
                                        # for i in range(len(predictions)):
                                        #   if predictions[i]:
                                        #       try:
                                        #           cat_results.append(cat_class_mapping[i])
                                        #       except:
                                        #           pass
                                        # tr_post["categories"] = cat_results
                                        
                                        # try:
                                        #     text = preprocess(tr_post["content"])
                                        #     encoded_input = ironizer(text, return_tensors='pt')
                                        #     output = mdl_ironizer(**encoded_input)
                                        #     scores = output[0][0].detach().numpy()
                                        #     scores = softmax(scores)
                
                                        #     if(scores[0] < scores[1]):
                                        #         isIrony = True
                                        #     else:
                                        #         isIrony = False
                                        #     tr_post["isIrony"] = isIrony
                                        # except:
                                        #     text = preprocess(tr_post["content"][:500])
                                        #     encoded_input = ironizer(text, return_tensors='pt')
                                        #     output = mdl_ironizer(**encoded_input)
                                        #     scores = output[0][0].detach().numpy()
                                        #     scores = softmax(scores)
                
                                        #     if(scores[0] < scores[1]):
                                        #         isIrony = True
                                        #     else:
                                        #         isIrony = False
                                        #     tr_post["isIrony"] = isIrony
                                            
                                        
                                        # try:
                                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"])    
                                        # except:
                                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"][:500])    
                                        # if(len(tr_post["content"]) < 50):
                                        #     tr_post["emotions"] = tr_post["emotions"].loc[:2]
                                        
                                        # try:
                                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                                        # except:
                                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                                        tr_post["controversial"] = False
                                        # tr_post["toxic"] = self.models["toxicity"][0].predict(self.models["toxicity"][1].transform([tr_post["content"]]))[0]
                                        # tr_post["censored"] = (self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["content"]]))[0] or self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["url"]]))[0])
                
                                        tr_post["tokenOfInterest"] = list()
                                        max_ngram_size = 1
                                        deduplication_thresold = 0.9
                                        deduplication_algo = 'seqm'
                                        windowSize = 1
                                        numOfKeywords = 20
                                        
                                        kw_extractor = yake.KeywordExtractor(lan=tr_post["lang"], n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
                                        kx = kw_extractor.extract_keywords(tr_post["content"])
                
                                        for kw in kx:
                                            if(kw[0] not in tr_post["tokenOfInterest"]):
                                                tr_post["tokenOfInterest"].append(kw[0])    
                                           
                                        tr_post["reference"] = endpoint.split("/")[3]
                                        tr_post["link"] = None
                                        tr_post["is_video"] = None
                                        tr_post["nb_comments"] = replies
                                        tr_post["nb_shared"] = 0
                                        tr_post["nb_liked"] = 0
                                        tr_post["topics"] = list()
                                        tr_post["entities"] = list()
                                        tr_post["medias"] = list()
                                        tr_post["links"] = list()
                                        
                                        if(tr_post["url"] not in results and tr_post["content"] != 'NaN'):
                                            self.send_doc(tr_post)
                                            #results[tr_post["url"]] = tr_post
                                        
                                        
                                        if 'last_replies' in threads:
                                            for comment in threads['last_replies']:
                    
                                                com_com = cleanhtml(comment.get('com', 'NaN'))
                                                time_com = comment.get('time', 'NaN')
                                                fname_com = comment.get('filename', 'NaN')
                                                
                                                tr_post = dict()
                                                
                                                tr_post["internal_id"] = str(comment["no"])
                                                tr_post["internal_parent_id"] = str(no)
                                                
                                                tr_post["keyword"] = ""
                                                tr_post["mediaType"] = "Social_Networks"
                                                tr_post["domainName"] = "4channel.org"
                                                tr_post["url"] = "https://boards.4channel.org/biz/thread/" + str(no) + "/" + str(comment["no"])
                                                #print(tr_post["url"])
                                                tr_post["author"] = name
                                                tr_post["authorLocation"] = ""
                                                tr_post["creationDateTime"] = dt.datetime.fromtimestamp(time_com,pytz.timezone('UTC'))
                                                tr_post["lang"] = detect(text=com_com.replace("\n",""), low_memory=False)["lang"]
                                                if(tr_post["lang"] in self.languages):
                                                    self.languages[tr_post["lang"]] += 1
                                                else:
                                                    self.languages[tr_post["lang"]] = 1
                                                tr_post["title"] = ''
                                                tr_post["description"] = ''
                                                tr_post["content"] = com_com.replace("\n","").replace("'","''")
                                                if(tr_post["content"] in ("","[removed]") and tr_post["title"] != ""):
                                                    tr_post["content"] = tr_post["title"]
                                                    
                                                # tokens = cat_tokenizer(tr_post["content"][:500], return_tensors='pt')
                                                # output = cat_model(**tokens)
                                                # scores = output[0][0].detach().numpy()
                                                # scores = expit(scores)
                                                # predictions = (scores >= 0.5) * 1
                                                # cat_results = list()
                                                # for i in range(len(predictions)):
                                                #   if predictions[i]:
                                                #       try:
                                                #           cat_results.append(cat_class_mapping[i])
                                                #       except:
                                                #           pass
                                                # tr_post["categories"] = cat_results
                                                
    
                                                    
                                                # try:
                                                #     text = preprocess(tr_post["content"])
                                                #     encoded_input = ironizer(text, return_tensors='pt')
                                                #     output = mdl_ironizer(**encoded_input)
                                                #     scores = output[0][0].detach().numpy()
                                                #     scores = softmax(scores)
                
                                                #     if(scores[0] < scores[1]):
                                                #         isIrony = True
                                                #     else:
                                                #         isIrony = False
                                                #     tr_post["isIrony"] = isIrony
                                                # except:
                                                #     text = preprocess(tr_post["content"][:500])
                                                #     encoded_input = ironizer(text, return_tensors='pt')
                                                #     output = mdl_ironizer(**encoded_input)
                                                #     scores = output[0][0].detach().numpy()
                                                #     scores = softmax(scores)
                
                                                #     if(scores[0] < scores[1]):
                                                #         isIrony = True
                                                #     else:
                                                #         isIrony = False
                                                #     tr_post["isIrony"] = isIrony
                                                                                                
                                                # tr_post["emotions"] = emotions
                                                # try:
                                                #     tr_post["emotions"] = self.calc_emotions(tr_post["content"])    
                                                # except:
                                                #     tr_post["emotions"] = self.calc_emotions(tr_post["content"][:500])    
                                                # if(len(tr_post["content"]) < 50):
                                                #     tr_post["emotions"] = tr_post["emotions"].loc[:2]
                                                
                                                
                                                # try:
                                                #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                                                # except:
                                                #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                                                tr_post["controversial"] = False
                                                # tr_post["toxic"] = self.models["toxicity"][0].predict(self.models["toxicity"][1].transform([tr_post["content"]]))[0]
                                                # tr_post["censored"] = (self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["content"]]))[0] or self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["url"]]))[0])
                
                                                tr_post["tokenOfInterest"] = list()
                                                max_ngram_size = 1
                                                deduplication_thresold = 0.9
                                                deduplication_algo = 'seqm'
                                                windowSize = 1
                                                numOfKeywords = 20
                                                
                                                kw_extractor = yake.KeywordExtractor(lan=tr_post["lang"], n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
                                                kx = kw_extractor.extract_keywords(tr_post["content"])
                
                                                for kw in kx:
                                                    if(kw[0] not in tr_post["tokenOfInterest"]):
                                                        tr_post["tokenOfInterest"].append(kw[0])    
                                                    
                                                tr_post["reference"] = endpoint.split("/")[3]
                                                tr_post["link"] = None
                                                tr_post["is_video"] = None
                                                tr_post["nb_comments"] = 0
                                                tr_post["nb_shared"] = 0
                                                tr_post["nb_liked"] = 0
                                                tr_post["topics"] = list()
                                                tr_post["entities"] = list()
                                                tr_post["medias"] = list()
                                                tr_post["links"] = list()
                                                
                                                if(tr_post["url"] not in results):
                                                    self.send_doc(tr_post)
                                                    #results[tr_post["url"]] = tr_post
                                                    #self.send_item(tr_post)
                            
            
                except Exception as e:
                    # print()
                    # print(target, e)
                    # print()
                    pass
                    
            if(target == "reddit1"):
                
                try:
                
                    r = requests.get("https://api.pushshift.io/reddit/search/comment/?q="+"|".join(keywords)+"&after=5m").json()
                    #r = requests.get("https://api.pushshift.io/reddit/search/comment/?q="+keyword+"&after=5m").json()
                    posts = r["data"]      
                    
                    
                    for post in posts:

                        break
                        #try:
                        tr_post = dict()
                        
                        tr_post["internal_id"] = post["id"]
                        tr_post["internal_parent_id"] = post["parent_id"] if post["parent_id"] != None else 0
                        
                        
                        
                        tr_post["domainName"] = "reddit.com"
                        tr_post["mediaType"] = "Social_Networks"
                        tr_post["url"] = "https://www.reddit.com" + post["permalink"]
                        tr_post["author"] = post["author"]
                        tr_post["authorLocation"] = ""
                        tr_post["creationDateTime"] = dt.datetime.fromtimestamp(post["created_utc"],pytz.timezone('UTC'))
                        tr_post["lang"] = detect(text=post["body"].replace("\n",""), low_memory=False)["lang"]
                        if(tr_post["lang"] in self.languages):
                            self.languages[tr_post["lang"]] += 1
                        else:
                            self.languages[tr_post["lang"]] = 1
                        tr_post["title"] = ''
                        tr_post["description"] = ''
                        tr_post["content"] = cleanhtml(post["body"].replace("\n","").replace("'","''"))
                        if(tr_post["content"] in ("","[removed]") and tr_post["title"] != ""):
                            tr_post["content"] = tr_post["title"]
                            
                        subkeywords = [x for x in keywords if x in tr_post["content"]]
                        tr_post["keyword"] = subkeywords[0] if len(subkeywords) != 0 else keywords[0]
        
                        
                        # tokens = cat_tokenizer(tr_post["content"][:500], return_tensors='pt')
                        # output = cat_model(**tokens)
                        # scores = output[0][0].detach().numpy()
                        # scores = expit(scores)
                        # predictions = (scores >= 0.5) * 1
                        # cat_results = list()
                        # for i in range(len(predictions)):
                        #   if predictions[i]:
                        #       try:
                        #           cat_results.append(cat_class_mapping[i])
                        #       except:
                        #           pass
                        # tr_post["categories"] = cat_results
                                            
                        # try:
                        #     text = preprocess(tr_post["content"])
                        #     encoded_input = ironizer(text, return_tensors='pt')
                        #     output = mdl_ironizer(**encoded_input)
                        #     scores = output[0][0].detach().numpy()
                        #     scores = softmax(scores)
        
                        #     if(scores[0] < scores[1]):
                        #         isIrony = True
                        #     else:
                        #         isIrony = False
                        #     tr_post["isIrony"] = isIrony
                        # except:
                        #     text = preprocess(tr_post["content"][:500])
                        #     encoded_input = ironizer(text, return_tensors='pt')
                        #     output = mdl_ironizer(**encoded_input)
                        #     scores = output[0][0].detach().numpy()
                        #     scores = softmax(scores)
        
                        #     if(scores[0] < scores[1]):
                        #         isIrony = True
                        #     else:
                        #         isIrony = False
                        #     tr_post["isIrony"] = isIrony
                            
                        # try:
                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"])    
                        # except:
                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"][:500])    
                        # if(len(tr_post["content"]) < 50):
                        #     tr_post["emotions"] = tr_post["emotions"].loc[:2]
                        
                        
                        # try:
                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                        # except:
                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                        tr_post["controversial"] = False
                        # tr_post["toxic"] = self.models["toxicity"][0].predict(self.models["toxicity"][1].transform([tr_post["content"]]))[0]
                        # tr_post["censored"] = (self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["content"]]))[0] or self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["url"]]))[0])
        
                        tr_post["tokenOfInterest"] = list()
                        max_ngram_size = 1
                        deduplication_thresold = 0.9
                        deduplication_algo = 'seqm'
                        windowSize = 1
                        numOfKeywords = 20
                        
                        kw_extractor = yake.KeywordExtractor(lan=tr_post["lang"], n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
                        kx = kw_extractor.extract_keywords(tr_post["content"])
        
                        for kw in kx:
                            if(kw[0] not in tr_post["tokenOfInterest"]):
                                tr_post["tokenOfInterest"].append(kw[0])    
        
                        tr_post["reference"] = post["subreddit"]
                        tr_post["link"] = None
                        tr_post["is_video"] = None
                        tr_post["nb_comments"] = 0
                        tr_post["nb_shared"] = 0
                        tr_post["nb_liked"] = 0
                        tr_post["topics"] = list()
                        tr_post["entities"] = list()
                        tr_post["medias"] = list()
                        tr_post["links"] = list()
        
                        
                        if(tr_post["url"] not in results):
                            #results[tr_post["url"]] = tr_post
                            self.send_doc(tr_post)
                            #self.send_item(tr_post)
                            
                except Exception as e:
                    # print()
                    # print(target, e)
                    # print()
                    pass
                
            if(target == "reddit2"):
                
                r = requests.get("https://api.pushshift.io/reddit/search/submission/?q="+"|".join(keywords)+"&after=5m").json()
                #r = requests.get("https://api.pushshift.io/reddit/search/submission/?q="+keyword+"&after=5m").json()
                posts = r["data"]  
    
                for post in posts:
                    try:
                        tr_post = dict()
                        
                        tr_post["internal_id"] = post["id"]
                        tr_post["internal_parent_id"] = 0
                        
                        tr_post["domainName"] = "reddit.com"
                        tr_post["mediaType"] = "Social_Networks"
                        tr_post["url"] = post["full_link"]
                        tr_post["author"] = post["author"]
                        tr_post["authorLocation"] = ""
                        tr_post["creationDateTime"] = dt.datetime.fromtimestamp(post["created_utc"],pytz.timezone('UTC'))
                        tr_post["lang"] = detect(text=post["selftext"].replace("\n",""), low_memory=False)["lang"] if "selftext" in post else detect(text=post["titile"].replace("\n",""), low_memory=False)["lang"]
                        if(tr_post["lang"] in self.languages):
                            self.languages[tr_post["lang"]] += 1
                        else:
                            self.languages[tr_post["lang"]] = 1
                        tr_post["title"] = post["title"]
                        tr_post["description"] = ''
                        tr_post["content"] = cleanhtml(post["selftext"].replace("\n","").replace("'","''")) if "selftext" in post else cleanhtml(post["title"].replace("\n","").replace("'","''")) 
                        if(tr_post["content"] in ("","[removed]") and tr_post["title"] != ""):
                            tr_post["content"] = tr_post["title"]
                            
                        subkeywords = [x for x in keywords if x in tr_post["content"]]
                        tr_post["keyword"] = subkeywords[0] if len(subkeywords) != 0 else keywords[0]
                        
                        # tokens = cat_tokenizer(tr_post["content"][:500], return_tensors='pt')
                        # output = cat_model(**tokens)
                        # scores = output[0][0].detach().numpy()
                        # scores = expit(scores)
                        # predictions = (scores >= 0.5) * 1
                        # cat_results = list()
                        # for i in range(len(predictions)):
                        #   if predictions[i]:
                        #       try:
                        #           cat_results.append(cat_class_mapping[i])
                        #       except:
                        #           pass
                        # tr_post["categories"] = cat_results
                                                
                        # try:
                        #     text = preprocess(tr_post["content"])
                        #     encoded_input = ironizer(text, return_tensors='pt')
                        #     output = mdl_ironizer(**encoded_input)
                        #     scores = output[0][0].detach().numpy()
                        #     scores = softmax(scores)
    
                        #     if(scores[0] < scores[1]):
                        #         isIrony = True
                        #     else:
                        #         isIrony = False
                        #     tr_post["isIrony"] = isIrony
                        # except:
                        #     text = preprocess(tr_post["content"][:500])
                        #     encoded_input = ironizer(text, return_tensors='pt')
                        #     output = mdl_ironizer(**encoded_input)
                        #     scores = output[0][0].detach().numpy()
                        #     scores = softmax(scores)
    
                        #     if(scores[0] < scores[1]):
                        #         isIrony = True
                        #     else:
                        #         isIrony = False
                        #     tr_post["isIrony"] = isIrony
                            
                        # try:
                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"])    
                        # except:
                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"][:500])    
                        # if(len(tr_post["content"]) < 50):
                        #     tr_post["emotions"] = tr_post["emotions"].loc[:2]
                        
                        
                        # try:
                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                        # except:
                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                        tr_post["controversial"] = False
                        # tr_post["toxic"] = self.models["toxicity"][0].predict(self.models["toxicity"][1].transform([tr_post["content"]]))[0]
                        # tr_post["censored"] = (self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["content"]]))[0] or self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["url"]]))[0])
    
                        tr_post["tokenOfInterest"] = list()
                        max_ngram_size = 1
                        deduplication_thresold = 0.9
                        deduplication_algo = 'seqm'
                        windowSize = 1
                        numOfKeywords = 20
                        
                        kw_extractor = yake.KeywordExtractor(lan=tr_post["lang"], n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
                        kx = kw_extractor.extract_keywords(tr_post["content"])
    
                        for kw in kx:
                            if(kw[0] not in tr_post["tokenOfInterest"]):
                                tr_post["tokenOfInterest"].append(kw[0])    
                        
                        tr_post["reference"] = post["subreddit"]
                        tr_post["link"] = post["url"]
                        tr_post["is_video"] = post["is_video"]
                        tr_post["nb_comments"] = 0
                        tr_post["nb_shared"] = 0
                        tr_post["nb_liked"] = 0
                        tr_post["topics"] = list()
                        tr_post["entities"] = list()
                        tr_post["medias"] = list()    
                        tr_post["links"] = list()
        
                        if(tr_post["url"] not in results):
                            #self.send_item(tr_post)
                            #results[tr_post["url"]] = tr_post
                            self.send_doc(tr_post)
                            #Save to DB
                    except Exception as e:
                        # print()
                        # print(target, e)
                        # print()
                        pass
                    
            if(target == "reddit3"):
                
                r = requests.get("https://api.pushshift.io/reddit/search/comment/?subreddit="+"|".join(keywords)+"&after=5m").json()
                #r = requests.get(f'https://api.pushshift.io/reddit/search/comment/?subreddit='+keyword+"&after=5m").json()
                posts = r["data"] 
    
                for post in posts:
                    try:
                        tr_post = dict()
                        
                        tr_post["internal_id"] = post["id"]
                        tr_post["internal_parent_id"] = post["parent_id"] if post["parent_id"] != None else 0
                        
                        tr_post["domainName"] = "reddit.com"
                        tr_post["mediaType"] = "Social_Networks"
                        tr_post["url"] = "https://www.reddit.com" + post["permalink"]
                        tr_post["author"] = post["author"]
                        tr_post["authorLocation"] = ""
                        tr_post["creationDateTime"] = dt.datetime.fromtimestamp(post["created_utc"],pytz.timezone('UTC'))
                        tr_post["lang"] = detect(text=post["body"].replace("\n",""), low_memory=False)["lang"]
                        if(tr_post["lang"] in self.languages):
                            self.languages[tr_post["lang"]] += 1
                        else:
                            self.languages[tr_post["lang"]] = 1
                        tr_post["title"] = ''
                        tr_post["description"] = ''
                        tr_post["content"] = cleanhtml(post["body"].replace("\n","").replace("'","''"))
                        if(tr_post["content"] in ("","[removed]") and tr_post["title"] != ""):
                            tr_post["content"] = tr_post["title"]
                            
                        subkeywords = [x for x in keywords if x in tr_post["content"]]
                        tr_post["keyword"] = subkeywords[0] if len(subkeywords) != 0 else keywords[0]
                        
                        # tokens = cat_tokenizer(tr_post["content"][:500], return_tensors='pt')
                        # output = cat_model(**tokens)
                        # scores = output[0][0].detach().numpy()
                        # scores = expit(scores)
                        # predictions = (scores >= 0.5) * 1
                        # cat_results = list()
                        # for i in range(len(predictions)):
                        #   if predictions[i]:
                        #       try:
                        #           cat_results.append(cat_class_mapping[i])
                        #       except:
                        #           pass
                        # tr_post["categories"] = cat_results
                        
                        # try:
                        #     text = preprocess(tr_post["content"])
                        #     encoded_input = ironizer(text, return_tensors='pt')
                        #     output = mdl_ironizer(**encoded_input)
                        #     scores = output[0][0].detach().numpy()
                        #     scores = softmax(scores)
    
                        #     if(scores[0] < scores[1]):
                        #         isIrony = True
                        #     else:
                        #         isIrony = False
                        #     tr_post["isIrony"] = isIrony
                        # except:
                        #     text = preprocess(tr_post["content"][:500])
                        #     encoded_input = ironizer(text, return_tensors='pt')
                        #     output = mdl_ironizer(**encoded_input)
                        #     scores = output[0][0].detach().numpy()
                        #     scores = softmax(scores)
    
                        #     if(scores[0] < scores[1]):
                        #         isIrony = True
                        #     else:
                        #         isIrony = False
                        #     tr_post["isIrony"] = isIrony
                            
                        # try:
                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"])    
                        # except:
                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"][:500])    
                        # if(len(tr_post["content"]) < 50):
                        #     tr_post["emotions"] = tr_post["emotions"].loc[:2]
                        
                        
                        # try:
                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                        # except:
                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                        tr_post["controversial"] = False
                        # tr_post["toxic"] = self.models["toxicity"][0].predict(self.models["toxicity"][1].transform([tr_post["content"]]))[0]
                        # tr_post["censored"] = (self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["content"]]))[0] or self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["url"]]))[0])
    
                        tr_post["tokenOfInterest"] = list()
                        max_ngram_size = 1
                        deduplication_thresold = 0.9
                        deduplication_algo = 'seqm'
                        windowSize = 1
                        numOfKeywords = 20
                        
                        kw_extractor = yake.KeywordExtractor(lan=tr_post["lang"], n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
                        kx = kw_extractor.extract_keywords(tr_post["content"])
    
                        for kw in kx:
                            if(kw[0] not in tr_post["tokenOfInterest"]):
                                tr_post["tokenOfInterest"].append(kw[0])    
                        
                        tr_post["reference"] = post["subreddit"]
                        tr_post["link"] = "https://www.reddit.com" + post["permalink"]
                        tr_post["is_video"] = post["is_video"] if "is_video" in post else None
                        tr_post["nb_comments"] = 0
                        tr_post["nb_shared"] = 0
                        tr_post["nb_liked"] = 0
                        tr_post["topics"] = list()
                        tr_post["entities"] = list()
                        tr_post["medias"] = list()    
                        tr_post["links"] = list()
    
                        if(tr_post["url"] not in results):
                            #self.send_item(tr_post)
                            #results[tr_post["url"]] = tr_post
                            self.send_doc(tr_post)
                            #Save to DB
                    except Exception as e:
                        # print()
                        # print(target, e)
                        # print()
                        pass
                    
            if(target == "reddit4"):
                
                r = requests.get("https://api.pushshift.io/reddit/search/submission/?subreddit="+"|".join(keywords)+"&after=5m").json()
                #r = requests.get(f'https://api.pushshift.io/reddit/search/comment/?subreddit='+keyword+"&after=5m").json()
                posts = r["data"] 
    
                for post in posts:
                    try:
                        tr_post = dict()
                        
                        tr_post["internal_id"] = post["id"]
                        tr_post["internal_parent_id"] = post["parent_id"] if post["parent_id"] != None else 0
                        
                        tr_post["domainName"] = "reddit.com"
                        tr_post["mediaType"] = "Social_Networks"
                        tr_post["keyword"] = ",".join(self.keywords)
                        tr_post["url"] = "https://www.reddit.com" + post["permalink"]
                        tr_post["author"] = post["author"]
                        tr_post["authorLocation"] = ""
                        tr_post["creationDateTime"] = dt.datetime.fromtimestamp(post["created_utc"],pytz.timezone('UTC'))
                        tr_post["lang"] = detect(text=post["body"].replace("\n",""), low_memory=False)["lang"]
                        if(tr_post["lang"] in self.languages):
                            self.languages[tr_post["lang"]] += 1
                        else:
                            self.languages[tr_post["lang"]] = 1
                        tr_post["title"] = ''
                        tr_post["description"] = ''
                        tr_post["content"] = cleanhtml(post["body"].replace("\n","").replace("'","''"))
                        if(tr_post["content"] in ("","[removed]") and tr_post["title"] != ""):
                            tr_post["content"] = tr_post["title"]
                        
                        subkeywords = [x for x in keywords if x in tr_post["content"]]
                        tr_post["keyword"] = subkeywords[0] if len(subkeywords) != 0 else keywords[0]
                            
                        # tokens = cat_tokenizer(tr_post["content"][:500], return_tensors='pt')
                        # output = cat_model(**tokens)
                        # scores = output[0][0].detach().numpy()
                        # scores = expit(scores)
                        # predictions = (scores >= 0.5) * 1
                        # cat_results = list()
                        # for i in range(len(predictions)):
                        #   if predictions[i]:
                        #       try:
                        #           cat_results.append(cat_class_mapping[i])
                        #       except:
                        #           pass
                        # tr_post["categories"] = cat_results
                        
                        # try:
                        #     text = preprocess(tr_post["content"])
                        #     encoded_input = ironizer(text, return_tensors='pt')
                        #     output = mdl_ironizer(**encoded_input)
                        #     scores = output[0][0].detach().numpy()
                        #     scores = softmax(scores)
    
                        #     if(scores[0] < scores[1]):
                        #         isIrony = True
                        #     else:
                        #         isIrony = False
                        #     tr_post["isIrony"] = isIrony
                        # except:
                        #     text = preprocess(tr_post["content"][:500])
                        #     encoded_input = ironizer(text, return_tensors='pt')
                        #     output = mdl_ironizer(**encoded_input)
                        #     scores = output[0][0].detach().numpy()
                        #     scores = softmax(scores)
    
                        #     if(scores[0] < scores[1]):
                        #         isIrony = True
                        #     else:
                        #         isIrony = False
                        #     tr_post["isIrony"] = isIrony
                            
                        # try:
                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"])    
                        # except:
                        #     tr_post["emotions"] = self.calc_emotions(tr_post["content"][:500])    
                        # if(len(tr_post["content"]) < 50):
                        #     tr_post["emotions"] = tr_post["emotions"].loc[:2]
                        
                        
                        # try:
                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                        # except:
                        #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                        tr_post["controversial"] = False
                        # tr_post["toxic"] = self.models["toxicity"][0].predict(self.models["toxicity"][1].transform([tr_post["content"]]))[0]
                        # tr_post["censored"] = (self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["content"]]))[0] or self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["url"]]))[0])
    
                        tr_post["tokenOfInterest"] = list()
                        max_ngram_size = 1
                        deduplication_thresold = 0.9
                        deduplication_algo = 'seqm'
                        windowSize = 1
                        numOfKeywords = 20
                        
                        kw_extractor = yake.KeywordExtractor(lan=tr_post["lang"], n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
                        kx = kw_extractor.extract_keywords(tr_post["content"])
    
                        for kw in kx:
                            if(kw[0] not in tr_post["tokenOfInterest"]):
                                tr_post["tokenOfInterest"].append(kw[0])    
                        
                        tr_post["reference"] = post["subreddit"]
                        tr_post["link"] = "https://www.reddit.com" + post["permalink"]
                        tr_post["is_video"] = post["is_video"] if "is_video" in post else None
                        tr_post["nb_comments"] = 0
                        tr_post["nb_shared"] = 0
                        tr_post["nb_liked"] = 0
                        tr_post["topics"] = list()
                        tr_post["entities"] = list()
                        tr_post["medias"] = list() 
                        tr_post["links"] = list()
    
                        if(tr_post["url"] not in results):
                            #self.send_item(tr_post)
                            #results[tr_post["url"]] = tr_post
                            self.send_doc(tr_post)
                            #Save to DB
                    except Exception as e:
                        # print()
                        # print(target, e)
                        # print()
                        pass        
                    
            if(target == "instagram"):
    
                pass
                    
            if (target == "twitter1"):
    
                d= dt.datetime.now(pytz.timezone('UTC')) - dt.timedelta(minutes=5)
    
                try:
                    for keyword in keywords:
                    
                        for i, _post in enumerate(snscrape.modules.twitter.TwitterSearchScraper('(from:{} OR about:{}) since_time:{}'.format(keyword, keyword, int(d.timestamp()))).get_items()):
                            post = _post.__dict__
            
                            tr_post = dict()
                            
                            tr_post["internal_id"] = post["id"]
                            tr_post["internal_parent_id"] = post["inReplyToTweetId"] #post["referenced_tweets"][0]["id"] if "referenced_tweets" in post and len(post["referenced_tweet"]) != 0 and post["referenced_tweets"][0]["id"] != None else 0
                        
                            tr_post["keyword"] = keyword
                            tr_post["mediaType"] = "Social_Networks"
                            tr_post["domainName"] = "twitter.com"
                            tr_post["url"] = "https://twitter.com/ExordeLabs/status/{}".format(post["id"])
                            tr_post["author"] = post["user"].displayname
                            tr_post["authorLocation"] = post["user"].location
                            tr_post["creationDateTime"] = post["date"] #parse(post["date"]).replace(tzinfo=pytz.timezone('UTC'))
                            tr_post["lang"] = post["lang"]
                            if(tr_post["lang"] in self.languages):
                                self.languages[tr_post["lang"]] += 1
                            else:
                                self.languages[tr_post["lang"]] = 1
                            tr_post["title"] = '' #post["title"] if "title" in post else None
                            tr_post["description"] = '' #post["annotations"]["description"] if "annotations" in post and "description" in post["annotations"] else ''
                            tr_post["content"] = cleanhtml(post["renderedContent"].replace("\n","").replace("'","''"))
                            if(tr_post["content"] in ("","[removed]") and tr_post["title"] != ""):
                                tr_post["content"] = tr_post["title"]
                            
                            # tokens = cat_tokenizer(tr_post["content"][:500], return_tensors='pt')
                            # output = cat_model(**tokens)
                            # scores = output[0][0].detach().numpy()
                            # scores = expit(scores)
                            # predictions = (scores >= 0.5) * 1
                            # cat_results = list()
                            # for i in range(len(predictions)):
                            #   if predictions[i]:
                            #       try:
                            #           cat_results.append(cat_class_mapping[i])
                            #       except:
                            #           pass
                            # tr_post["categories"] = cat_results
                                                    
                            # try:
                            #     text = preprocess(tr_post["content"])
                            #     encoded_input = ironizer(text, return_tensors='pt')
                            #     output = mdl_ironizer(**encoded_input)
                            #     scores = output[0][0].detach().numpy()
                            #     scores = softmax(scores)
            
                            #     if(scores[0] < scores[1]):
                            #         isIrony = True
                            #     else:
                            #         isIrony = False
                            #     tr_post["isIrony"] = isIrony
                            # except:
                            #     text = preprocess(tr_post["content"][:500])
                            #     encoded_input = ironizer(text, return_tensors='pt')
                            #     output = mdl_ironizer(**encoded_input)
                            #     scores = output[0][0].detach().numpy()
                            #     scores = softmax(scores)
            
                            #     if(scores[0] < scores[1]):
                            #         isIrony = True
                            #     else:
                            #         isIrony = False
                            #     tr_post["isIrony"] = isIrony
                                
                            # try:
                            #     tr_post["emotions"] = self.calc_emotions(tr_post["content"])    
                            # except:
                            #     tr_post["emotions"] = self.calc_emotions(tr_post["content"][:500])    
                            # if(len(tr_post["content"]) < 50):
                            #     tr_post["emotions"] = tr_post["emotions"].loc[:2]
                            
                            
                            # try:
                            #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                            # except:
                            #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                            tr_post["controversial"] = False
                            # tr_post["toxic"] = self.models["toxicity"][0].predict(self.models["toxicity"][1].transform([tr_post["content"]]))[0]
                            # tr_post["censored"] = (self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["content"]]))[0] or self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["url"]]))[0])
            
                            tr_post["tokenOfInterest"] = list()
                            max_ngram_size = 1
                            deduplication_thresold = 0.9
                            deduplication_algo = 'seqm'
                            windowSize = 1
                            numOfKeywords = 20
                            
                            kw_extractor = yake.KeywordExtractor(lan=tr_post["lang"], n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
                            kx = kw_extractor.extract_keywords(tr_post["content"])
            
                            for kw in kx:
                                if(kw[0] not in tr_post["tokenOfInterest"]):
                                    tr_post["tokenOfInterest"].append(kw[0])    
                
                
                            tr_post["reference"] = ''
                            tr_post["links"] = list()
                            if("outlinks" in post and type(post["outlinks"]) != None):
                                try:
                                    for j in range(len(post["outlinks"])):
                                        tr_post["links"].append(post["outlinks"][i])
                                except:
                                    pass
                            if("tcooutlinks" in post and type(post["tcooutlinks"]) != None):
                                try:
                                    for j in range(len(post["tcooutlinks"])):
                                        tr_post["links"].append(post["tcooutlinks"][i])
                                except:
                                    pass
                            tr_post["is_video"] = None #post["is_video"] if "is_video" in post else ''
                            tr_post["nb_comments"] = post["replyCount"]
                            tr_post["nb_shared"] = post["retweetCount"]
                            tr_post["nb_liked"] = post["likeCount"]
                            tr_post["topics"] = post["hashtags"]
                            tr_post["entities"] = list()
                            tr_post["medias"] = list()
            
                            if("context_annotation" in post):
                                for lvl0 in post["context_annotations"]:
                                    
                                    tr_post["topics"].append({"superclass":lvl0["domain"]["name"],
                                                              "superdesc":lvl0["domain"]["description"],
                                                              "class":lvl0["entity"]["name"],
                                                              "desc":lvl0["domain"]["description"],})
                            
                            tr_post["mentions"] = list()
                            if("entities" in post):
                                for entType in post["entities"]:
                                    
                                    if(entType == "hashtags"):
                                        for i in range(len(post["entities"]["hashtags"])):
                                            tr_post["mentions"].append(post["entities"]["hashtags"][i]["tag"])
                                            
                                    if(entType == "mentions"):
                                        for i in range(len(post["entities"]["mentions"])):
                                            tr_post["mentions"].append(post["entities"]["mentions"][i]["username"])
                
                                    if(entType == "urls"):
                                        for i in range(len(post["entities"]["urls"])):
                                            tr_post["links"].append(post["entities"]["urls"][i]["expanded_url"])
                                            
                                    if(entType == "unwound_url"):
                                        tr_post["links"].append(post["entities"]["unwound_url"])
                                            
                                    if(entType == "annotations"):
                                        for i in range(len(post["entities"]["annotations"])):
                                            annot = post["entities"]["annotations"][i]
                                            neo_annot = {"type":annot["type"],
                                                         "name":annot["normalized_text"],
                                                         "proba":annot["probability"]}
                                            tr_post["entities"].append(neo_annot)
                                            
                                    if(entType == "images"):
                                        for i in range(len(post["entities"]["images"])):
                                            img = post["entities"]["urls"][i]
                                            neo_img = {"type":"img",
                                                       "url":img["url"]}
                                            tr_post["medias"].append(neo_img)
                            
                            
                            if(tr_post["url"] not in results):
                                #self.send_item(tr_post)
                                #results[tr_post["url"]] = tr_post
                                self.send_doc(tr_post)
                                
                except Exception as e:
                    # print()
                    # print(target, e)
                    # print()
                    pass
                
            if (target == "twitter2"):
            
                try:
                    #headers={"Authorization": "Bearer "+random.choice(bearers)}
                    d= dt.datetime.now(pytz.timezone('UTC')) - dt.timedelta(minutes=5)
    
                    for keyword in keywords:
        
                        postList = [_post.__dict__ for i, _post in enumerate(snscrape.modules.twitter.TwitterHashtagScraper(keyword + ' since_time:{}'.format(int(d.timestamp()))).get_items()) if _post.__dict__["date"].timestamp() >= d.timestamp()]                
        
                        #for i, _post in enumerate(snscrape.modules.twitter.TwitterHashtagScraper(keyword + ' since_time:{}'.format(int(d.timestamp()))).get_items()):
                        for post in postList:
                            #post = _post.__dict__
                            
                            if(post["date"].timestamp() > d.timestamp()):
            
                                tr_post = dict()
                                
                                tr_post["internal_id"] = post["id"]
                                tr_post["internal_parent_id"] = post["inReplyToTweetId"] #post["referenced_tweets"][0]["id"] if "referenced_tweets" in post and len(post["referenced_tweet"]) != 0 and post["referenced_tweets"][0]["id"] != None else 0
                            
                                tr_post["keyword"] = keyword
                                tr_post["mediaType"] = "Social_Networks"
                                tr_post["domainName"] = "twitter.com"
                                tr_post["url"] = "https://twitter.com/ExordeLabs/status/{}".format(post["id"])
                                tr_post["author"] = post["user"].displayname
                                tr_post["authorLocation"] = post["user"].location
                                tr_post["creationDateTime"] = post["date"] #parse(post["date"]).replace(tzinfo=pytz.timezone('UTC'))
                                tr_post["lang"] = post["lang"]
                                if(tr_post["lang"] in self.languages):
                                    self.languages[tr_post["lang"]] += 1
                                else:
                                    self.languages[tr_post["lang"]] = 1
                                tr_post["title"] = '' #post["title"] if "title" in post else None
                                tr_post["description"] = '' #post["annotations"]["description"] if "annotations" in post and "description" in post["annotations"] else ''
                                tr_post["content"] = cleanhtml(post["renderedContent"].replace("\n","").replace("'","''"))
                                if(tr_post["content"] in ("","[removed]") and tr_post["title"] != ""):
                                    tr_post["content"] = tr_post["title"]
                                
                                # tokens = cat_tokenizer(tr_post["content"][:500], return_tensors='pt')
                                # output = cat_model(**tokens)
                                # scores = output[0][0].detach().numpy()
                                # scores = expit(scores)
                                # predictions = (scores >= 0.5) * 1
                                # cat_results = list()
                                # for i in range(len(predictions)):
                                #   if predictions[i]:
                                #       try:
                                #           cat_results.append(cat_class_mapping[i])
                                #       except:
                                #           pass
                                # tr_post["categories"] = cat_results
                                    
                                # try:
                                #     text = preprocess(tr_post["content"])
                                #     encoded_input = ironizer(text, return_tensors='pt')
                                #     output = mdl_ironizer(**encoded_input)
                                #     scores = output[0][0].detach().numpy()
                                #     scores = softmax(scores)
            
                                #     if(scores[0] < scores[1]):
                                #         isIrony = True
                                #     else:
                                #         isIrony = False
                                #     tr_post["isIrony"] = isIrony
                                # except:
                                #     text = preprocess(tr_post["content"][:500])
                                #     encoded_input = ironizer(text, return_tensors='pt')
                                #     output = mdl_ironizer(**encoded_input)
                                #     scores = output[0][0].detach().numpy()
                                #     scores = softmax(scores)
            
                                #     if(scores[0] < scores[1]):
                                #         isIrony = True
                                #     else:
                                #         isIrony = False
                                #     tr_post["isIrony"] = isIrony
                                    
                                # try:
                                #     tr_post["emotions"] = self.calc_emotions(tr_post["content"])    
                                # except:
                                #     tr_post["emotions"] = self.calc_emotions(tr_post["content"][:500])    
                                # if(len(tr_post["content"]) < 50):
                                #     tr_post["emotions"] = tr_post["emotions"].loc[:2]
                                
                                
                                # try:
                                #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                                # except:
                                #     tr_post["sentiment"] = tr_post["emotions"].loc[0, "label"]
                                tr_post["controversial"] = False
                                # tr_post["toxic"] = self.models["toxicity"][0].predict(self.models["toxicity"][1].transform([tr_post["content"]]))[0]
                                # tr_post["censored"] = (self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["content"]]))[0] or self.models["censoring"][0].predict(self.models["censoring"][1].transform([tr_post["url"]]))[0])
            
                                tr_post["tokenOfInterest"] = list()
                                max_ngram_size = 1
                                deduplication_thresold = 0.9
                                deduplication_algo = 'seqm'
                                windowSize = 1
                                numOfKeywords = 20
                                
                                kw_extractor = yake.KeywordExtractor(lan=tr_post["lang"], n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
                                kx = kw_extractor.extract_keywords(tr_post["content"])
            
                                for kw in kx:
                                    if(kw[0] not in tr_post["tokenOfInterest"]):
                                        tr_post["tokenOfInterest"].append(kw[0])    
                                
            
                                tr_post["reference"] = ''
                                tr_post["links"] = list()
                                if("outlinks" in post and type(post["outlinks"]) != None):
                                    try:
                                        for j in range(len(post["outlinks"])):
                                            tr_post["links"].append(post["outlinks"][i])
                                    except:
                                        pass
                                if("tcooutlinks" in post and type(post["tcooutlinks"]) != None):
                                    try:
                                        for j in range(len(post["tcooutlinks"])):
                                            tr_post["links"].append(post["tcooutlinks"][i])
                                    except:
                                        pass
                                tr_post["is_video"] = None 
                                tr_post["nb_comments"] = post["replyCount"]
                                tr_post["nb_shared"] = post["retweetCount"]
                                tr_post["nb_liked"] = post["likeCount"]
                                tr_post["topics"] = post["hashtags"]
                                tr_post["entities"] = list()
                                tr_post["medias"] = list()
                                
                                if("context_annotation" in post):
                                    for lvl0 in post["context_annotations"]:
                                        
                                        tr_post["topics"].append({"superclass":lvl0["domain"]["name"],
                                                                  "superdesc":lvl0["domain"]["description"],
                                                                  "class":lvl0["entity"]["name"],
                                                                  "desc":lvl0["domain"]["description"],})
                                
                                tr_post["mentions"] = list()
                                if("entities" in post):
                                    for entType in post["entities"]:
                                        
                                        if(entType == "hashtags"):
                                            for i in range(len(post["entities"]["hashtags"])):
                                                tr_post["mentions"].append(post["entities"]["hashtags"][i]["tag"])
                                                
                                        if(entType == "mentions"):
                                            for i in range(len(post["entities"]["mentions"])):
                                                tr_post["mentions"].append(post["entities"]["mentions"][i]["username"])
                    
                                        if(entType == "urls"):
                                            for i in range(len(post["entities"]["urls"])):
                                                tr_post["links"].append(post["entities"]["urls"][i]["expanded_url"])
                                                
                                        if(entType == "unwound_url"):
                                            tr_post["links"].append(post["entities"]["unwound_url"])
                                                
                                        if(entType == "annotations"):
                                            for i in range(len(post["entities"]["annotations"])):
                                                annot = post["entities"]["annotations"][i]
                                                neo_annot = {"type":annot["type"],
                                                             "name":annot["normalized_text"],
                                                             "proba":annot["probability"]}
                                                tr_post["entities"].append(neo_annot)
                                                
                                        if(entType == "images"):
                                            for i in range(len(post["entities"]["images"])):
                                                img = post["entities"]["urls"][i]
                                                neo_img = {"type":"img",
                                                           "url":img["url"]}
                                                tr_post["medias"].append(neo_img)
                                
                                
                                if(tr_post["url"] not in results):
                                    #self.send_item(tr_post)
                                    self.send_doc(tr_post)
                                    #results[tr_post["url"]] = tr_post
                except Exception as e:
                    # print()
                    # print(target, e)
                    # print()
                    pass
                
            sys.exit()
        except Exception as e:
            #print("scraping", e)
            sys.exit()
        
    def manage_sending(self):

        _contract = self.app.cm.instantiateContract("ConfigRegistry")        

        while True:

            try:                

                try:
                    batchSize = int(_contract.functions.get("_ModuleMinSpotBatchSize").call())
                    self.lastBatchSize = batchSize
                except Exception as e:
                    #print("Couldn't get batch size")
                    #print( e)
                    batchSize = self.lastBatchSize

                if(len(self.pendingBlocks) >= batchSize):
                    
                    #print([x["item"]["DomainName"] for x in self.pendingBlocks[:batchSize]])
                        tmp = self.pendingBlocks[:batchSize]
                        
                        
                        res = None
                        
                        while res == None:
                            try:
                                res = filebase_upload(json.dumps({"Content":tmp}, indent=4, sort_keys=True, default=str), self.app.cm.instantiateContract("ConfigRegistry").functions.get("SpotBucket").call())
                                time.sleep(7.5)
                                break
                            except:
                                res = None
                        domNames = [x["item"]["DomainName"] for x in self.pendingBlocks[:batchSize]][0]
                        # res = filebase_upload(json.dumps({"Content":self.pendingBlocks[:batchSize]}, indent=4, sort_keys=True, default=str), self.app.cm.instantiateContract("ConfigRegistry").functions.get("SpotBucket").call())
                        #print("Res:", res)
                        if(res != None):
                            
                            #print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"SCRAPER", "manage_sending", "SPOTDATA")) 
                            #print("Scraper sending file", res)
                            
                            contract = self.app.cm.instantiateContract("DataSpotting")
                            increment_tx = contract.functions.SpotData([res], [domNames], batchSize, 'Hi Bob!').buildTransaction(
                            {
                                'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
                                'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
                                'gasPrice': w3.eth.gas_price,
                                'gas':200000000
                            })
                            self.app.tm.waitingRoom.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))
                            #print("File sent", res)
                        
                        self.pendingBlocks = self.pendingBlocks[batchSize:]
                    
            except Exception as e:
                #print("manage_sending", e)
                pass
            
                
                
            
    def send_doc(self, doc):

        try:
            document = dict()
            
            tr_item = dict()
            tr_item["CreationDateTime"] = doc["creationDateTime"]
            tr_item["Language"] = doc["lang"]
            tr_item["Url"] = doc["url"]
            tr_item["Author"] = doc["author"]
            tr_item["Title"] = doc["title"]
            tr_item["Description"] = doc["description"].replace("'", "''")
            tr_item["Content"] = doc["content"].replace('"','\"')
            #tr_item["Sentiment"] = doc["sentiment"]
            tr_item["Controversial"] = doc["controversial"]
            # tr_item["Toxic"] = doc["toxic"]
            # tr_item["Censored"] = doc["censored"]
            tr_item["Reference"] = doc["reference"]
            tr_item["nbComments"] = doc["nb_comments"]
            tr_item["nbShared"] = doc["nb_shared"]
            tr_item["nbLiked"] = doc["nb_liked"]
            tr_item["DomainName"] = doc["domainName"]
            #tr_item["isIrony"] = doc["isIrony"]
            tr_item["internal_id"] = doc["internal_id"]
            tr_item["internal_parent_id"] = doc["internal_parent_id"]
            tr_item["mediaType"] = doc["mediaType"]
            
            
            document["item"] = tr_item
            document["keyword"] = doc["keyword"]
            #document["categories"] = doc["categories"]
            document["links"] = doc["links"]
            document["entities"] = doc["entities"]
            document["medias"] = doc["medias"]
            document["tokenOfInterest"] = doc["tokenOfInterest"]
            
            if(self.app.localconfig["ExordeApp"]["SendCountryInfo"] == True):
                document["spotterCountry"] = self.app.userCountry
            else:
                document["spotterCountry"] = ""
                
            self.pendingBlocks.append(document)
            self.nbItems += 1
            
        except Exception as e:
            #print("send_doc", e)
            pass
        #document["emotions"] = doc["emotions"]
        
        #print("BucketName:", self.app.cm.instantiateContract("ConfigRegistry").functions.get("SpotBucket").call())
        # res = filebase_upload(json.dumps({"Content":document}, indent=4, sort_keys=True, default=str), self.app.cm.instantiateContract("ConfigRegistry").functions.get("SpotBucket").call())

        # if(res != None):
            
        #     contract = self.app.cm.instantiateContract("DataSpotting")
        #     increment_tx = contract.functions.SpotData([res], [doc["domainName"]], 1, 'Hi Bob!').buildTransaction(
        #     {
        #         'nonce': w3.eth.get_transaction_count(self.app.localconfig["ExordeApp"]["ERCAddress"]),
        #         'from': self.app.localconfig["ExordeApp"]["ERCAddress"],
        #         'gasPrice': w3.eth.gas_price,
        #         'gas':200000000
        #     })
        #     self.app.tm.waitingRoom.put((increment_tx, self.app.localconfig["ExordeApp"]["ERCAddress"], self.app.pKey))
            
#print("[{}]\t{}\t{}\t\t{}".format(dt.datetime.now(),"SCRAPER", "import", "LOADED")) 