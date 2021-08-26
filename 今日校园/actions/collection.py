import base64
import json
import re
import uuid
from typing import Optional, List, Text, Callable

from pyDes import PAD_PKCS5, des, CBC

from todayLoginService import TodayLoginService


class UserForms:
    forms: List

    def __init__(self, forms):
        self.forms = forms

    def getValueByTitle(self, title: str, raiseIfNotFound: bool = False) -> Optional[Text]:
        """
        通过问题的标题来查找对应答案
        :param title: 标题
        :param raiseIfNotFound: 未找到对应选项时是否抛出异常
        :return: 答案
        """
        if ret := list(filter(lambda x: x['form']['title'] == title, self.forms)):
            return ret[0]['form']['value']

        if raiseIfNotFound:
            raise Exception(f"config.yml 中不存在 '{title}' 的答案")
        else:
            return None

    def getValueByIndex(self, idx: int) -> str:
        """
        通过问题的索引来查找对应答案，适用于 checkTitle 选项为 False 且 getValueByTitle 查找失败的情况
        :param idx: 索引
        :return: 答案
        """
        try:
            return self.forms[idx]['form']['value']
        except IndexError:
            raise IndexError(f"config.yml 中不存在表单第 [{idx}] 个问题的答案")


class FormItem(dict):
    """
    表单中的一个问题
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.get('fieldType'), f"字段读取错误，缺少 fieldType，原始内容：{self}"
        self.acceptableFieldItems = self['fieldItems']

    @property
    def isRequired(self) -> bool:
        return bool(self['isRequired'])

    @property
    def fieldType(self) -> int:
        return int(self['fieldType'])

    @property
    def isTextField(self) -> bool:
        """
        是文字型问题
        :return:
        """
        return self.fieldType == 1 or self.fieldType == 5

    @property
    def isSingleChoiceField(self) -> bool:
        return self.fieldType == 2

    @property
    def isMultiChoiceField(self) -> bool:
        return self.fieldType == 3

    @property
    def isIgnoredChoiceField(self) -> bool:
        return self.fieldType == 4

    def getValueSetterByFieldType(self) -> Callable:
        """
        根据表单类型取得对应 setter
        :return:
        """
        if self.isTextField:
            return self._setTextValue
        elif self.isSingleChoiceField:
            return self._setSingleChoiceValue
        elif self.isMultiChoiceField:
            return self._setMultiChoiceValue
        elif self.isIgnoredChoiceField:
            return lambda newValue: None
        else:
            raise ValueError(f"未知问题类型，原始数据：{self}")

    @property
    def value(self) -> Text:
        return self['value']

    @value.setter
    def value(self, newValue: Text):
        setter = self.getValueSetterByFieldType()
        setter(newValue)

    def _setTextValue(self, newValue: Text):
        """
        填充 文本型问题 的答案
        :param newValue:
        :return:
        """
        self['value'] = newValue

    def _setSingleChoiceValue(self, newValue: Text):
        """
        填充 单选型问题 的答案
        :param newValue:
        :return:
        """
        self['value'] = newValue
        # 仅保留与用户回答相同的 fieldItem
        self['fieldItems'] = list(filter(lambda x: x['content'] == newValue, self.acceptableFieldItems))
        assert len(self['fieldItems']) == 1, f"单选问题 {self['title']} 实际获得了 {len(self['fieldItems'])} 个答案"

    def _setMultiChoiceValue(self, newValue: Text):
        userChoices = newValue.split("|")
        # 先筛选出用户选择的选项
        finalSelectedFieldItems = list(filter(lambda field: field['content'] in userChoices, self.acceptableFieldItems))
        self['fieldItems'] = finalSelectedFieldItems
        self['value'] = " ".join(list(map(lambda fieldItem: fieldItem['content'], finalSelectedFieldItems)))


class Collection:
    # 初始化信息收集类
    def __init__(self, todayLoginService: TodayLoginService, userInfo):
        self.session = todayLoginService.session
        self.host = todayLoginService.host
        self.userInfo = userInfo
        self.form: Optional[List] = None
        self.collectWid = None
        self.formWid = None
        self.schoolTaskWid = None

    # 查询表单
    def queryForm(self):
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        queryUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'
        params = {
            'pageSize': 6,
            "pageNumber": 1
        }
        res = self.session.post(queryUrl, data=json.dumps(params), headers=headers, verify=False).json()
        if len(res['datas']['rows']) < 1:
            raise Exception('查询表单失败，请确认你是信息收集并且当前有收集任务。确定请联系开发者')
        self.collectWid = res['datas']['rows'][0]['wid']
        self.formWid = res['datas']['rows'][0]['formWid']
        detailUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/detailCollector'
        res = self.session.post(detailUrl, headers=headers, data=json.dumps({'collectorWid': self.collectWid}),
                                verify=False).json()
        self.schoolTaskWid = res['datas']['collector']['schoolTaskWid']
        getFormUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/getFormFields'
        params = {"pageSize": 100, "pageNumber": 1, "formWid": self.formWid, "collectorWid": self.collectWid}
        res = self.session.post(getFormUrl, headers=headers, data=json.dumps(params), verify=False).json()
        self.form = res['datas']['rows']

    # 填写表单
    def fillForm(self):
        # 最终 finalFormItems，独立出来是为了防止在遍历过程中修改被遍历的内容，这可能会造成指针混乱或者修改不生效
        finalFormItems: List[FormItem] = []

        # 用户预设的，对问题的回答
        userForms = UserForms(self.userInfo['forms'])

        # 使用 FormItem 类初始化原始表单
        forms = map(lambda formItemDict: FormItem(formItemDict), self.form)

        # 仅处理必填
        requiredForms = filter(lambda formItem: formItem.isRequired, forms)

        for idx, formItem in enumerate(requiredForms):
            # 取得用户期望的回答
            answerValue = userForms.getValueByTitle(formItem['title'], raiseIfNotFound=self.userInfo['checkTitle'])
            if answerValue is None:
                answerValue = userForms.getValueByIndex(idx)
            formItem.value = answerValue
            finalFormItems.append(formItem)

        self.form = finalFormItems

    # 提交表单
    def submitForm(self):
        extension = {
            "model": "OPPO R11 Plus",
            "appVersion": "8.2.14",
            "systemVersion": "9.1.0",
            "userId": self.userInfo['username'],
            "systemName": "android",
            "lon": self.userInfo['lon'],
            "lat": self.userInfo['lat'],
            "deviceId": str(uuid.uuid1())
        }

        headers = {
            'User-Agent': self.session.headers['User-Agent'],
            'CpdailyStandAlone': '0',
            'extension': '1',
            'Cpdaily-Extension': self.DESEncrypt(json.dumps(extension)),
            'Content-Type': 'application/json; charset=utf-8',
            # 请注意这个应该和配置文件中的host保持一致
            'Host': re.findall('//(.*?)/', self.host)[0],
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        params = {
            "formWid": self.formWid, "address": self.userInfo['address'], "collectWid": self.collectWid,
            "schoolTaskWid": self.schoolTaskWid, "form": self.form, "uaIsCpadaily": True
        }
        submitUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/submitForm'
        data = self.session.post(submitUrl, headers=headers, data=json.dumps(params), verify=False).json()
        return data['message']

    # DES加密
    def DESEncrypt(self, content):
        key = 'b3L26XNL'
        iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        encrypt_str = k.encrypt(content)
        return base64.b64encode(encrypt_str).decode()
