import json
import re

import requests
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
import base64
import yaml
from io import BytesIO
import random

from urllib3.exceptions import InsecureRequestWarning

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
    def getNeedcaptchaUrl(self):
        host = re.findall('\w{4,5}\:\/\/.*?\/', self.login_url)[0]
        url = host + 'authserver/needCaptcha.html' + '?username=' + self.username
        flag = self.session.get(url, verify=False).text
        return 'false' != flag and 'False' != flag

    # 读取yml配置
    def getYmlConfig(yaml_file='system.yml'):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        config = yaml.load(file_data, Loader=yaml.FullLoader)
        return dict(config)

    # 获取验证码并通过腾讯ocr解析
    def getCodeFromImg(self):
        imgUrl = self.host + 'authserver/captcha.html'
        response = self.session.get(imgUrl, verify=False)  # 将这个图片保存在内存
        # 得到这个图片的base64编码
        imgCode = str(base64.b64encode(BytesIO(response.content).read()), encoding='utf-8')
        # print(imgCode)
        try:
            cred = credential.Credential(self.getYmlConfig()['SecretId'], self.getYmlConfig()['SecretKey'])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)

            req = models.GeneralBasicOCRRequest()
            params = {
                "ImageBase64": imgCode
            }
            req.from_json_string(json.dumps(params))
            resp = client.GeneralBasicOCR(req)
            codeArray = json.loads(resp.to_json_string())['TextDetections']
            code = ''
            for item in codeArray:
                code += item['DetectedText'].replace(' ', '')
            if len(code) == 4:
                return code
            else:
                return self.getCodeFromImg()
        except TencentCloudSDKException as err:
            raise Exception('验证码识别出现问题了' + str(err.message))

    # 获取指定长度的随机字符
    def randString(self, length):
        baseString = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
        data = ''
        for i in range(length):
            data += baseString[random.randint(0, len(baseString) - 1)]
        return data

    # aes加密的实现
    def encryptAES(self, password, key):
        randStrLen = 64
        randIvLen = 16
        ranStr = self.randString(randStrLen)
        ivStr = self.randString(randIvLen)
        aes = AES.new(bytes(key, encoding='utf-8'), AES.MODE_CBC, bytes(ivStr, encoding="utf8"))
        data = ranStr + password

        text_length = len(data)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        data = data + pad * amount_to_pad

        text = aes.encrypt(bytes(data, encoding='utf-8'))
        text = base64.encodebytes(text)
        text = text.decode('utf-8').strip()
        return text

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
                raise Exception('出错啦！网页中未找到salt')
        needCaptcha = self.getNeedcaptchaUrl()
        if needCaptcha:
            code = self.getCodeFromImg()
            params['captchaResponse'] = code
        params['username'] = self.username
        params['password'] = self.encryptAES(self.password, salt)
        data = self.session.post(self.login_url, params=params, allow_redirects=False)
        # 如果等于302强制跳转，代表登陆成功
        if data.status_code == 302:
            jump_url = data.headers['Location']
            self.session.post(jump_url)
            return self.session.cookies
        elif data.status_code == 200:
            data = data.text
            soup = BeautifulSoup(data, 'lxml')
            msg = soup.select('#errorMsg')[0].get_text()
            raise Exception(msg)
        else:
            raise Exception('教务系统出现了问题啦！返回状态码：' + data.status_code)
