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
        self.headers = {
            'HOST': 'mp.weixin.qq.com',
            'Cookie': cookies,
            'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 '
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
            time.sleep(10)
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
    account = "俊红的数据分析之路"
    uri = "/mp/profile_ext?action=getmsg&__biz=MzI2MjE3OTA1MA==&f=json&offset=18&count=10&is_ok=1&scene=124&uin=MTIzOTMzNTI0MA%3D%3D&key=aa8e5c393e4dd29dd14e5d5d42da71a0a675a30ae47d1e051da801ef4ca2ddc0d8ea80a26b09faec3e87602efd300166aba2aeeb888389e885b267f7629f5ff3d3c4c40d961672f0fdf1ec46d2d093c8&pass_ticket=EU51ZWV3zD2L8nXAYbmH0unTVcvlO59nMrEcuF3i3T2sD1iEBN09l2ULLDHYEP3N&wxtoken=&appmsg_token=1038_yBvzRmxnbJiZVYHBcubUqKl6Xdz0_qQ5P_zNNw~~&x5=0&f=json"
    biz = re.search(r'.*biz=(.*?)&',uri).group(1)
    uin = re.search(r'.*uin=(.*?)&',uri).group(1)
    key = re.search(r'.*key=(.*?)&',uri).group(1)
    pass_ticket = re.search(r'.*pass_ticket=(.*?)&',uri).group(1)
    appmsg_token = re.search(r'.*appmsg_token=(.*?)&',uri).group(1)
    cookies = "wap_sid2=CMiC+84EEnBneDNjWHJhMk5kQU56RWdhT0EwNzY1UThzUFlRN1BObENlREl4WWZzYUI5cXVSTnhZNExSRnpManAzbkRfdWs0SFllNEtWY284Rnl0QVBOaVNjZGJZTDFNZDYzUUI1MVc4R0VlQTRhcU9HSU9CQUFBMOTbqe8FOA1AlU4="
    wx = WxSpider(biz,uin,key,pass_ticket,appmsg_token,cookies,account)
    wx.start()
