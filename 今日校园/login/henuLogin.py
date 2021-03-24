import json
import re

from bs4 import BeautifulSoup

from login.Utils import Utils


class henuLogin:
    # 初始化henu登陆类
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
        if (len(form) == 0):
            raise Exception('出错啦！网页中没有找到casLoginForm')
        # 填充input字段
        params = {}
        form = soup.select('#loginFromId input')
        for item in form:
            if None != item.get('name') and len(item.get('name')) > 0:
                if item.get('name') != 'rememberMe':
                    if (None == item.get('value')):
                        params[item.get('name')] = ''
                    else:
                        params[item.get('name')] = item.get('value')
        params.pop('dllt')
        # 寻找salt
        salt = soup.select('#pwdEncryptSalt')[0].get('value')
        # 填充用户名和密码
        params['username'] = self.username
        params['password'] = Utils.encryptAES(self.password, salt)
        if self.getNeedCaptchaUrl():
            imgUrl = self.host + '/authserver/getCaptcha.htl'
            code = Utils.getCodeFromImg(self.session, imgUrl)
            params['captcha'] = code
        res = self.session.post(self.login_url, params=params, verify=False, allow_redirects=False)
        if res.status_code == 302:
            jump_url = res.headers['Location']
            self.session.post(jump_url, verify=False)
            return self.session.cookies
        elif res.status_code == 401:
            msg = soup.select('#formErrorTip2')[0].get_text()
            raise Exception(msg)
        else:
            raise Exception('教务系统出现了问题啦！返回状态码：' + str(res.status_code))

    # 判断是否需要验证码
    def getNeedCaptchaUrl(self):
        host = re.findall('\w{4,5}\:\/\/.*?\/', self.login_url)[0]
        url = host + 'authserver/checkNeedCaptcha.htl' + '?username=' + self.username
        flag = self.session.get(url, verify=False).json()
        return flag['isNeed']
