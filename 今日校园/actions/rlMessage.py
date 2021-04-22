import requests


# 若离消息通知类
class RlMessage:
    # 初始化类
    def __init__(self, mail, apiUrl):
        self.mail = mail
        self.apiUrl = apiUrl

    # 发送邮件消息
    def sendMail(self, status, msg):
        # 若离邮件api， 将会存储消息到数据库，并保存1周以供查看，请勿乱用，谢谢合作
        if self.mail == '':
            return '邮箱为空，已取消发送邮件！'
        params = {
            'to': self.mail,
            'title': f'[{status}]今日校园通知',
            'content': msg
        }
        res = requests.post(url=self.apiUrl, params=params).json()
        return res['msg']
    # 其他通知方式待添加
