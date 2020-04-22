import requests


def getCookies():
    params = {
        'login_url': 'http://authserver.swun.edu.cn/authserver/login',
        'needcaptcha_url': 'http://authserver.swun.edu.cn/authserver/needCaptcha.html',
        'captcha_url': 'http://authserver.swun.edu.cn/authserver/captcha.html',
        'username': 'test',
        'password': 'test'
    }

    # 借助上一个项目开放出来的登陆API，此API只适用于宜宾学院
    res = requests.post('http://www.zimo.wiki:8080/yibinu-score-crawler/api/login', params)
    print(res.text)


if __name__ == '__main__':
    getCookies()
