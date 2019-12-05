from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import json
import re
import requests
import random
import math


class weChatSpider(object):
    def __init__(self):
        self.post = {}
        self.username = "15018890736@163.com"
        self.password = "hym19920325"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(chrome_options=self.options)
        print("启动浏览器...")

    def weChatLogin(self):
        print("打开微信公众号...")
        self.driver.get("https://mp.weixin.qq.com/")
        time.sleep(2)
        print("正在输入微信公众号登录账号和密码...")
        self.driver.find_element_by_xpath("//input[@name='account']").clear()
        self.driver.find_element_by_xpath("//input[@name='account']").send_keys(self.username)
        self.driver.find_element_by_xpath("//input[@name='password']").clear()
        self.driver.find_element_by_xpath("//input[@name='password']").send_keys(self.password)
        self.driver.find_element_by_xpath("//i[@class='icon_checkbox']").click() # 勾选自动登录
        self.driver.find_element_by_xpath("//a[@class='btn_login']").click()
        time.sleep(2)
        self.driver.get_screenshot_as_file("QR_code.png")

        print("等待扫码，20秒倒数...")
        time.sleep(20)
        cookie_items = self.driver.get_cookies()
        for cookie_item in cookie_items:
            self.post[cookie_item['name']] = cookie_item['value']
        cookie_str = json.dumps(self.post)
        with open('cookies.txt','w+',encoding='utf-8') as f:
            f.write(cookie_str)
        print("Cookies已保存到本地...")

    def weChatGetContent(self,query):
        print("开始爬取...")
        appmsg = dict() # 用来存放文章标题和链接
        url = 'https://mp.weixin.qq.com'
        headers = {
            "HOST": "mp.weixin.qq.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
        }
        with open('cookies.txt','r',encoding='utf-8') as f:
            cookies = json.loads(f.read())
        response = requests.get(url=url, cookies=cookies)
        token = re.findall(r'token=(\d+)', str(response.url))[0]
        # 搜索接口
        search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
        query_id = {
            'action': 'search_biz',
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'query': query,
            'begin': '0',
            'count': '5'
        }

        search_response = requests.get(search_url,cookies=cookies,headers=headers,params=query_id)
        lists = search_response.json().get('list')[0]
        fakeid = lists.get('fakeid')

        # 数据接口
        appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
        query_id_data = {
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'action': 'list_ex',
            'begin': '0',
            'count': '5',
            'query':'',
            'fakeid':fakeid,
            'type':9
        }
        appmsg_response = requests.get(appmsg_url,headers=headers,cookies=cookies,params=query_id_data)
        countSum = appmsg_response.json().get('app_msg_cnt')
        print("{}:共{}篇文章...".format(query,countSum))
        page = int(math.floor(int(countSum)/5)*5)

        # 起始页是最后一页，往后每页-5
        begin = int(int(page-1)*5)
        curPage = page
        while curPage > 0 :
            query_id_data = {
                'token': token,
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': '1',
                'random': random.random(),
                'action': 'list_ex',
                'begin': '{}'.format(begin),
                'count': '5',
                'query': '',
                'fakeid': fakeid,
                'type': 9
            }
            print("{}:共{}页，正在爬取第{}页，begin={}...".format(query,page,curPage,begin))
            appmsg_response = requests.get(appmsg_url, headers=headers, cookies=cookies, params=query_id_data)
            appmsg_lists = appmsg_response.json().get('app_msg_list')
            with open('{}.txt'.format(query),'a+',encoding='utf-8') as f:
                for i in range(5):
                    update_time = str(appmsg_lists[i]['update_time'])
                    title = appmsg_lists[i]['title']
                    link = appmsg_lists[i]['link']
                    f.write(title+"\t"+update_time+"\t"+link+"\n")
            curPage -= 1
            begin -= 5
            time.sleep(10)
        print("已完成{}的爬取...".format(query))

if __name__ == '__main__':
    spider = weChatSpider()
    spider.weChatLogin()
    query = ['简说Python','进击的Coder']
    for item in query:
        spider.weChatGetContent(item)