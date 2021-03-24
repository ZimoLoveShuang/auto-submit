import re
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from login.Utils import Utils
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class casLogin:
    # 初始化cas登陆模块
    def __init__(self, username, password, login_url, host, session):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.host = host
        self.session = session

    # 判断是否需要验证码
    def getNeedCaptchaUrl(self):
        host = re.findall('\w{4,5}\:\/\/.*?\/', self.login_url)[0]
        url = host + 'authserver/needCaptcha.html' + '?username=' + self.username
        flag = self.session.get(url, verify=False).text
        return 'false' != flag and 'False' != flag

    def login(self):
        html = self.session.get(self.login_url, verify=False).text
        soup = BeautifulSoup(html, 'lxml')
        form = soup.select('#casLoginForm')
        if (len(form) == 0):
            raise Exception('出错啦！网页中没有找到casLoginForm')
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
        salt = soup.select("#pwdDefaultEncryptSalt")
        if (len(salt) != 0):
            salt = salt.get_text()
        else:
            pattern = '\"(\w{16})\"'
            salt = re.findall(pattern, html)
            if (len(salt) == 1):
                salt = salt[0]
            else:
                salt = False
        params['username'] = self.username
        if not salt:
            params['password'] = self.password
        else:
            params['password'] = Utils.encryptAES(self.password, salt)
            if self.getNeedCaptchaUrl():
                imgUrl = self.host + 'authserver/captcha.html'
                code = Utils.getCodeFromImg(self.session, imgUrl)
                params['captchaResponse'] = code
        data = self.session.post(self.login_url, params=params, allow_redirects=False)
        # 如果等于302强制跳转，代表登陆成功
        if data.status_code == 302:
            jump_url = data.headers['Location']
            self.session.post(jump_url, verify=False)
            return self.session.cookies
        elif data.status_code == 200:
            data = data.text
            soup = BeautifulSoup(data, 'lxml')
            msg = soup.select('#errorMsg')[0].get_text()
            raise Exception(msg)
        else:
            raise Exception('教务系统出现了问题啦！返回状态码：' + str(data.status_code))
