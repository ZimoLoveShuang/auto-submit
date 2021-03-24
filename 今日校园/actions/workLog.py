import base64
import json
import re
import uuid
from pyDes import PAD_PKCS5, des, CBC
import time

from todayLoginService import TodayLoginService


# 教师工作日志类
class workLog:
    # 初始化顶底工作日志类
    def __init__(self, todayLoginService: TodayLoginService, userInfo):
        self.session = todayLoginService.session
        self.host = todayLoginService.host
        self.userInfo = userInfo
        self.collectWid = None
        self.formWids = []
        self.forms = []
        self.session.headers = {
            'User-Agent': self.session.headers['User-Agent'],
            'Content-type': 'application/json; charset=utf-8;'
        }

    # 检查是否存在已创建且未提交的模板
    def checkHasLog(self):
        # 首先 获取 templateName=疫情采集（每天上报）新 的wid：37
        url = f'{self.host}wec-counselor-worklog-apps/worklog/template/listActiveTemplate'
        params = {
            'pageNumber': '1',
            'pageSize': '9999999',
            'status': '1'
        }
        res = self.session.post(url, data=json.dumps(params), verify=False).json()
        self.collectWid = res['datas']['rows'][0]['wid']
        url = f'{self.host}wec-counselor-worklog-apps/worklog/list'
        params = {
            'formWid': self.collectWid,
            'pageNumber': '1',
            'pageSize': '20'
        }
        res = self.session.post(url, data=json.dumps(params), verify=False).json()
        for item in res['datas']['rows']:
            if item['status'] == 0:
                self.formWids.append(item['wid'])

    # 通过wid获取表单信息
    def getFormsByWids(self):
        # 如果不存在已经创建好的模板，那么就自己创建一个模板
        if len(self.formWids) == 0:
            self.createFormTemplate()
        for wid in self.formWids:
            url = f'{self.host}wec-counselor-worklog-apps/worklog/detail'
            params = {
                'wid': wid
            }
            res = self.session.post(url, data=json.dumps(params), verify=False).json()
            self.forms.append(res['datas']['form'])

    # 填充表单
    def fillForms(self):
        userItems = self.userInfo['forms']
        for form in self.forms[:]:
            # 由于无法判断有没有签到选项，使用个i来作为下标索引
            i = 0
            for pos, formItem in enumerate(form):
                # 只填写必填项
                if formItem['isRequired']:
                    # 判断一下是否是签到选项
                    if formItem['signScopeWids'] != '':
                        # 如果是签到选项
                        # 新的代码
                        form = self.submitSign(formItem['wid'], self.formWids[pos])
                        # 以下代码已放弃，应该是先去请求地点签到api
                        # value = {
                        #     "isInSignScope": False,
                        #     "lat": "%.6f" % float(formItem['templateScopes'][0]['latitude']),
                        #     "lon": "%.6f" % float(formItem['templateScopes'][0]['longitude']),
                        #     "signDate": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                        #     "signPlace": formItem['templateScopes'][0]["address"]
                        # }
                        # formItem['value'] = str(value)
                    else:
                        # 判断是否需要检查标题
                        if self.userInfo['checkTitle'] == 1:
                            if userItems[i]['form']['title'] != formItem['title']:
                                raise Exception(
                                    f'\r\n第{i + 1}个配置出错了\r\n您的标题为：{userItems[i]["form"]["title"]}\r\n系统的标题为：{formItem["title"]}')
                        # 文本选项直接赋值
                        formItem['value'] = userItems[i]['form']['value']
                        i += 1
                else:
                    pass
                formItem.pop('fieldItems')

    # DES加密
    def DESEncrypt(self, s, key='b3L26XNL'):
        key = key
        iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        encrypt_str = k.encrypt(s)
        return base64.b64encode(encrypt_str).decode()

    # 地点签到
    def submitSign(self, fieldWid, worklogWid):
        extension = {
            "lon": self.userInfo['lon'],
            "model": "OPPO R11 Plus",
            "appVersion": "8.1.14",
            "systemVersion": "4.4.4",
            "userId": self.userInfo['username'],
            "systemName": "android",
            "lat": self.userInfo['lat'],
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
        url = f'{self.host}wec-counselor-worklog-apps/worklog/sign/submitSign'
        params = {
            "fieldWid": fieldWid,
            "worklogWid": worklogWid,
            "signPlace": self.userInfo['address'],
            "longitude": self.userInfo['lon'],
            "latitude": self.userInfo['lat']
        }
        res = self.session.post(url, data=json.dumps(params), headers=headers, verify=False).json()
        if res['message'] == 'SUCCESS':
            url = f'{self.host}wec-counselor-worklog-apps/worklog/detail'
            params = {
                'wid': worklogWid
            }
            res = self.session.post(url, data=json.dumps(params), verify=False).json()
            form = res['datas']['form']
            return form
        else:
            raise Exception('定位信息提交失败，请联系开发者反馈BUG')

    # 提交表单
    def submitForms(self):
        result = []
        for i, wid in enumerate(self.formWids):
            form = self.forms[i]
            params = {
                'formWid': self.collectWid,
                'wid': wid,
                'form': form,
                'operationType': 1
            }
            res = self.session.post(f'{self.host}wec-counselor-worklog-apps/worklog/update', data=json.dumps(params),
                                    verify=False).json()
            result.append(res['message'])
        return result

    # 创建模板
    def createFormTemplate(self):
        # 获取模板
        params = {
            'formWid': self.collectWid
        }
        res = self.session.post(f'{self.host}wec-counselor-worklog-apps/worklog/template/detail',
                                data=json.dumps(params), verify=False).json()
        formTemplate = res['datas']['content']
        for formItem in formTemplate:
            formItem.pop('fieldItems')
            formItem['value'] = ""
        params = {
            'form': formTemplate,
            'formWid': str(self.collectWid),
            'operationType': 0
        }
        res = self.session.post(f'{self.host}wec-counselor-worklog-apps/worklog/update', data=json.dumps(params)).json()
        if res['message'] == 'SUCCESS':
            self.formWids.append(res['datas']['wid'])
        else:
            raise Exception('创建模板失败，请联系开发者反馈BUG')
