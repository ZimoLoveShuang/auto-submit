# 获取不到MOD_AUTH_CAS
import re
import time
import requests
from fzu.utils import *
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# 全局配置
config = getYmlConfig('config.yml')
session = requests.session()


# 获取今日校园api
def getCpdailyApis(user):
    apis = {}
    schools = requests.get(url='https://www.cpdaily.com/v6/config/guest/tenant/list').json()['data']
    flag = True
    for one in schools:
        if one['name'] == user['school']:
            if one['joinType'] == 'NONE':
                log(user['school'] + ' 未加入今日校园')
                exit(-1)
            flag = False
            params = {
                'ids': one['id']
            }
            apis['tenantId'] = one['id']
            res = requests.get(url='https://www.cpdaily.com/v6/config/guest/tenant/info', params=params)
            data = res.json()['data'][0]
            joinType = data['joinType']
            idsUrl = data['idsUrl']
            ampUrl = data['ampUrl']
            ampUrl2 = data['ampUrl2']
            if 'campusphere' in ampUrl or 'cpdaily' in ampUrl:
                parse = urlparse(ampUrl)
                host = parse.netloc
                apis[
                    'login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host
            if 'campusphere' in ampUrl2 or 'cpdaily' in ampUrl2:
                parse = urlparse(ampUrl2)
                host = parse.netloc
                apis[
                    'login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host
            if joinType == 'NOTCLOUD':
                res = requests.get(url=apis['login-url'])
                if urlparse(apis['login-url']).netloc != urlparse(res.url):
                    apis['login-url'] = res.url
            break
    if flag:
        log(user['school'] + ' 未找到该院校信息，请检查是否是学校全称错误')
        exit(-1)
    if user['school'] == '福州大学':
        apis[
            'login-url'] = 'http://id.fzu.edu.cn/authserver/login?service=http%3A%2F%2Fid.fzu.edu.cn%2Fauthserver%2Fmobile%2Fcallback%3FappId%3D673223559&login_type=mobileLogin'
    log(apis)
    return apis


# 登陆过程
def login(user):
    # 1. 获取登陆页
    api = getCpdailyApis(user)
    res = session.get(url=api['login-url'])
    html = res.text

    # 2. 构造登陆参数
    soup = BeautifulSoup(html, 'html5lib')

    # 2.1 获取加密盐
    salt = None
    pwdDefaultEncryptSalt = soup.find(id='pwdDefaultEncryptSalt')
    if pwdDefaultEncryptSalt == None:
        scripts = soup.find_all('script')
        for script in scripts:
            if 'pwdDefaultEncryptSalt' in str(script):
                search = re.search('"\w{16}"', str(script))
                group = search.group()
                salt = group[1:len(group) - 1]
                break
    else:
        salt = pwdDefaultEncryptSalt.attrs['value']
    # 2.2 获取表单参数
    casLoginForm = soup.find(id='casLoginForm')
    inputs = casLoginForm.find_all('input')
    params = {}
    for inp in inputs:
        attrs = inp.attrs
        if 'value' in attrs and 'name' in attrs:
            params[attrs['name']] = attrs['value']

    # 2.3 构造表单
    user = user['user']
    user['CpdailyInfo'] = getCpdailyInfo(user)
    user['SessionToken'] = DESEncrypt('')

    params['username'] = user['username']
    if salt == None:
        params['password'] = user['password']
    else:
        params['password'] = AESEncrypt(user['password'], salt)

    # 2.4 发送登陆请求
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    }
    res = session.post(url=api['login-url'], headers=headers, data=params)
    # 没有被禁用云端系统的NOTCLOUD学校模拟登陆到这里就可以了
    # 获取到ticket
    parse = urlparse(res.url)
    ticket = parse.fragment[len('mobile_token='):]
    user['ticket'] = DESEncrypt(ticket)

    # 3 notcloudlogin
    params = {
        'tenantId': api['tenantId'],
        'ticket': user['ticket'],
    }
    headers = {
        'SessionToken': user['SessionToken'],
        'clientType': 'cpdaily_student',
        'tenantId': api['tenantId'],
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': user['CpdailyInfo'],
        'RetrofitHeader': '8.0.8',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'www.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }

    res = session.post(url='https://www.cpdaily.com/v6/auth/authentication/notcloud/login', headers=headers,
                       data=json.dumps(params))
    errMsg = res.json()['errMsg']
    if errMsg != None:
        log(errMsg)
        exit(-1)
    data = res.json()['data']
    mobile = data['mobile']
    user['mobile'] = mobile

    # 3.1 发送验证码
    params = {
        'mobile': DESEncrypt(mobile)
    }
    res = session.post(url='https://www.cpdaily.com/v6/auth/deviceChange/mobile/messageCode', headers=headers,
                       data=json.dumps(params))
    errMsg = res.json()['errMsg']
    if errMsg != None:
        log(errMsg)
        exit(-1)
    messageCode = input('请输入验证码：')
    params = {
        'messageCode': messageCode,
        'ticket': user['ticket'],
        'mobile': user['mobile'],
    }

    # 3.2 验证验证码
    res = session.post(url='https://www.cpdaily.com/v6/auth/deviceChange/validateMessageCode', headers=headers,
                       data=json.dumps(params))
    data = res.json()['data']
    tgc = data['tgc']
    sessionToken = data['sessionToken']
    amp = {
        'AMP1': [{
            'value': sessionToken,
            'name': 'sessionToken'
        }],
        'AMP2': [{
            'value': sessionToken,
            'name': 'sessionToken'
        }]
    }
    user['idsToken'] = user['ticket']
    user['tgc'] = DESEncrypt(tgc)
    user['SessionToken'] = DESEncrypt(sessionToken)
    user['amp'] = DESEncrypt(json.dumps(amp))

    # 3.3 更新acw_tc
    headers2 = {
        'TGC': user['tgc'],
        'AmpCookies': user['amp'],
        'SessionToken': user['SessionToken'],
        'clientType': 'cpdaily_student',
        'tenantId': api['tenantId'],
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': user['CpdailyInfo'],
        'RetrofitHeader': '8.0.8',
        'Cache-Control': 'max-age=0',
        'Host': 'open.cpdaily.com',
    }
    res = session.get(url='https://open.cpdaily.com/wec-open-app/app/userAppListGroupByCategory', headers=headers2)

    # 2.9 验证登陆
    # headers['SessionToken'] = user['SessionToken']
    # params = {
    #     'tgc': user['tgc'],
    #     'idsToken': user['idsToken'],
    # }
    # res = session.post(url='https://www.cpdaily.com/v6/auth/authentication/validation', headers=headers,
    #                    data=json.dumps(params))
    # print(res.text)

    # 3.4获取MOD_AUTH_CAS
    url = 'https://{host}/wec-counselor-collector-apps/stu/mobile/index.html?timestamp='.format(host=api['host']) + str(
        int(round(time.time() * 1000)))
    headers3 = {
        'Host': api['host'],
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 cpdaily/8.0.8 wisedu/8.0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'X-Requested-With': 'com.wisedu.cpdaily',
    }

    res = session.get(url=url, headers=headers3)
    # log(session.cookies)
    print('==============CpdailyInfo填写到index.py==============')
    print(user['CpdailyInfo'])
    print('==============Cookies填写到index.py==============')
    print(requests.utils.dict_from_cookiejar(session.cookies))


if __name__ == '__main__':
    login(config['user'])
    # getCpdailyInfo(config['user'])
