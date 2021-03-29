import base64
import json
import re
import uuid
from pyDes import PAD_PKCS5, des, CBC
from requests_toolbelt import MultipartEncoder

from todayLoginService import TodayLoginService


class sleepCheck:
    # 初始化信息收集类
    def __init__(self, todaLoginService: TodayLoginService, userInfo):
        self.session = todaLoginService.session
        self.host = todaLoginService.host
        self.userInfo = userInfo
        self.taskInfo = None
        self.form = {}
    # 获取未签到任务
    def getUnSignedTasks(self):
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        # 第一次请求接口获取cookies（MOD_AUTH_CAS）
        url = f'{self.host}wec-counselor-attendance-apps/student/attendance/getStuAttendacesInOneDay'
        self.session.post(url, headers=headers, data=json.dumps({}), verify=False)
        # 第二次请求接口，真正的拿到具体任务
        res = self.session.post(url, headers=headers, data=json.dumps({}), verify=False).json()
        if len(res['datas']['unSignedTasks']) < 1:
            raise Exception('当前暂时没有未签到的任务哦！')
        # 获取最后的一个任务
        latestTask = res['datas']['unSignedTasks'][0]
        self.taskInfo = {
            'signInstanceWid': latestTask['signInstanceWid'],
            'signWid': latestTask['signWid']
        }

    # 获取具体的签到任务详情
    def getDetailTask(self):
        url = f'{self.host}wec-counselor-attendance-apps/student/attendance/detailSignInstance'
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        res = self.session.post(url, headers=headers, data=json.dumps(self.taskInfo), verify=False).json()
        self.task = res['datas']

    # 上传图片到阿里云oss
    def uploadPicture(self):
        url = f'{self.host}wec-counselor-sign-apps/stu/oss/getUploadPolicy'
        res = self.session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps({'fileType': 1}),
                                verify=False)
        datas = res.json().get('datas')
        fileName = datas.get('fileName')
        policy = datas.get('policy')
        accessKeyId = datas.get('accessid')
        signature = datas.get('signature')
        policyHost = datas.get('host')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'
        }
        multipart_encoder = MultipartEncoder(
            fields={  # 这里根据需要进行参数格式设置
                'key': fileName, 'policy': policy, 'OSSAccessKeyId': accessKeyId, 'success_action_status': '200',
                'signature': signature,
                'file': ('blob', open(self.userInfo['photo'], 'rb'), 'image/jpg')
            })
        headers['Content-Type'] = multipart_encoder.content_type
        res = self.session.post(url=policyHost,
                                headers=headers,
                                data=multipart_encoder)
        self.fileName = fileName

    # 获取图片上传位置
    def getPictureUrl(self):
        url = f'{self.host}wec-counselor-sign-apps/stu/sign/previewAttachment'
        params = {'ossKey': self.fileName}
        res = self.session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps(params),
                                verify=False)
        photoUrl = res.json().get('datas')
        return photoUrl


    # 填充表单
    def fillForm(self):
        # 判断签到是否需要照片
        if self.task['isPhoto'] == 1:
            self.uploadPicture()
            self.form['signPhotoUrl'] = self.getPictureUrl()
        else:
            self.form['signPhotoUrl'] = ''
        self.form['signInstanceWid'] = self.taskInfo['signInstanceWid']
        self.form['longitude'] = self.userInfo['lon']
        self.form['latitude'] = self.userInfo['lat']
        self.form['isMalposition'] = self.task['isMalposition']
        self.form['abnormalReason'] = self.userInfo['abnormalReason']
        self.form['position'] = self.userInfo['address']
        self.form['qrUuid'] = ''
        self.form['uaIsCpadaily'] = True


    # DES加密
    def DESEncrypt(self, s, key='b3L26XNL'):
        key = key
        iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        encrypt_str = k.encrypt(s)
        return base64.b64encode(encrypt_str).decode()

    # 提交签到信息
    def submitForm(self):
        extension = {
            "model": "OPPO R11 Plus",
            "appVersion": "8.1.14",
            "systemVersion": "4.4.4",
            "userId": self.userInfo['username'],
            "systemName": "android",
            "lat": self.userInfo['lat'],
            "lon": self.userInfo['lon'],
            "deviceId": str(uuid.uuid1())
        }
        headers = {
            'User-Agent': self.session.headers['User-Agent'],
            'CpdailyStandAlone': '0',
            'extension': '1',
            'Cpdaily-Extension': self.DESEncrypt(json.dumps(extension)),
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Encoding': 'gzip',
            'Host': re.findall('//(.*?)/', self.host)[0],
            'Connection': 'Keep-Alive'
        }
        print(json.dumps(self.task))
        print(json.dumps(self.form))
        res = self.session.post(f'{self.host}wec-counselor-attendance-apps/student/attendance/submitSign', headers=headers,
                                data=json.dumps(self.form), verify=False).json()
        return res['message']
