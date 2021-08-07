# -*- coding: utf-8 -*-
import sys
from urllib.parse import urlparse

import requests
import json
import uuid
import base64
from pyDes import des, CBC, PAD_PKCS5
from datetime import datetime, timedelta, timezone
import yaml
import time


# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()


# 获取今日校园api
def getCpdailyApis(user, debug=False):
    apis = {}
    schools = requests.get(url='https://mobile.campushoy.com/v6/config/guest/tenant/list', verify=not debug).json()['data']
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
            res = requests.get(url='https://mobile.campushoy.com/v6/config/guest/tenant/info', params=params,
                               verify=not debug)
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
                res = requests.get(url=apis['login-url'], verify=not debug)
                if urlparse(apis['login-url']).netloc != urlparse(res.url):
                    apis['login-url'] = res.url
            break
    if user['school'] == '云南财经大学':
        apis[
            'login-url'] = 'http://idas.ynufe.edu.cn/authserver/login?service=https%3A%2F%2Fynufe.cpdaily.com%2Fportal%2Flogin'
    if flag:
        log(user['school'] + ' 未找到该院校信息，请检查是否是学校全称错误')
        exit(-1)
    log(apis)
    return apis


# 读取yml配置
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


# DES加密
def DESEncrypt(s, key='ST83=@XV'):
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    encrypt_str = k.encrypt(s)
    return base64.b64encode(encrypt_str).decode()


# DES解密
def DESDecrypt(s, key='ST83=@XV'):
    s = base64.b64decode(s)
    iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    return k.decrypt(s)

# Accept config file path from argv[2]
# TODO: Do this in main()
config_file = sys.argv[2] if len(sys.argv) > 2 else 'config.yml'

# 全局配置
config = getYmlConfig(config_file)
session = requests.session()
user = config['user']
# Cpdaily-Extension
extension = {
    "lon": user['lon'],
    "model": "iPhone10,1",
    "appVersion": "8.2.14",
    "systemVersion": "13.3.1",
    "userId": user['username'],
    "systemName": "iOS",
    "lat": user['lat'],
    "deviceId": str(uuid.uuid1())
}
CpdailyInfo = DESEncrypt(json.dumps(extension))
apis = getCpdailyApis(user)
host = apis['host']


# 获取验证码
def getMessageCode():
    log('正在获取验证码')
    headers = {
        'SessionToken': 'szFn6zAbjjU=',
        'clientType': 'cpdaily_student',
        'tenantId': apis['tenantId'],
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
        'RetrofitHeader': '8.2.14',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'mobile.campushoy.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    params = {
        'mobile': DESEncrypt(str(user['tellphone']))
    }
    url = 'https://mobile.campushoy.com/v6/auth/authentication/mobile/messageCode'
    res = session.post(url=url, headers=headers, data=json.dumps(params))
    errMsg = res.json()['errMsg']
    if errMsg != None:
        log(errMsg)
        log(res.json())
        #exit(-1)
    log('获取验证码成功')


# 手机号登陆
def mobileLogin(code):
    log('正在验证验证码')
    headers = {
        'SessionToken': 'szFn6zAbjjU=',
        'clientType': 'cpdaily_student',
        'tenantId': apis['tenantId'],
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
        'RetrofitHeader': '8.2.14',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'mobile.campushoy.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    params = {
        'loginToken': str(code),
        'loginId': str(user['tellphone'])
    }
    url = 'https://mobile.campushoy.com/v6/auth/authentication/mobileLogin'
    res = session.post(url=url, headers=headers, data=json.dumps(params))
    errMsg = res.json()['errMsg']
    if errMsg != None:
        log(errMsg)
        # exit(-1)
    log('验证码验证成功')
    return res.json()['data']


# 验证登陆信息
def validation(data):
    log('正在验证登陆信息')
    sessionToken = data['sessionToken']
    tgc = data['tgc']
    headers = {
        'SessionToken': DESEncrypt(sessionToken),
        'clientType': 'cpdaily_student',
        'tenantId': apis['tenantId'],
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
        'RetrofitHeader': '8.2.14',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'mobile.campushoy.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'Cookie': 'sessionToken=' + sessionToken
    }
    params = {
        'tgc': DESEncrypt(tgc)
    }
    url = 'https://mobile.campushoy.com/v6/auth/authentication/new/validation'
    res = session.post(url=url, headers=headers, data=json.dumps(params))
    errMsg = res.json()['errMsg']
    if errMsg != None:
        log(errMsg)
        exit(-1)
    log('验证登陆信息成功')
    return res.json()['data']


# 更新acw_tc
def updateACwTc(data):
    log('正在更新acw_tc')
    sessionToken = data['sessionToken']
    tgc = data['tgc']
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
    headers = {
        'TGC': DESEncrypt(tgc),
        'AmpCookies': DESEncrypt(json.dumps(amp)),
        'SessionToken': DESEncrypt(sessionToken),
        'clientType': 'cpdaily_student',
        'tenantId': apis['tenantId'],
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
        'RetrofitHeader': '8.2.14',
        'Cache-Control': 'max-age=0',
        'Host': host,
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    url = 'https://{host}/wec-portal-mobile/client/userStoreAppList'.format(host=host)
    # 清除cookies
    # session.cookies.clear()
    session.get(url=url, headers=headers, allow_redirects=False)
    log('更新acw_tc成功')


# 获取MOD_AUTH_CAS
def getModAuthCas(data):
    log('正在获取MOD_AUTH_CAS')
    sessionToken = data['sessionToken']
    headers = {
        'Host': host,
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 cpdaily/8.2.14 wisedu/8.2.14',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'X-Requested-With': 'com.wisedu.cpdaily'
    }
    url = 'https://{host}/wec-counselor-sign-apps/stu/mobile/index.html?timestamp='.format(host=host) + str(
        int(round(time.time() * 1000)))
    res = session.get(url=url, headers=headers, allow_redirects=False)
    location = res.headers['location']
    # print(location)
    headers2 = {
        'Host': 'mobile.campushoy.com',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 cpdaily/8.2.14 wisedu/8.2.14',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Cookie': 'clientType=cpdaily_student; tenantId=' + apis['tenantId'] + '; sessionToken=' + sessionToken,
    }
    res = session.get(url=location, headers=headers2, allow_redirects=False)
    location = res.headers['location']
    # print(location)
    session.get(url=location, headers=headers)
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    if 'MOD_AUTH_CAS' not in cookies:
        log('获取MOD_AUTH_CAS失败')
        exit(-1)
    log('获取MOD_AUTH_CAS成功')


# 通过手机号和验证码进行登陆
def login(dest="session.yml"):
    # 1. 获取验证码
    getMessageCode()
    code = input("请输入验证码：")
    # 2. 手机号登陆
    data = mobileLogin(code)
    # 3. 验证登陆信息
    data = validation(data)
    # 4. 更新acw_tc
    updateACwTc(data)
    # 5. 获取mod_auth_cas
    getModAuthCas(data)
    print('==============sessionToken==============')
    sessionToken = data['sessionToken']
    print(sessionToken)
    print('==============CpdailyInfo==============')
    print(CpdailyInfo)
    print('==============Cookies==============')
    print(requests.utils.dict_from_cookiejar(session.cookies))
    # Save session data
    session_data = {
        "sessionToken": sessionToken,
        "CpdailyInfo": CpdailyInfo,
        "Cookies": requests.utils.dict_from_cookiejar(session.cookies)
    }
    print('正在写入 {} ...'.format(dest))
    with open(dest, 'w') as f:
        yaml.dump(session_data, f, allow_unicode=True)

if __name__ == '__main__':
    session_file = "session.yml"
    try:
        session_file = sys.argv[1]
    except:
        pass
    login(session_file)
