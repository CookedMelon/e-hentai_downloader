from tkinter import *
import tkinter as tk
import time
import requests
import io
from PIL import Image, ImageTk
import urllib.request
import GetHtml as GH
import DownLoad as DL
import bs4
import re
from threading import Thread
import threading
import os
import ctypes

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


get_proxy_()


def ask5URL(url):
    print(url)
    html = ''
    i = 0
    while i < 5 and html == '':
        i += 1
        html = GH.askURL(url)
    return html


class StoppableDownloadThread(threading.Thread):
    def __init__(self,  *args, **kwargs):
        super(StoppableDownloadThread, self).__init__(*args, **kwargs)
        self.args = kwargs['args']
        # print(self.task, self.begin)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        task = self.args['task']
        begin = self.args['begin']
        Links = task['links']
        name = task['name']
        wrong = []
        i = 0
        for link in Links[begin::20]:
            if self.stopped():
                wrong.append(begin+1+20*i)
            else:
                html = ask5URL(link)
                if html == '':
                    print("请求失败，链接：", link)
                if html == "":
                    wrong.append(begin+1+20*i)
                else:
                    src = DL.getSrc(html)
                    message = DL.newTurnPic(src, begin+1+20*i, name +
                                            '\\'+'Pic'+str(begin+1+20*i))
                    if message == 'wrong':
                        wrong.append(begin+1+20*i)
                task['wrong'] = wrong
                task['finished'] += 1
                # print(begin, task['finished'])
            i += 1


class StoppableGetallThread(threading.Thread):
    def __init__(self,  *args, **kwargs):
        super(StoppableGetallThread, self).__init__(*args, **kwargs)
        self.args = kwargs['args']
        # print(self.task, self.begin)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        print("开始")
        searched = self.args['str']
        root = self.args['root']
        for i in range(10):
            workslist = []
            if self.stopped():
                break
            else:
                baseurl = 'https://e-hentai.org/?page='+str(i)
                if searched != '':
                    baseurl += '&f_search='+searched

                html = ask5URL(baseurl)
                if html == '':
                    print("请求失败，链接：", baseurl)
                soup = bs4.BeautifulSoup(html, "html.parser")
                for item in soup.find_all('table', class_="itg gltc"):
                    for item1 in item.find_all('tr')[1:]:
                        work = {}
                        for Type in item1.find_all('div', class_='cn ct2'):
                            work['type'] = 'Doujinshi'
                        for Type in item1.find_all('div', class_='cn ct3'):
                            work['type'] = 'Manga'
                        for Type in item1.find_all('div', class_='cn ct4'):
                            work['type'] = 'Artist CG'
                        for Type in item1.find_all('div', class_='cn ct5'):
                            work['type'] = 'Game CG'
                        for Type in item1.find_all('div', class_='cn cta'):
                            work['type'] = 'Western'
                        for Type in item1.find_all('div', class_='cn ct9'):
                            work['type'] = 'Non-H'
                        for Type in item1.find_all('div', class_='cn ct6'):
                            work['type'] = 'Image Set'
                        for Type in item1.find_all('div', class_='cn ct7'):
                            work['type'] = 'Cosplay'
                        for Type in item1.find_all('div', class_='cn ct8'):
                            work['type'] = 'Asian Porn'
                        for Type in item1.find_all('div', class_='cn ct1'):
                            work['type'] = 'Misc'
                        for Name in item1.find_all('div', class_='glink'):
                            work['name'] = Name.string
                        for Page in item1.find_all('td', class_='gl4c glhide'):
                            try:
                                p = Page.find_all('div')
                                work['page'] = int(p[1].string.split(' ')[0])
                            except:
                                pass
                        for Star in item1.find_all('div', class_='ir'):
                            try:
                                S = re.findall("\d+", Star.attrs['style'])[: 2]
                                star = 5-int(S[0])/16-(int(S[1])-1)/40
                                work['star'] = star
                            except:
                                work['star'] = 0.0
                        for Link in item1.find_all('td', class_='gl3c glname'):
                            if Link.find('a').attrs.__contains__('href'):
                                link = Link.find('a').attrs['href']
                                work['link'] = link
                        for Imgsrc in item1.find_all('div', class_='glthumb'):
                            for img in Imgsrc.find_all('img'):
                                if img.attrs. __contains__('data-src'):
                                    work['imgsrc'] = img.attrs['data-src']
                                elif img.attrs. __contains__('src'):
                                    work['imgsrc'] = img.attrs['src']
                                if work != {}:
                                    workslist.append(work)
            if self.stopped() or len(workslist) == 0:
                break
            else:
                root.allworks += workslist
                # print(root.allworks)
            time.sleep(3)
        self.stop()
        print("结束")


class MY_GUI():
    imgs = []

    allworks = []
    worksList = []
    tasklist = []

    nowloc = 0
    beginindex = 0
    step = 20
    allLabels = [{} for i in range(step)]

    def __init__(self, init_window_name):
        user32 = ctypes.windll.user32
        self.totalwidth = user32.GetSystemMetrics(0)
        self.totalheight = user32.GetSystemMetrics(1)
        self.init_window_name = init_window_name
        self.nowpage = 0
        self.homewidth = (self.totalwidth*3)//4
        self.homeheight = (self.totalheight*3)//4
        self.directdownloadwidth = self.totalwidth//6
        self.directdownloadheight = 20
        self.downlistwidth = self.totalwidth//6
        self.downlistheight = self.totalwidth//4
        self.tempPicWidth = self.totalwidth//6
        self.tempPicHeight = self.totalwidth//4
        self.nowloc = 0
        self.nowlabelnum = 0
        self.beginindex = 0
        self.step = 20
        self.allLabels = [{} for i in range(self.step)]
        # mode负责当前筛选条件，starleast为最少星数，type为允许的种类,page1为张数上限,page2为张数下限
        self.mode = {'starleast': 4, 'type': ['Doujinshi', 'Manga', 'Artist CG',
                                              'Game CG', 'Western', 'Non-H', 'Image Set',
                                              'Cosplay', 'Asian Porn', 'Misc'],
                     'page1': 0, 'page2': 10000}
        #  存放删选后的作品
        self.worksList = []
        #  存放所有作品
        self.allworks = []
        # self.is_catching_more = False
        # self.break_get_more = False

    def set_init_windows(self):
        self.init_window_name.title("e站爬取")
        self.init_window_name.bind("<Button-1>", self.callback)
        self.init_window_name.geometry(
            str(self.totalwidth)+'x'+str(self.totalheight)+'+0+0')
        self.home_data_label = Label(
            self.init_window_name, text="首页")
        self.home_data_label.grid(row=1, column=0)
        self.star_label = Label(
            self.init_window_name, text="最低星数:")
        self.star_label.grid(row=1, column=1)
        self.star_entry_var = StringVar()
        # 注意，输入框就是单行文本，它是没有height属性的
        self.star_entry = Entry(self.init_window_name, width=5,
                                textvariable=self.star_entry_var)
        self.star_entry.bind('<Return>', self.refresh_star)
        self.star_entry.grid(row=1, column=2)
        self.star_entry_var.set(str(self.mode['starleast']))

        self.page1_label = Label(
            self.init_window_name, text="最少页数:")
        self.page1_label.grid(row=1, column=3)
        self.page1_entry_var = StringVar()
        # 注意，输入框就是单行文本，它是没有height属性的
        self.page1_entry = Entry(self.init_window_name, width=5,
                                 textvariable=self.page1_entry_var)
        self.page1_entry.bind('<Return>', self.refresh_page1)
        self.page1_entry.grid(row=1, column=4)
        self.page1_entry_var.set(str(self.mode['page1']))

        self.page2_label = Label(
            self.init_window_name, text="最多页数:")
        self.page2_label.grid(row=1, column=5)
        self.page2_entry_var = StringVar()
        # 注意，输入框就是单行文本，它是没有height属性的
        self.page2_entry = Entry(self.init_window_name, width=5,
                                 textvariable=self.page2_entry_var)
        self.page2_entry.bind('<Return>', self.refresh_page2)
        self.page2_entry.grid(row=1, column=6)
        self.page2_entry_var.set(str(self.mode['page2']))

        self.search_label = Label(
            self.init_window_name, text="搜索框:")
        self.search_label.grid(row=1, column=7)
        self.search_entry_var = StringVar()
        # 注意，输入框就是单行文本，它是没有height属性的
        self.search_entry = Entry(self.init_window_name, width=20,
                                  textvariable=self.search_entry_var)
        self.search_entry.bind('<Return>', self.beginsearch)
        self.search_entry.grid(row=1, column=8)

        self.home_data_frame = Frame(
            self.init_window_name, bg="white")
        self.home_data_frame.place(
            x=0, y=20, width=self.homewidth, height=self.homeheight)
        self.last_label = Label(
            self.init_window_name, text="前一页")
        self.last_label.bind('<Button-1>', self.lastPage())
        self.last_label.place(x=self.homewidth//2-75,
                              y=self.homeheight+20, width=50, height=30)
        self.where_label = Label(
            self.init_window_name, text="1-20")
        self.where_label.place(x=self.homewidth//2-25,
                               y=self.homeheight+20, width=50, height=30)
        self.next_label = Label(
            self.init_window_name, text="后一页")
        self.next_label.bind('<Button-1>', self.nextPage())
        self.next_label.place(x=self.homewidth//2+25,
                              y=self.homeheight+20, width=50, height=30)
        self.direct_download_Label = Label(self.init_window_name, text="下载链接")
        self.direct_download_Label.place(x=self.homewidth+50, y=0)
        self.direct_download_var = StringVar()
        # 注意，输入框就是单行文本，它是没有height属性的
        self.direct_download_entry = Entry(self.init_window_name,
                                           textvariable=self.direct_download_var)
        self.direct_download_entry.bind('<Return>', self.directdownload)
        self.direct_download_entry.place(
            x=self.homewidth+50, y=20, width=self.directdownloadwidth)

        self.downlist_data_Label = Label(self.init_window_name, text="下载列表")
        self.downlist_data_Label.place(x=self.homewidth+50, y=40)
        self.downlist_data_box = Listbox(self.init_window_name)
        self.downlist_data_box.bind(
            "<Button-1>", self.click_button(self.downlist_data_box))
        self.downlist_data_box.place(
            x=self.homewidth+50, y=60, width=self.downlistwidth, height=self.downlistheight)

        # for i in range(2):
        #     labal = Label(self.downlist_data_frame, text="123", bg='green')
        #     labal.grid(row=i, column=0)

        vbar = Scrollbar(self.downlist_data_box, orient=VERTICAL)  # 竖直滚动条
        vbar.place(x=self.downlistwidth-20, width=20,
                   height=self.downlistheight)
        vbar.configure(command=self.downlist_data_box.yview)
        self.downlist_data_box.config(yscrollcommand=vbar.set)  # 设置
        self.tempPic_label = Label(
            self.init_window_name, text="预览图")
        self.tempPic_label.place(x=self.homewidth+50, y=60+self.downlistheight)
        self.tempPic = Label(
            self.init_window_name, bg="white")
        self.tempPic.place(
            x=self.homewidth+50, y=60+self.downlistheight+20, width=self.tempPicWidth, height=self.tempPicHeight)

        # self.switch_pages =

        # self.home_data_label.grid(row=2, column=0)

        self.searchthread = StoppableGetallThread(
            args={'str': '', 'root': self})
        self.searchthread.start()

        print("数量：", len(self.allworks))
        self.getworkslist()
        print("数量2：", len(self.worksList))
        # threads = [[] for i in range(len(self.worksList))]
        # for i in range(len(self.worksList)):
        #     threads[i] = Thread(target=self.pushwork, args=(i,))
        #     threads[i].setDaemon(True)
        # for i in range(len(self.worksList)):
        #     threads[i].start()
        # for i in range(len(self.worksList)):
        #     threads[i].join()
        self.push_step_works()
        self.refresh_data()
        self.refresh_downwork()

    def push_step_works(self, begin=0):
        # print("gong", min(self.step, len(self.worksList)-self.beginindex))
        for i in range(begin, min(self.step, len(self.worksList)-self.beginindex)):
            self.nowlabelnum = i
            self.pushwork(i)
            self.nowlabelnum = i+1

    def lastPage(self):
        def fun(event):
            if self.beginindex >= self.step:
                self.allLabels = [{}for i in range(self.step)]
                self.beginindex -= self.step
                self.home_data_frame.destroy()
                self.home_data_frame = Frame(
                    self.init_window_name, bg="white")
                self.home_data_frame.place(
                    x=0, y=20, width=self.homewidth, height=self.homeheight)
                self.push_step_works()
                self.updateWhere()
        return fun

    def nextPage(self):
        def fun(event):

            if self.beginindex + self.step < len(self.worksList):
                # print(1)
                self.allLabels = [{}for i in range(self.step)]
                self.beginindex += self.step
                self.home_data_frame.destroy()
                self.home_data_frame = Frame(
                    self.init_window_name, bg="white")
                self.home_data_frame.place(
                    x=0, y=20, width=self.homewidth, height=self.homeheight)
                # print(2)
                self.push_step_works()
                self.updateWhere()
        return fun

    def get_big(self, imgsrc):
        def larger():
            try:
                image_bytes = requests.get(
                    imgsrc, proxies=proxy, headers=headers).content
                # 将数据存放到data_stream中
                data_stream = io.BytesIO(image_bytes)
                # 转换为图片格式
                pil_image = Image.open(data_stream)
                w = pil_image.size[0]
                h = pil_image.size[1]
                k = h/w
                if self.tempPicHeight > k*self.tempPicWidth:
                    w = self.tempPicWidth
                    h = int(k*w)
                else:
                    h = self.tempPicHeight
                    w = int(h/k)
                pil_image = pil_image.resize((w, h))
                self.tempimg = ImageTk.PhotoImage(pil_image)
                self.tempPic.configure(image=self.tempimg)
            except:
                print("访问过快")

        def run_larger(event):
            self.tempPicThread = Thread(target=larger)
            self.tempPicThread.start()
        return run_larger

    # def get_more(self):
    #     self.break_get_more = False
    #     for i in range(9):
    #         time.sleep(3)
    #         if self.break_get_more == True:
    #             break
    #         url = 'https://e-hentai.org/?page='+str(i+1)
    #         self.addallworks(url)
    #     self.is_catching_more = False

    def getworkslist(self):
        self.nowloc -= 1
        while 1:
            self.findnext()
            if self.nowloc >= len(self.allworks):
                break
            work = self.allworks[self.nowloc]
            work['pic'] = ''
            self.worksList.append(work)
        if self.searchthread.stopped() == False:
            self.init_window_name.after(3000, self.getworkslist)

    def directdownload(self, event):
        link = self.direct_download_entry.get()
        print(link)
        self.outer_push_tesk(link, "")(event)
        self.direct_download_entry.delete(0, END)

    def beginsearch(self, event):
        self.search_entry_var = self.search_entry.get()
        self.worksList = []
        self.allworks = []
        self.home_data_frame.destroy()
        self.home_data_frame = Frame(
            self.init_window_name, bg="white")
        self.home_data_frame.place(
            x=0, y=20, width=self.homewidth, height=self.homeheight)
        self.getworkslist()
        self.beginindex = 0
        self.nowloc = 0
        self.nowlabelnum = 0
        self.searchthread.stop()
        self.searchthread = StoppableGetallThread(
            args={'str': self.search_entry.get(), 'root': self})
        self.searchthread.start()
        # self.addallworks(url)
        pass

    def getpic(self,  imgheight, imgwidth, index, label):
        # print('in')
        try:
            image_bytes = requests.get(
                self.worksList[index]['imgsrc'], proxies=proxy, headers=headers).content
            # 将数据存放到data_stream中
            data_stream = io.BytesIO(image_bytes)
            # 转换为图片格式
            pil_image = Image.open(data_stream)
            w = pil_image.size[0]
            h = pil_image.size[1]
            k = h/w
            if imgheight > k*imgwidth:
                w = imgwidth
                h = int(k*w)
            else:
                h = imgheight
                w = int(h/k)
            pil_image = pil_image.resize((w, h))
            self.worksList[index]['pic'] = ImageTk.PhotoImage(pil_image)
        except:
            pass
            # print('频繁访问', self.worksList[index]['imgsrc'])

    def click_button(self, box):
        def inbox(event):
            w = event.widget
            box.curIndex = box.nearest(event.y)
            index = box.curIndex
            task = self.tasklist[index]
            pathname = '.\\'+task['name']
            os.system("start explorer "+pathname)
        return inbox

    def ThreadsManage(self):
        # while 1:
        # print("inmanage")
        for task in self.tasklist:
            # print(task['name'], task['state'])
            # print(task['state'])
            if task['state'] == 'running':
                # print(task['name'], "running", task['finished'])
                if(task['finished'] == len(task['links'])):
                    task['state'] = 'done'
                break
            if task['state'] == 'prepared':
                # print(task['name'], 'prepared')
                task['state'] = 'running'
                task['threads'] = [StoppableDownloadThread(
                    args={'task': task, 'begin': i}) for i in range(20)]
                for ths in task['threads']:
                    ths.start()
                break

        # time.sleep(1)

    def outer_push_tesk(self, link, name):
        name = DL.validateTitle(name)

        def pushtask(event):
            # for i in range(2):
            #     labal = Label(self.downlist_data_frame, text="123", bg='green')
            #     labal.grid(row=i, column=0)

            task = {}
            task['mainlink'] = link
            task['name'] = name
            task['state'] = 'blank'
            task['links'] = []
            task['finished'] = 0

            self.downlist_data_box.insert(END, name)
            # TaskLabel.place(x=0, y=len(self.tasklist)*taskheight,
            #                 width=taskwidth, height=taskheight)
            # nameLabel = Label(TaskLabel, text=name, bg='green')
            # nameLabel.place(x=0, y=0,
            #                 width=namewidth, height=nameheight)
            self.tasklist.append(task)
            task['threadname'] = Thread(
                target=DL.getImgLinks, args=(link, task, name))
            task['threadname'].start()
            task['state'] = 'wait'

        return pushtask

    def pushwork(self, index):
        workheight = self.homeheight//((self.step+1)//2)
        workwidth = self.homewidth//2
        imgheight = workheight
        imgwidth = workwidth//9
        typeheight = workheight
        typewidth = workwidth//10
        starheight = workheight
        starwidth = workwidth//18
        pageheight = workheight
        pagewidth = workwidth//10
        nameheight = workheight
        namewidth = workwidth//2
        downheight = workheight
        downwidth = workwidth-imgwidth-typewidth-starwidth-pagewidth-namewidth
        work = self.worksList[index+self.beginindex]
        frame = Frame(self.home_data_frame, relief=GROOVE, border=3)
        if index % 2 == 1:
            frame.place(x=self.homewidth//2, y=workheight * (index//2),
                        width=workwidth, height=workheight)
        else:
            frame.place(x=0, y=workheight*(index//2),
                        width=workwidth, height=workheight)

        # self.imgs.append(tk_image)
        label = Label(frame,  bg='white', image=work['pic'])
        label.bind('<Button-1>', self.get_big(work['imgsrc']))
        if work['pic'] == '':
            thread = Thread(target=self.getpic, args=(
                imgheight, imgwidth, index+self.beginindex, label))
            thread.start()
        label.place(x=0, y=0, width=imgwidth, height=imgheight)
        self.allLabels[index]['label'] = label
        self.allLabels[index]['index'] = index+self.beginindex
        # label.pack(padx=5, pady=5)
        Typeframe = Label(frame)
        Typeframe.place(x=imgwidth, y=0,
                        width=typewidth, height=typeheight)
        t1 = Label(Typeframe, text="type", border=2, relief=GROOVE)
        t1.place(x=0, y=0, width=typewidth, height=typeheight//2)
        t2 = Label(Typeframe, text=work['type'], border=2, relief=GROOVE)
        t2.place(x=0, y=typeheight//2,
                 width=typewidth, height=typeheight//2)
        Starframe = Label(frame)
        Starframe.place(x=imgwidth+typewidth, y=0,
                        width=starwidth, height=starheight)
        s1 = Label(Starframe, text="Score", border=2, relief=GROOVE)
        s1.place(x=0, y=0, width=starwidth, height=starheight//2)
        s2 = Label(Starframe, text=work['star'], border=2, relief=GROOVE)
        s2.place(x=0, y=starheight//2,
                 width=starwidth, height=starheight//2)
        Pageframe = Label(frame)
        Pageframe.place(x=imgwidth+typewidth+starwidth, y=0,
                        width=pagewidth, height=pageheight)
        p1 = Label(Pageframe, text="page", border=2, relief=GROOVE)
        p1.place(x=0, y=0, width=pagewidth, height=pageheight//2)
        p2 = Label(Pageframe, text=work['page'], border=2, relief=GROOVE)
        p2.place(x=0, y=pageheight//2,
                 width=pagewidth, height=pageheight//2)
        Nameframe = Label(frame)
        Nameframe.place(x=imgwidth+typewidth+starwidth+pagewidth, y=0,
                        width=namewidth, height=nameheight)
        n1 = Label(Nameframe, text="Name", border=2, relief=GROOVE)
        n1.place(x=0, y=0, width=namewidth, height=nameheight//2)
        n2 = Label(Nameframe, text=work['name'],
                   border=2, relief=GROOVE, anchor='w')
        n2.place(x=0, y=nameheight//2,
                 width=namewidth, height=nameheight//2)
        DownloadButtom = Button(frame, text='Download')
        DownloadButtom.bind(
            "<Button-1>", self.outer_push_tesk(work['link'], work['name']))
        DownloadButtom.place(x=imgwidth+typewidth+starwidth+pagewidth+namewidth, y=0,
                             width=downwidth, height=downheight)
        frame.bind("<Button-1>", self.callback)

    def findnext(self):
        while self.nowloc+1 < len(self.allworks):
            self.nowloc += 1
            work = self.allworks[self.nowloc]
            if work['star'] >= self.mode[
                    'starleast'] and work['type'] in self.mode['type'] and work['page'] >= self.mode['page1'] and work['page'] <= self.mode['page2']:
                return
        self.nowloc = len(self.allworks)

    def refresh_data(self):
        for L in self.allLabels:
            try:
                L['label'].configure(
                    image=self.worksList[L['index']]['pic'])
            except:
                pass
        # print("refresh", self.nowlabelnum, len(self.worksList)-self.beginindex)
        if self.nowlabelnum < len(self.worksList)-self.beginindex:
            self.push_step_works(self.nowlabelnum)
        self.init_window_name.after(1000, self.refresh_data)

    def refresh_downwork(self):
        self.ThreadsManage()
        self.downlist_data_box.delete(0, END)
        for item in self.tasklist:
            name = item['name']
            self.downlist_data_box.insert(END, name)
        print("下载列表刷新")
        self.init_window_name.after(1000, self.refresh_downwork)

    def refresh_star(self, event):
        star = self.mode['starleast']
        try:
            star = float(self.star_entry_var.get())
        except:
            pass
        print(star)
        if star < 0:
            star = 0
        if star > 5:
            star = 5
        star = int(star*2)/2
        if self.mode['starleast'] != star:
            self.mode['starleast'] = star
            self.worksList = []
            self.home_data_frame.destroy()
            self.home_data_frame = Frame(
                self.init_window_name, bg="white")
            self.home_data_frame.place(
                x=0, y=20, width=self.homewidth, height=self.homeheight)
            self.getworkslist()
            self.beginindex = 0
            self.nowloc = 0
            self.nowlabelnum = 0
            self.push_step_works()
            self.updateWhere()
            self.star_entry_var.set(str(star))

    def refresh_page1(self, event):
        page1 = self.mode['page1']
        try:
            page1 = int(self.page1_entry_var.get())
        except:
            pass
        print(page1)
        if page1 < 0:
            page1 = 0
        if self.mode['page1'] != page1:
            self.mode['page1'] = page1
            self.worksList = []
            self.home_data_frame.destroy()
            self.home_data_frame = Frame(
                self.init_window_name, bg="white")
            self.home_data_frame.place(
                x=0, y=20, width=self.homewidth, height=self.homeheight)
            self.getworkslist()
            self.beginindex = 0
            self.nowloc = 0
            self.nowlabelnum = 0
            self.push_step_works()
            self.updateWhere()
            self.page1_entry_var.set(str(page1))

    def refresh_page2(self, event):
        page2 = self.mode['page2']
        try:
            page2 = int(self.page2_entry_var.get())
        except:
            pass
        print(page2)
        if page2 < 0:
            page2 = 10000
        if self.mode['page2'] != page2:
            self.mode['page2'] = page2
            self.worksList = []
            self.home_data_frame.destroy()
            self.home_data_frame = Frame(
                self.init_window_name, bg="white")
            self.home_data_frame.place(
                x=0, y=20, width=self.homewidth, height=self.homeheight)
            self.getworkslist()
            self.beginindex = 0
            self.nowloc = 0
            self.nowlabelnum = 0
            self.push_step_works()
            self.updateWhere()
            self.page2_entry_var.set(str(page2))

    def updateWhere(self):
        self.where_label.configure(
            text=str(self.beginindex+1)+"-"+str(self.beginindex+self.step))

    def callback(self, event):
        for work in self.worksList:
            print(work['page'], end=' ')
        print()


def callback(event):
    print("clicked at", event)


root = Tk()
GUI = MY_GUI(root)
GUI.set_init_windows()
root.mainloop()
