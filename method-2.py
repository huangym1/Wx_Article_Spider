import pymysql
import requests
import json
import random
import re
from datetime import datetime
import time
from selenium import webdriver

class WxSpider(object):
    def __init__(self,biz,uin,key,pass_ticket,token,cookies,account,offset=0):
        self.biz = biz
        self.offset = offset
        self.uin = uin
        self.key = key
        self.pass_ticket = pass_ticket
        self.token = token
        self.cookies = cookies
        self.account = account
        self.conn = pymysql.connect(host='192.168.1.11',user='hive',password='hive',database='wx_spider') # 填写数据库信息
        self.uapools = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'
        ]
        self.ua = random.choice(self.uapools)
        self.headers = {
            'HOST': 'mp.weixin.qq.com',
            'Cookie': cookies,
            'User-Agent': self.ua
        }

    def start(self):
        print("正在爬取：[{}]...".format(account))
        while True:
            print("offset:{}".format(self.offset))
            url = "https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz={}&f=json&offset={}&count=10&is_ok=1" \
                  "&scene=124&uin={}&key={}&pass_ticket={}&wxtoken=&appmsg_token={}&x5=0&f=json".format(self.biz,self.offset,self.uin,self.key,self.pass_ticket,self.token)
            response = requests.get(url,headers=self.headers).json()
            can_msg_continue = response['can_msg_continue']
            if can_msg_continue == 1:
                next_offset = response['next_offset'] # 下一次偏移量
                general_msg_list = response['general_msg_list']
                msg_list = json.loads(general_msg_list)['list']
                for msg in msg_list:
                    if 'app_msg_ext_info' in msg:
                        app_msg = msg['app_msg_ext_info']
                        if app_msg['title']:
                            _datetime =  datetime.fromtimestamp(msg['comm_msg_info']['datetime'])
                            self.parseMsgToMysql(app_msg,_datetime)
                        multi_list = msg['app_msg_ext_info']['multi_app_msg_item_list']
                        if multi_list:
                            for multi_msg in multi_list:
                                self.parseMsgToMysql(multi_msg,_datetime)
            else:
                print("can_msg_continue:{}".format(can_msg_continue))
                break
            time.sleep(20)
            self.offset = next_offset
        print("已完成[{}]的爬取...".format(self.account))
        self.conn.close()

    def parseMsgToMysql(self,msg,datetime):
        account = self.account  # 公众号名字
        title = msg['title']  # 文章标题
        author = msg['author'] # 作者
        soure_url = msg['source_url'] # 原始url
        content_url = msg['content_url'] # 内容url
        _datetime = datetime # 文章更新时间
        data = [account, title, author, soure_url, content_url, _datetime]
        sql = "insert into article(account, title, author, soure_url, content_url, datetime) values(%s,%s,%s,%s,%s,%s)"
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql,data) # 数据入库
            self.conn.commit()
        except Exception as e:
            print(e)
        return

if __name__ == '__main__':
    account = "Python专栏"
    uri = "/mp/profile_ext?action=getmsg&__biz=Mzg4ODE1MjU4Ng==&f=json&offset=10&count=10&is_ok=1&scene=124&uin=MTIzOTMzNTI0MA%3D%3D&key=ee95545b6f7acc6e3a73e1790e5ec2ae32640574326acebc4fb9b30712ad2d6abec0c128f1be90f57a72c89cc8b81e26c8fbf6790bb8329726b3970e1fa1f616fe9c312df2b4233858908524d19268e7&pass_ticket=EZfJgKvg3Yh7YLIEWbsiD8qlGJWd9d8iICmwQNSzrxlDcTmAlvtUnITKZtnK5nHr&wxtoken=&appmsg_token=1039_q%252FL8T7Oqoxilxv3dKApFFxo-Xm0ZGGyFPFJSHg~~&x5=0&f=json"
    biz = re.search(r'.*biz=(.*?)&',uri).group(1)
    uin = re.search(r'.*uin=(.*?)&',uri).group(1)
    key = re.search(r'.*key=(.*?)&',uri).group(1)
    pass_ticket = re.search(r'.*pass_ticket=(.*?)&',uri).group(1)
    appmsg_token = re.search(r'.*appmsg_token=(.*?)&',uri).group(1)
    cookies = "wap_sid2=CMiC+84EElw5Y1g4QzZ6LWduVFBTWXp6TUV2cmp0VFFFRTlMdjZ0OF9PcU5xVlkzek9qLVVvREJIX3kzTVV2M3Fqckh1WnloeGpFSjNHWTNDY3ZPZFBMeURPaXVwUThFQUFBfjCIw8LvBTgNQJVO"
    wx = WxSpider(biz,uin,key,pass_ticket,appmsg_token,cookies,account)
    wx.start()
