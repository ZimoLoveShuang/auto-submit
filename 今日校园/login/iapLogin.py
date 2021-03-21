import base64
import json
from io import BytesIO
import requests
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
from urllib3.exceptions import InsecureRequestWarning
from login.Utils import Utils

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class iapLogin:
    # 初始化iap登陆类
    def __init__(self, username, password, login_url, host, session):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.host = host
        self.session = session
        self.ltInfo = None
        self.count = 0

    # 判断是否需要验证码
    def getNeedCaptchaUrl(self):
        data = self.session.post(f'{self.host}iap/checkNeedCaptcha?username={self.username}', data=json.dumps({}),
                                 verify=False).json()
        return data['needCaptcha']

    # 获取验证码并解析
    def getCodeFromImg(self):
        imgUrl = f'{self.host}iap/generateCaptcha?ltId={self.ltInfo["result"]["_lt"]}'
        response = self.session.get(imgUrl, verify=False)  # 将这个图片保存在内存
        # 得到这个图片的base64编码
        imgCode = str(base64.b64encode(BytesIO(response.content).read()), encoding='utf-8')
        try:
            cred = credential.Credential(Utils.getYmlConfig()['SecretId'], Utils.getYmlConfig()['SecretKey'])
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

    def login(self):
        params = {}
        self.ltInfo = self.session.post(f'{self.host}iap/security/lt', data=json.dumps({})).json()
        params['lt'] = self.ltInfo['result']['_lt']
        params['rememberMe'] = 'false'
        params['dllt'] = ''
        params['mobile'] = ''
        params['username'] = self.username
        params['password'] = self.password
        needCaptcha = self.getNeedCaptchaUrl()
        if needCaptcha:
            print('正在解析验证码...')
            code = self.getCodeFromImg()
            params['captcha'] = code
        else:
            params['captcha'] = ''
        data = self.session.post(f'{ self.host }iap/doLogin', params=params, verify=False, allow_redirects=False)
        if data.status_code == 302:
            data = self.session.post(data.headers['Location'], verify=False)
            return self.session.cookies
        else:
            data = data.json()
            self.count += 1
            if data['resultCode'] == 'CAPTCHA_NOTMATCH':
                if self.count < 10:
                    self.login()
                else:
                    raise Exception('验证码错误超过10次，请检查')
            elif data['resultCode'] == 'FAIL_UPNOTMATCH':
                raise Exception('用户名密码不匹配，请检查')
            else:
                raise Exception('登陆出错，请联系开发者修复...')
