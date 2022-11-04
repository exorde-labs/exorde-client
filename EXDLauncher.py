# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 10:06:40 2022

@author: flore
"""

import boto3
from collections import Counter, deque
import csv
import datetime as dt
from datetime import timezone
from dateutil.parser import parse
from eth_account import Account
import facebook_scraper  as fb
from functools import partial
from ftlangdetect import detect
from geopy.geocoders import Nominatim
import html
from idlelib.tooltip import Hovertip
from iso639 import languages
import itertools
import json
import keyboard
import libcloud
from lxml.html.clean import Cleaner
import numpy as np
from operator import itemgetter
import os
import pandas as pd
from pathlib import Path
import pickle
from PIL import Image, ImageTk, ImageFile
from plyer import notification
import pytz
from queue import Queue
import random
import re
import requests
from requests_html import HTML
from requests_html import HTMLSession
from scipy.special import softmax, expit
import shutils
import snscrape.modules
import string
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tldextract
import tqdm
# import transformers
# from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig, TFAutoModelForSequenceClassification
import unicodedata
import urllib.request
import warnings
import web3
from web3 import Web3, HTTPProvider
import webbrowser
import yake


# import boto3
# from collections import Counter, deque
# import datetime as dt
# from datetime import timezone
# from eth_account import Account
# import facebook_scraper  as fb
# from geopy.geocoders import Nominatim
# import html
# from idlelib.tooltip import Hovertip
# import itertools
# import json
# from langdetect import detect
# import libcloud
# from lxml.html.clean import Cleaner
# import numpy as np
# import os
# import pandas as pd
# from pathlib import Path
# import pickle
# from PIL import Image, ImageTk, ImageFile
# import pytz
# from queue import Queue
# import random
# import re
# import requests
# from requests_html import HTML
# from requests_html import HTMLSession
# import shutils
# import sklearn
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import PassiveAggressiveClassifier
# from sklearn.metrics import accuracy_score, confusion_matrix
# from sklearn.naive_bayes import MultinomialNB
# import snscrape.modules
# import string
# import threading
# import time
# import tkinter as tk
# from tkinter import ttk
# import tkinter.messagebox
# import tldextract
# import unicodedata
# import warnings
# import web3
# from web3 import Web3, HTTPProvider
# import webbrowser
# import yake


try:
    launcher = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/module_files/Launcher.py").text        # PROD
    #launcher = requests.get("https://raw.githubusercontent.com/exorde-labs/LinuxClient/main/Launcher_server.py?token=GHSAT0AAAAAABX6NEFILDFYOFPFXZ6BIVKWYYWB3TQ").text # SERVER
    #launcher = requests.get("https://raw.githubusercontent.com/MathiasExorde/TestnetProtocol-staging/main/module_files/Launcher_test.py").text    # TEST
    exec(launcher)
except Exception as e:
    tk.messagebox("Initialization error", e)
    

