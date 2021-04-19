import json
import re

from bs4 import BeautifulSoup

from login.Utils import Utils

class kmuLogin:
    # 初始化昆明学院的登陆类
    def __init__(self, username, password, login_url, host, session):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.host = host
        self.session = session
    # 登陆方法
    def login(self):
        html = self.session.get(self.login_url, verify=False).text
        soup = BeautifulSoup(html, 'lxml')
        form = soup.select('#fm1')
        if (len(form) == 0):
            raise Exception('出错啦！网页中没有找到casLoginForm')
        # 填充input字段
        params = {}
        form = soup.select('#fm1 input')
        for item in form:
            if None != item.get('name') and len(item.get('name')) > 0:
                if item.get('name') != 'rememberMe':
                    if (None == item.get('value')):
                        params[item.get('name')] = ''
                    else:
                        params[item.get('name')] = item.get('value')
        print(params)
        salt = soup.select('#pwdEncryptSalt')[0].get('value')
        print(salt)