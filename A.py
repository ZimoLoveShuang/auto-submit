import requests


def getCookies():
    params = {
        'login_url': 'http://authserver.swun.edu.cn/authserver/login',
        'needcaptcha_url': 'http://authserver.swun.edu.cn/authserver/needCaptcha.html',
        'captcha_url': 'http://authserver.swun.edu.cn/authserver/captcha.html',
        'username': 'test',
        'password': 'test'
    }

    res = requests.post('http://www.zimo.wiki:8080/yibinu-score-crawler/api/login', params)
    print(res.text)


if __name__ == '__main__':
    getCookies()
