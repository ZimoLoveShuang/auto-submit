import requests


# 若离消息通知类
class RlMessage:
    # 初始化类
    def __init__(self, mail, wx):
        self.mail = mail
        self.wx = wx
    # 发送邮件消息
    def sendMail(self, status, msg):
        # 若离邮件api， 将会存储消息到数据库，并保存1周以供查看，请勿乱用，谢谢合作
        if self.mail == '':
            return '邮箱为空，已取消发送邮件！'
        api = 'http://mail.ruoli.cc/api/sendMail'
        params = {
            'to': self.mail,
            'title': f'[{status}]今日校园通知',
            'content': msg
        }
        res = requests.post(url=api, params=params).json()
        return res['msg']
    # Server酱Turbo通知
    def sendWX(self, status, msg):
        if self.wx=='':
            return '微信为空，已取消发送微信！'
        api = 'https://sctapi.ftqq.com/{wx}.send'.format(wx=self.wx)
        data = {
            'title': msg,
            "desp": f'[{status}]今日校园通知'
        }
        res=requests.post(api,data = data)
        return res.json()['data']['error']
