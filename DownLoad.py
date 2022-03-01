from tempfile import tempdir
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
import threading
import math
import copy
import requests
import random
import numpy as np
from tkinter import *


# 获取代理

proxy = {}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
}


def get_proxy_():
    global proxy
    proxies = urllib.request.getproxies()  # 获取代理
    if len(proxies) != 0:
        proxy = {
            "http": proxies['http'],
            "https": proxies['https'].replace('https', 'http')
        }
        return proxy

    else:
        return None

# 爬取网页


def askURL(url):
    global proxy
    global headers

    try:
        response = requests.get(url, proxies=proxy, headers=headers)
        html = ""
        response.encoding = 'utf-8'
        html = repr(response.text)
    except:
        html = ""
    return html


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def getSrc(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    for item in soup.find_all('div', id="i3"):
        item = str(item)
        src = re.findall(findImgSrc, item)[0]
        return src


def getOne(Links, index, name):
    link = Links[index-1]
    print('link = '+link)
    html = askURL(link)
    if html == "":
        wrongPic[str(index)] = name
    else:
        src = getSrc(html)
        print('src = '+src)
        TurnPic(src, index, name)


def newTurnPic(url, index, name):
    global proxy
    global headers
    try:
        response = requests.get(url, proxies=proxy, headers=headers)
        pic = response.content
        with open('.\\'+name+'.jpg', 'wb') as f:
            f.write(pic)
    except:
        return 'wrong'


def newgetPart(task, begin):
    print('begin', begin)
    Links = task['links']
    name = task['name']
    wrong = []
    i = 0
    # print(len(Links))
    for link in Links[begin::20]:
        # print(begin, i)
        html = askURL(link)
        if html == "":
            wrong.append(begin+1+20*i)

        else:
            src = getSrc(html)
            newTurnPic(src, begin+1+20*i, name+'\\'+'Pic'+str(begin+1+20*i))
        task['wrong'] = wrong

        task['finished'] += 1
        # print(begin, task['finished'])
        i += 1


def getPart(Links, name, begin):
    global finishednum
    global lastprogress
    global Sum
    i = 0
    for link in Links[begin::20]:
        html = askURL(link)
        if html == "":
            wrongPic[str(begin+1+20*i)] = name+'\\'+'Pic'+str(begin+1+20*i)

        else:
            src = getSrc(html)
            TurnPic(src, begin+1+20*i, name+'\\'+'Pic'+str(begin+1+20*i))
        finishednum = finishednum+1
        if Sum != 0:
            nowprogress = int(math.floor(20*finishednum/Sum))
        for j in range(nowprogress-lastprogress):
            print("█", end="")
        lastprogress = nowprogress
        i = i+1


def beginGet(Links, name):
    treads = [[] for i in range(20)]
    for i in range(20):
        treads[i] = Thread(target=getPart, args=(
            Links, name, i))
    for i in range(20):
        treads[i].start()
    for i in range(20):
        treads[i].join()


def getLinks(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    Links = []
    for item in soup.find_all('div', class_="gdtm"):
        item = str(item)
        link = re.findall(findLink, item)[0]
        Links.append(link)

    return Links


def TurnPic(url, index, name):
    global proxy
    global headers
    try:
        response = requests.get(url, proxies=proxy, headers=headers)
        pic = response.content
        with open('.\\'+name+'.jpg', 'wb') as f:
            f.write(pic)
    except:
        wrongPic[str(index)] = name


def getSum(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    for item in soup.find_all('div', id="gdd"):
        item = str(item)
        Sum = re.findall(findPages, item)[0]
        Sum = int(Sum)
        return Sum


def getName(html):
    global findName
    soup = bs4.BeautifulSoup(html, "html.parser")
    for item in soup.find_all('div', id="gd2"):
        item = str(item)
        Name = re.findall(findName, item)[0]
        return Name


def reDownload(Links):
    tempPic = copy.deepcopy(wrongPic)
    for key, name in tempPic.items():
        del wrongPic[key]
        index = int(key)
        getOne(Links, index, name)


def getImgLinks(baseurl, task, Name=''):
    # global Sum
    Links = task['links']
    get_proxy_()
    print("正在读取作品第1页及相关信息...")
    html = askURL(baseurl+'?p=0')
    while html == "":
        # print("读取失败，开始重新读取")
        askURL(baseurl+'?p=0')
    # print("读取成功！")
    Sum = getSum(html)
    Pages = int(math.ceil(Sum/40))
    if Name == '':
        Name = getName(html)
        Name = validateTitle(Name)
        task['name'] = Name

    print("作品名:"+Name)
    try:
        os.makedirs(Name)
        print("创建文件夹成功!")
    except:
        print("创建文件夹失败!")
        pass

    templinks = getLinks(html)
    for i in range(Pages-1):
        # print("开始读取第"+str(i+2)+"页")
        html = askURL(baseurl+'?p='+str(i+1))
        while html == "":
            # print("读取失败，开始重新读取")
            askURL(baseurl+'?p='+str(i+1))
        templinks = templinks+getLinks(html)
    for link in templinks:
        Links.append(link)
    task['state'] = 'prepared'
    print("pr")
    # beginCatch(Links, Name)


def beginCatch(Links, Name):
    beginGet(Links, Name)
    print("下载失败的文件数：", len(wrongPic))
    for name in wrongPic.values():
        print(name, end=" ")
    while len(wrongPic):
        reDownload(Links)
        print("下载失败的文件数：", len(wrongPic))
        for name in wrongPic.values():
            print(name, end=" ")


lastprogress = 0
# Sum = 0
PicSrcs = []
finishednum = 0
wrongPic = {}

findLink = re.compile(r'<a href="(.*?)">')
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)
findPages = re.compile(r'<td class="gdt2">(\d*?) pages</td>', re.S)
findName = re.compile(r'<h1 id="gn">(.*?)</h1>')
