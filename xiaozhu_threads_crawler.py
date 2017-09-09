import queue
import re
import threading
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
from  downloader import Downloader
from scrape_back import GetDetailInfo
from mongo_cache import MongoCache



SLEEP_TIME = 1



def threaded_crawler(seed_url, delay=2, max_depth=-1,max_urls = -1,proxy=None,
                     user_agent='wswp', scrape_callback=None, cache=None, max_threads=5):

    crawl_queue = queue.deque([seed_url])
    seen = {seed_url: 0}
    rp = get_robots(seed_url)
    D = Downloader(delay=delay, cache=cache)

    def process_queue():
        num_urls = 0
        page = 1
        while True:
            try:
                url = crawl_queue.pop()
            except IndexError:
                # crawl queue is empty
                break
            else:
                if rp.can_fetch(user_agent, url):
                    html = D(url)
                    if html is None:
                        pass
                    else:
                        if scrape_callback:
                            try:
                                s = scrape_callback()
                                s(url, html)
                            except Exception as e:
                                print('Error in callback for: {}: {}'.format(url, e))
                            else:
                                link_regex  = '/(fangzi|search-duanzufang-p{}-0)'.format(page+1)
                                if re.search('search-duanzufang', url):
                                    depth = seen[url]
                                    if depth != max_depth:
                                        # 将来仍然可以爬虫
                                        for link in get_links(html):  # 过滤以得到与我们的链接正则表达式匹配的链接地址
                                            if re.search(link_regex, link):
                                                if link not in seen:
                                                    seen[link] = depth + 1
                                                    # 检查链接是否在相同的域名
                                                    if same_domain(seed_url, link):
                                                        # success! 将链接加入到爬虫列表中
                                                        crawl_queue.append(link)
                    page += 1
                    num_urls += 1
                    if num_urls == max_urls:
                        break
                else:
                    print('Blocked by robots.txt: ', url)
    # 等待所有的下载线程结束
    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                # 移除已经停止的进程
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            # 开始更多的线程
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        time.sleep(SLEEP_TIME)

def get_links(html):
    webpage = re.compile('href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage.findall(html)

def get_robots(url):
    #解析网站的robots.txt文件
    rp = RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    rp.read()
    return rp

def same_domain(url1, url2):
    """如果两个url地址具有相同的域名则返回回真。
    """
    return urlparse(url1).netloc == urlparse(url2).netloc


if __name__ == '__main__':
    Scrape_Back = GetDetailInfo
    Cache = MongoCache()
    Cache.clear()
    Areas = ['bj', 'sh', 'gz', 'sz', 'cs', 'wh', 'cd', 'cq']
    for Area in Areas:
        URL = 'http://{}.xiaozhu.com/search-duanzufang-p1-0/'.format(Area)
        threaded_crawler(URL, scrape_callback=Scrape_Back, cache=Cache)