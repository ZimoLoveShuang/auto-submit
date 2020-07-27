# 获取不到MOD_AUTH_CAS
import re
import time
import requests
from fzu.utils import *
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# 全局配置
config = getYmlConfig('config.yml')
user = config['user']
session = requests.session()


# 获取今日校园api
def getCpdailyApis():
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
    print('今日校园api')
    print(apis)
    return apis


# 获取登陆参数
def getLoginParams(html):
    soup = BeautifulSoup(html, 'html5lib')

    # 获取加密盐
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
    # 获取表单参数
    casLoginForm = soup.find(id='casLoginForm')
    inputs = casLoginForm.find_all('input')
    params = {}
    for inp in inputs:
        attrs = inp.attrs
        if 'value' in attrs and 'name' in attrs:
            params[attrs['name']] = attrs['value']
    params['username'] = user['username']
    if salt == None:
        params['password'] = user['password']
    else:
        params['password'] = AESEncrypt(user['password'], salt)
    print('登陆参数')
    print(params)
    return params


# 发送登陆请求，获取ticket
def getTicket(url, params):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    }
    res = session.post(url=url, headers=headers, data=params)
    # 没有被禁用云端系统的NOTCLOUD学校模拟登陆到这里就可以了
    # 获取到ticket
    parse = urlparse(res.url)
    ticket = parse.fragment[len('mobile_token='):]
    print('ticket')
    print(ticket)
    print(session.cookies)
    return ticket


# 进行notcloudlogin，获取到电话号码
def notcloudlogin(CpdailyInfo, ticket, tenantId):
    params = {
        'tenantId': tenantId,
        'ticket': DESEncrypt(ticket),
    }
    headers = {
        'SessionToken': DESEncrypt(''),
        'clientType': 'cpdaily_student',
        'tenantId': tenantId,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
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
    print('电话号码')
    print(mobile)
    print(session.cookies)
    return mobile


# 发送验证码
def sendMessageCode(CpdailyInfo, tenantId, mobile):
    headers = {
        'SessionToken': DESEncrypt(''),
        'clientType': 'cpdaily_student',
        'tenantId': tenantId,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
        'RetrofitHeader': '8.0.8',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'www.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    params = {
        'mobile': DESEncrypt(mobile)
    }
    res = session.post(url='https://www.cpdaily.com/v6/auth/deviceChange/mobile/messageCode', headers=headers,
                       data=json.dumps(params))
    print('发送验证码')
    print(res.text)
    errMsg = res.json()['errMsg']
    if errMsg != None:
        log(errMsg)
        exit(-1)


# 验证验证码，返回用户信息
def validateMessageCode(messageCode, ticket, mobile, tenantId, CpdailyInfo):
    headers = {
        'SessionToken': DESEncrypt(''),
        'clientType': 'cpdaily_student',
        'tenantId': tenantId,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
        'RetrofitHeader': '8.0.8',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'www.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    params = {
        'messageCode': messageCode,
        'ticket': DESEncrypt(ticket),
        'mobile': mobile,
    }
    res = session.post(url='https://www.cpdaily.com/v6/auth/deviceChange/validateMessageCode', headers=headers,
                       data=json.dumps(params))
    data = res.json()['data']
    print('验证验证码')
    print(res.text)
    return data


# 更新acw_tc
def updateAcwTc(data, CpdailyInfo, tenantId, host):
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
    headers = {
        'TGC': DESEncrypt(tgc),
        'AmpCookies': DESEncrypt(json.dumps(amp)),
        'SessionToken': DESEncrypt(sessionToken),
        'clientType': 'cpdaily_student',
        'tenantId': tenantId,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
        'RetrofitHeader': '8.0.8',
        'Cache-Control': 'max-age=0',
        'Host': host,
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'If-Modified-Since': str(getNowGMTTIme())
    }
    res = session.get(url='https://{host}/wec-portal-mobile/client/userStoreAppList'.format(host=host),
                      headers=headers, allow_redirects=False)
    print('更新acw_tc')
    print(session.cookies)
    # print(res.headers)
    # print(res.headers['Set-Cookie'])


# 验证登陆
def validation(data, tenantId, CpdailyInfo, ticket):
    tgc = data['tgc']
    sessionToken = data['sessionToken']
    params = {
        'tgc': DESEncrypt(tgc),
        'idsToken': DESEncrypt(ticket),
    }
    headers = {
        'SessionToken': DESEncrypt(sessionToken),
        'clientType': 'cpdaily_student',
        'tenantId': tenantId,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.8.1',
        'deviceType': '1',
        'CpdailyStandAlone': '0',
        'CpdailyInfo': CpdailyInfo,
        'RetrofitHeader': '8.0.8',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'www.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    res = session.post(url='https://www.cpdaily.com/v6/auth/authentication/validation', headers=headers,
                       data=json.dumps(params))
    print('验证登陆')
    print(res.text)
    return res.json()['data']


# 获取MOD_AUTH_CAS
def getModAuthCas(host):
    url = 'https://{host}/wec-counselor-collector-apps/stu/mobile/index.html?timestamp='.format(host=host) + str(
        int(round(time.time() * 1000)))
    headers = {
        'Host': host,
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 cpdaily/8.0.8 wisedu/8.0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'X-Requested-With': 'com.wisedu.cpdaily',
    }
    res = session.get(url=url, headers=headers)
    print('获取MOD_AUTH_CAS')
    print(res.headers)
    # location = res.headers['location']
    # res = session.get(url=location, headers=headers, allow_redirects=False)
    print(res.headers)
    print(res.text)
    print(requests.utils.dict_from_cookiejar(session.cookies))


# 登陆过程
def login(user):
    # 0. 生成CpdailyInfo
    CpdailyInfo = getCpdailyInfo(user)
    # 1. 获取api
    api = getCpdailyApis()
    # 2. 请求登陆页，获取登陆参数
    res = session.get(url=api['login-url'])
    html = res.text
    params = getLoginParams(html)
    # 3. 发送登陆请求，获取到ticket参数
    ticket = getTicket(api['login-url'], params)
    # 4. 发起notcloudlogin，获取电话号码
    mobile = notcloudlogin(CpdailyInfo, ticket, api['tenantId'])
    # 5. 设备更改发送验证码
    sendMessageCode(CpdailyInfo, api['tenantId'], mobile)
    # 6. 验证验证码，返回用户信息
    messageCode = input('请输入验证码：')
    data = validateMessageCode(messageCode, ticket, mobile, api['tenantId'], CpdailyInfo)
    # 7. 更新acw_tc
    updateAcwTc(data, CpdailyInfo, api['tenantId'], api['host'])
    # 8. 验证登陆
    # validation(data, api['tenantId'], CpdailyInfo, ticket)
    # 9. 获取MOD_AUTH_CAS
    getModAuthCas(api['host'])

    print('==============CpdailyInfo填写到index.py==============')
    print(CpdailyInfo)
    print('==============Cookies填写到index.py==============')
    print(requests.utils.dict_from_cookiejar(session.cookies))


if __name__ == '__main__':
    login(config['user'])
    # getCpdailyInfo(config['user'])
