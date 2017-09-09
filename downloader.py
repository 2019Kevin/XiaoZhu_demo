# -*- coding:utf-8 -*-
from urllib.parse import urlsplit
import random
import time
import  socket
import requests
from datetime import datetime

DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_TIMEOUT = 60
DEFAULT_USER_AGENT = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]

class Downloader:
    def __init__(self, delay=DEFAULT_DELAY, user_agent = DEFAULT_USER_AGENT,
                 timout=DEFAULT_TIMEOUT,cache=None):
        socket.setdefaulttimeout(timout)
        self.throttle = Throttle(delay)
        self.cache = cache
        self.user_agent = user_agent


    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                # 在缓存不存在url
                pass
        if result is None:
            #结果没有从缓存中得到，所以仍然需要被下载
            self.throttle.wait(url)
            result = self.download(url)
            if self.cache:
                #保存结果到缓存中
                self.cache[url] = result
        return result['html']


    def download(self, url, proxy=None, num_retries=3):
        User_Agent = random.choice(self.user_agent)
        headers = {'User-Agent': User_Agent}
        print('Downloading:', url)
        html = None

        if proxy is None:              #当代理为空时,不使用代理来发送请求
            try:
                wb_data = requests.get(url, headers=headers)
                if wb_data.status_code == 200:        #如果请求成功，并且返回正常值
                    html = wb_data.text
                    return  {'html': html}
                else:                                 #如果请求成功，但是返回其他信息， 那么使用忽略这个url的访问
                    pass
            except Exception as e:                                   #如果请求发生异常，
                print(str(e))
                if num_retries > 0:
                    time.sleep(5)
                    print('获取信息出错， 5s后倒数第{:d}次重新尝试!'.format(num_retries) )
                    return self.download(url, num_retries-1)
        return {'html': html}

class Throttle:
    def __init__(self, delay):
        # 在两次相同域名之间设置延时
        self.delay = delay
        # 上次访问一个域名的时间戳
        self.domains = {}

    def wait(self, url):
        """如果域名最近被访问过,那么设置延时
        """
        domain = urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()



























