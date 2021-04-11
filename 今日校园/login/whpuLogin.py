import re

import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

from login.Utils import Utils

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# 完成武汉轻工大学的登陆适配

class whpuLogin:
    # 初始化武汉轻工登陆模块
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
        form = soup.select('#loginFromId')
        # 有两种登陆方式，这里选择第二种
        if (len(form) != 2):
            raise Exception('出错啦！网页中没有找到登陆表单')
        form = form[1]
        html = "<html>" + str(form) + "</html>"
        soup = BeautifulSoup(html, 'lxml')
        form = soup.select('input')
        # 填充数据
        params = {}
        form = soup.select('input')
        for item in form:
            if None != item.get('name') and len(item.get('name')) > 0:
                if item.get('name') != 'rememberMe':
                    if (None == item.get('value')):
                        params[item.get('name')] = ''
                    else:
                        params[item.get('name')] = item.get('value')
        salt = soup.select("#pwdEncryptSalt")
        if len(salt) == 0:
            raise Exception('未找到salt，请联系开发者')
        salt = salt[0].get('value')
        params['username'] = self.username
        params['password'] = Utils.encryptAES(self.password, salt)
        if self.getNeedCaptchaUrl():
            imgUrl = self.host + 'authserver/getCaptcha.htl'
            code = Utils.getCodeFromImg(self.session, imgUrl)
            params['captcha'] = code
        data = self.session.post(self.login_url, params=params, allow_redirects=False)
        if data.status_code == 302:
            jump_url = data.headers['Location']
            self.session.post(jump_url, verify=False)
            return self.session.cookies
        elif data.status_code == 200:
            data = data.text
            soup = BeautifulSoup(data, 'lxml')
            msg = soup.select('#showErrorTip')[0].get_text()
            raise Exception(msg)


    # 判断是否需要验证码
    def getNeedCaptchaUrl(self):
        host = re.findall('\w{4,5}\:\/\/.*?\/', self.login_url)[0]
        url = host + 'authserver/checkNeedCaptcha.htl' + '?username=' + self.username
        flag = self.session.get(url, verify=False).json()
        return flag['isNeed']