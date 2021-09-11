import requests


# 若离消息通知类
class RlMessage:
    # 初始化类
    def __init__(self, mail, sc, pp):
        self.mail = mail
        self.sc = sc
        self.pp = pp
    # 发送推送总模块
    def send(self,status,msg):
       result=[]
       result.append(RlMessage.sendMail(self, status, msg)) 
       result.append(RlMessage.sendSC(self, status, msg)) 
       result.append(RlMessage.sendPP(self, status, msg)) 
       return '\n'.join(result)

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
    def sendSC(self, status, msg):
        if self.sc=='':
            return 'SC为空，已取消发送微信！'
        api = f'https://sctapi.ftqq.com/{self.sc}.send'
        data = {
            'title': msg,
            "desp": f'[{status}]今日校园通知'
        }
        res=requests.post(api,data = data)
        return res.json()['data']['error']
    # Pushplus推送
    def sendPP(self, status, msg):
        if self.pp=='':
            return 'PP为空，已取消发送PushPlus！'
        api = 'http://www.pushplus.plus/send'
        data = {
            'token': self.pp,
            'title': f'[{status}]今日校园通知',
            "content": msg
        }
        res=requests.post(api,data = data)
        return res.json()['msg']