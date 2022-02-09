import urllib.request
import urllib.parse
import urllib.error
import urllib.response
import urllib.robotparser
import os
from flask import request
import bs4
import re
import time
from threading import Thread
import math
import copy


def askURL(url):
    # print(url)

    my_headers = [
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    ]
    # headers = {
    #     "User-Agent": random.choice(my_headers)
    # }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
    }

    request = urllib.request.Request(url, headers=headers)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        html = ""
        # print(e)
        # if hasattr(e, "code"):
        #     print(e)
        # if hasattr(e, "reason"):
        #     print(e.reason)
    return html


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def merge(PicSrcParts):
    while len(PicSrcParts[0]):
        for item in PicSrcParts:
            try:
                PicSrcs.append(item.pop(0))
            except:
                pass


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
    treads = [[], [], [], [], [], [], [], [], [],
              [], [], [], [], [], [], [], [], [], [], []]
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
    try:
        pic = urllib.request.urlopen(url).read()
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


def prepare(baseurl, mode):
    global Sum
    print("正在读取作品第1页及相关信息...")
    html = askURL(baseurl+'?p=0')
    while html == "":
        print("读取失败，开始重新读取")
        askURL(baseurl+'?p=0')
    print("读取成功！")
    Sum = getSum(html)
    Name = getName(html)
    Name = validateTitle(Name)
    Pages = int(math.ceil(Sum/40))
    print("作品名:"+Name)
    print("共"+str(Sum)+"张")
    print("共"+str(Pages)+"页")
    try:
        os.makedirs(Name)
        print("创建文件夹成功!")
    except:
        pass

    Links = getLinks(html)
    for i in range(Pages-1):
        print("开始读取第"+str(i+2)+"页")
        html = askURL(baseurl+'?p='+str(i+1))
        while html == "":
            print("读取失败，开始重新读取")
            askURL(baseurl+'?p='+str(i+1))
        Links = Links+getLinks(html)
    if mode == 2:
        beginCatch(Links, Name)
    if mode == 1:
        while True:
            index = input("请输入编号：")
            index = int(index)
            if index == 0 or index > Sum:
                return
            getOne(Links, index, Name+"\\Pic"+str(index))


def beginCatch(Links, Name):

    print("初步读取完成，即将开始下载图片")
    print("开始下载图片")
    print("进 ↓                    ↓")
    print("度 ↑", end="")
    beginGet(Links, Name)

    print("↑下载完成")
    print("下载失败的文件数：", len(wrongPic))
    for name in wrongPic.values():
        print(name, end=" ")
    while len(wrongPic):
        a = input("\n是否重新下载错误的图片？y/n ")
        if a == 'y':
            reDownload(Links)
            print("下载失败的文件数：", len(wrongPic))
            for name in wrongPic.values():
                print(name, end=" ")
        else:
            return


def updateProgress():
    print("█", end='')


lastprogress = 0
Sum = 0
PicSrcs = []
finishednum = 0
wrongPic = {}


def main():
    print("使用前提醒，需先挂上梯子，当自己的浏览器可以访问https://e-hentai.org/时才可使用，当前版本只负责提供快速下载，至于需要下什么样的资源需用户自行选择（")
    baseurl = "https://e-hentai.org/g/2135909/efc47ee82e/"
    url = input("请输入需要下载的作品链接，如 "+baseurl+"，必须是该网站的网址(直接回车将默认)")
    if url != '':
        baseurl = url
    # getLinks(baseurl)
    mode = input("请选择模式：1.按图片编号下载 2.全部下载\n")
    mode = int(mode)
    prepare(baseurl, mode)
    # print(PicSrcs)


findLink = re.compile(r'<a href="(.*?)">')
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)
findPages = re.compile(r'<td class="gdt2">(\d*?) pages</td>', re.S)
findName = re.compile(r'<h1 id="gn">(.*?)</h1>')
if(__name__ == "__main__"):
    main()
