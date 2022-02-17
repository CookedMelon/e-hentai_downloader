import urllib.request
import urllib.parse
import urllib.error
import urllib.response
import urllib.robotparser
import os
import bs4
import re
import time
from threading import Thread
import math
import copy
import requests
import random
import numpy as np
from tkinter import *
# 获取代理


def get_proxy_():
    proxies = urllib.request.getproxies()  # 获取代理
    if len(proxies) != 0:
        proxy = {
            "http": proxies['http'],
            "https": proxies['https'].replace('https', 'http')
        }
        return proxy

    else:
        return None


def askURL(url):
    # headers = {
    #     "User-Agent": random.choice(my_headers)
    # }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
    }

    html = ""
    try:
        proxies = get_proxy_()
        print(proxies)
        response = requests.get(url, proxies=proxies, headers=headers)
        response.encoding = 'utf-8'
        html = repr(response.text)
    except:
        html = ""
        # print(e)
        # if hasattr(e, "code"):
        #     print(e)
        # if hasattr(e, "reason"):
        #     print(e.reason)
    return html
