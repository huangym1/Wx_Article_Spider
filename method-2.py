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
        self.conn = pymysql.connect(host='xxx',user='xxx',password='xxx',database='xxx') # 填写数据库信息
        self.headers = {
            'HOST': 'mp.weixin.qq.com',
            'Cookie': cookies,
            'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 '
        }

    def start(self):
        print("正在爬取：{}".format(account))
        while True:
            url = "https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz={}&f=json&offset={}&count=10&is_ok=1" \
                  "&scene=124&uin={}&key={}&pass_ticket={}&wxtoken=&appmsg_token={}&x5=0&f=json".format(self.biz,self.offset,self.uin,self.key,self.pass_ticket,self.token)
            print(url)
            response = requests.get(url,headers=self.headers).json()
            ret,status = response['ret'],response['errmsg']
            if ret == 0 or status == 'ok':
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
                print("ret:{},status:{}".format(ret, status))
                break
            time.sleep(10)
            self.offset = next_offset
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
    account = "简说Python"
    uri = "/mp/profile_ext?action=getmsg&__biz=MzUyOTAwMzI4NA==&f=json&offset=10&count=10&is_ok=1&scene=124&uin=MTIzOTMzNTI0MA%3D%3D&key=b88e9d7de4cb783ef18eb7cb428f781480c9ef527347502b3ff875753ba1e24a07c6258970c28aefa5db418b08cd214bf19cc4c45ab0d91d90e2a2e5b7db75ee4df37415c637f939a31244f881152e57&pass_ticket=KkkSyncV1LOwdql5EiR1wqcgPDw6EfRiskQxaXv%2BL3wePVuwWwsszq2FY9JEYq2%2F&wxtoken=&appmsg_token=1038_9fITF9WPkemIJaxNXglGJ5DgxzzNM190-1_RAA~~&x5=0&f=json"
    biz = re.search(r'.*biz=(.*?)&',uri).group(1)
    uin = re.search(r'.*uin=(.*?)&',uri).group(1)
    key = re.search(r'.*key=(.*?)&',uri).group(1)
    pass_ticket = re.search(r'.*pass_ticket=(.*?)&',uri).group(1)
    appmsg_token = re.search(r'.*appmsg_token=(.*?)&',uri).group(1)
    cookies = "wap_sid2=CMiC+84EElxWb2I4U291bGs0V2NEN0pHOWZyNlBKOXB1d2p2T3VHcmJwMWdvU1VidVdvY2JzZk0tX3RqNnU4NUUxMmhjZHhMRjlQenlqWmJVWmVwNUNKUlZ2Y3FtdzRFQUFBfjDsiqTvBTgNQJVO"
    wx = WxSpider(biz,uin,key,pass_ticket,appmsg_token,cookies,account)
    wx.start()
