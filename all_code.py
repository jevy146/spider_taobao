# @File  : all_code.py
# @Author: Jie Wei
#@time: 2019/6/26 16:46

import time
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq


client = pymongo.MongoClient("192.168.124.21",port=27017)  #默认的端口为27017，笔记本电脑的Ip
db = client["taobao"]
#第一步实现对淘宝的登陆
class Chrome_drive():
    def __init__(self):
        ua = UserAgent()
        # self.ip = IP  # 将爬取代理IP 开启来。。
        chrome_options = Options()
        # NoImage = {"profile.managed_default_content_settings.images": 2}  # 控制 没有图片
        # chrome_options.add_experimental_option("prefs", NoImage)
        # self.browser = webdriver.Chrome(chrome_options=chrome_options)  # 这里打开的话，会多增加一个浏览器运行。
        chrome_options.add_argument(f'user-agent={ua.chrome}')  # 增加浏览器头部
        print(ua.random)
        # chrome_options.add_argument(f"--proxy-server=http://{self.ip}")  # 增加IP地址。。
        # self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser = webdriver.Chrome(options=chrome_options)  ## 实例化浏览器。。
        self.wait = WebDriverWait(self.browser, 12)

    def get_login(self):
        url='https://s.taobao.com/'

        self.browser.get(url)
        self.browser.maximize_window()  # 在这里登陆的中国大陆的邮编
        time.sleep(12)
        #10秒的时间进行扫码进行登陆。还有一种方式，提前获取cookie，然后通过
        '''   browser.add_cookie({
        'domain':'.taobao.com',  # 此处xxx.com前，需要带点
        'name': cookie['name'],
        'value': cookie['value'],
        'path': '/',
        'expires': None
            })'''

        return


    #获取判断网页文本的内容：
    def index_page(self,page):
        """
        抓取索引页
        :param page: 页码
        """
        print('正在爬取第', page, '页')

        url = 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E5%B0%8F%E9%BE%99%E8%99%BE&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest&bcoffset=-3&ntoffset=-3&p4ppushleft=1%2C48&s=' + str(
                page * 22)
        js1 = f" window.open('{url}')"  # 执行打开新的标签页
        self.browser.execute_script(js1)  # 打开新的网页标签
            # 执行打开新一个标签页。
        self.browser.switch_to.window(self.browser.window_handles[-1])  # 此行代码用来定位当前页面窗口
        self.buffer()  # 网页滑动  成功切换
            #等待元素加载出来
        time.sleep(2)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
            #获取网页的源代码
        html =  self.browser.page_source

        get_products(html)

        self.close_window()


    def buffer(self): #滑动网页的
        for i in range(12):
            time.sleep(0.8)
            self.browser.execute_script('window.scrollBy(0,300)', '')  # 向下滑行300像素。

    def close_window(self):
        length=self.browser.window_handles
        print('length',length) #判断当前网页窗口的数量
        if  len(length) > 3:
            self.browser.switch_to.window(self.browser.window_handles[1])
            self.browser.close()
            time.sleep(1)
            self.browser.switch_to.window(self.browser.window_handles[-1])



#解析网页，
def get_products(html):
    """
    提取商品数据
    """
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('data-src'),
            'shop_href': item.find('.J_ItemPicA').attr('data-href'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)

#将数据保存到mongodb中
def save_to_mongo(result):
    """
    保存至MongoDB
    :param result: 结果
    """
    try:
        if db['xiaolongxia'].insert(result):
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')

MAX_PAGE=100
def main():
    """
    遍历每一页
    """
    run=Chrome_drive()
    run.get_login() #先扫码登录
    #从第二页开始爬取
    for i in range(3, MAX_PAGE + 1):
        run.index_page(i)


if __name__ == '__main__':
    main()