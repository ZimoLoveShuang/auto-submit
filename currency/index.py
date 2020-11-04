# -*- coding: utf-8 -*-
import oss2
from login import *

############配置############
Cookies = {
    'acw_tc': '需要填写内容！！！',
    'MOD_AUTH_CAS': '需要填写内容！！！',
}
sessionToken = '需要填写内容！！！'
CpdailyInfo = '需要填写内容！！！'
############配置############

# 全局
session = requests.session()
session.cookies = requests.utils.cookiejar_from_dict(Cookies)
config = getYmlConfig('config.yml')
user = config['user']
host = getCpdailyApis(user)['host']


# 查询表单
def queryForm():
    data = {
        'sessionToken': sessionToken
    }
    getModAuthCas(data)
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    queryCollectWidUrl = 'https://{host}/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'.format(
        host=host)
    params = {
        'pageSize': 6,
        'pageNumber': 1
    }
    res = session.post(queryCollectWidUrl, headers=headers, data=json.dumps(params))
    if len(res.json()['datas']['rows']) < 1:
        return None

    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    detailCollector = 'https://{host}/wec-counselor-collector-apps/stu/collector/detailCollector'.format(host=host)
    res = session.post(url=detailCollector, headers=headers,
                       data=json.dumps({"collectorWid": collectWid}))
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    getFormFields = 'https://{host}/wec-counselor-collector-apps/stu/collector/getFormFields'.format(host=host)
    res = session.post(url=getFormFields, headers=headers, data=json.dumps(
        {"pageSize": 100, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form = res.json()['datas']['rows']
    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(form):
    sort = 1
    for formItem in form:
        # 只处理必填项
        if formItem['isRequired'] == 1:
            default = config['cpdaily']['defaults'][sort - 1]['default']
            if formItem['title'] != default['title']:
                log('第%d个默认配置不正确，请检查' % sort)
                log(formItem['title'] + default['title'])
                exit(-1)
            # 文本直接赋值
            if formItem['fieldType'] == 1:
                formItem['value'] = default['value']
            # 单选框需要删掉多余的选项
            if formItem['fieldType'] == 2:
                # 填充默认值
                formItem['value'] = default['value']
                fieldItems = formItem['fieldItems']
                for i in range(0, len(fieldItems))[::-1]:
                    if fieldItems[i]['content'] != default['value']:
                        del fieldItems[i]
            # 多选需要分割默认选项值，并且删掉无用的其他选项
            if formItem['fieldType'] == 3:
                fieldItems = formItem['fieldItems']
                defaultValues = default['value'].split(',')
                for i in range(0, len(fieldItems))[::-1]:
                    flag = True
                    for j in range(0, len(defaultValues))[::-1]:
                        if fieldItems[i]['content'] == defaultValues[j]:
                            # 填充默认值
                            formItem['value'] += defaultValues[j] + ' '
                            flag = False
                    if flag:
                        del fieldItems[i]
            # 图片需要上传到阿里云oss
            if formItem['fieldType'] == 4:
                fileName = uploadPicture(default['value'])
                formItem['value'] = getPictureUrl(fileName)
            log('必填问题%d：' % sort + formItem['title'])
            log('答案%d：' % sort + formItem['value'])
            sort += 1
    return form


# 上传图片到阿里云oss
def uploadPicture(image):
    url = 'https://{host}/wec-counselor-collector-apps/stu/collector/getStsAccess'.format(host=host)
    res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps({}))
    datas = res.json().get('datas')
    fileName = datas.get('fileName')
    accessKeyId = datas.get('accessKeyId')
    accessSecret = datas.get('accessKeySecret')
    securityToken = datas.get('securityToken')
    endPoint = datas.get('endPoint')
    bucket = datas.get('bucket')
    bucket = oss2.Bucket(oss2.Auth(access_key_id=accessKeyId, access_key_secret=accessSecret), endPoint, bucket)
    with open(image, "rb") as f:
        data = f.read()
    bucket.put_object(key=fileName, headers={'x-oss-security-token': securityToken}, data=data)
    res = bucket.sign_url('PUT', fileName, 60)
    # log(res)
    return fileName


# 获取图片上传位置
def getPictureUrl(fileName):
    url = 'https://{host}/wec-counselor-collector-apps/stu/collector/previewAttachment'.format(host=host)
    data = {
        'ossKey': fileName
    }
    res = session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps(data), verify=False)
    photoUrl = res.json().get('datas')
    return photoUrl


# 提交表单
def submitForm(formWid, address, collectWid, schoolTaskWid, form):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        'extension': '1',
        'Cpdaily-Extension': '1wAXD2TvR72sQ8u+0Dw8Dr1Qo1jhbem8Nr+LOE6xdiqxKKuj5sXbDTrOWcaf v1X35UtZdUfxokyuIKD4mPPw5LwwsQXbVZ0Q+sXnuKEpPOtk2KDzQoQ89KVs gslxPICKmyfvEpl58eloAZSZpaLc3ifgciGw+PIdB6vOsm2H6KSbwD8FpjY3 3Tprn2s5jeHOp/3GcSdmiFLYwYXjBt7pwgd/ERR3HiBfCgGGTclquQz+tgjJ PdnDjA==',
        'Content-Type': 'application/json; charset=utf-8',
        # 请注意这个应该和配置文件中的host保持一致
        'Host': host,
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    # 默认正常的提交参数json
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": form}
    # print(params)
    submitForm = 'https://{host}/wec-counselor-collector-apps/stu/collector/submitForm'.format(host=host)
    r = session.post(url=submitForm, headers=headers, data=json.dumps(params))
    msg = r.json()['message']
    return msg


title_text = '今日校园疫结果通知'

# 发送邮件通知
def sendMessage(send, msg):
    if send != '':
        log('正在发送邮件通知。。。')
        res = requests.post(url='http://www.zimo.wiki:8080/mail-sender/sendMail',
                            data={'title': title_text, 'content': getTimeStr() + str(msg), 'to': send['email']})

        code = res.json()['code']
        if code == 0:
            log('发送邮件通知成功。。。')
        else:
            log('发送邮件通知失败。。。')
            log(res.json())

def sendEmail(send,msg):
    my_sender= config['Info']['Email']['account']   # 发件人邮箱账号
    my_pass = config['Info']['Email']['password']         # 发件人邮箱密码
    my_user = send['email']      # 收件人邮箱账号，我这边发送给自己
    try:
        msg=MIMEText(getTimeStr() + str(msg),'plain','utf-8')
        msg['From']=formataddr(["结果通知",my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To']=formataddr(["你",my_user])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject']=title_text               # 邮件的主题，也可以说是标题

        server=smtplib.SMTP_SSL(config['Info']['Email']['server'], config['Info']['Email']['port'])  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender,[my_user,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        log("邮件发送失败")
    else: print("邮件发送成功")

# server酱通知
def sendServerChan(msg):
    log('正在发送Server酱。。。')
    res = requests.post(url='https://sc.ftqq.com/{0}.send'.format(config['Info']['ServerChan']),
                            data={'text': title_text, 'desp': getTimeStr() + "\n" + str(msg)})
    code = res.json()['errmsg']
    if code == 'success':
        log('发送Server酱通知成功。。。')
    else:
        log('发送Server酱通知失败。。。')
        log('Server酱返回结果'+code)

# Qmsg酱通知
def sendQmsgChan(msg):
    log('正在发送Qmsg酱。。。')
    res = requests.post(url='https://qmsg.zendee.cn:443/send/{0}'.format(config['Info']['Qsmg']),
                            data={'msg': title_text + '\n时间：' + getTimeStr() + "\n 返回结果：" + str(msg)})
    code = res.json()['success']
    if code:
        log('发送Qmsg酱通知成功。。。')
    else:
        log('发送Qmsg酱通知失败。。。')
        log('Qmsg酱返回结果'+code)

# 综合提交
def InfoSubmit(msg, send=None):
    if(None != send):
        if(config['Info']['Email']['enable']): sendEmail(send,msg)
        else: sendMessage(send, msg)
    if(config['Info']['ServerChan']): sendServerChan(msg)
    if(config['Info']['Qsmg']): sendQmsgChan(msg)


# 腾讯云函数启动函数
def main_handler(event, context):
    try:
        user = config['user']
        log('当前用户：' + str(user['username']))
        log('脚本开始执行。。。')
        log('正在查询最新待填写问卷。。。')
        params = queryForm()
        if str(params) == 'None':
            log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
            InfoSubmit('没有新问卷')
            exit(-1)
        log('查询最新待填写问卷成功。。。')
        log('正在自动填写问卷。。。')
        form = fillForm(params['form'])
        log('填写问卷成功。。。')
        log('正在自动提交。。。')
        msg = submitForm(params['formWid'], user['address'], params['collectWid'],
                         params['schoolTaskWid'], form)
        if msg == 'SUCCESS':
            log('自动提交成功！')
            InfoSubmit('自动提交成功！', user)
        elif msg == '该收集已填写无需再次填写':
            log('今日已提交！')
            InfoSubmit('今日已提交！')
        else:
            log('自动提交失败。。。')
            log('错误是' + msg)
            InfoSubmit('自动提交失败！错误是' + msg, user)
            exit(-1)
    except Exception as e:
        InfoSubmit("出现问题了！"+str(e))
        return e
    else:
        return 'auto submit success.'


# 配合Windows计划任务等使用
if __name__ == '__main__':
    print(main_handler({}, {}))
    # for user in config['users']:
    #     log(getCpdailyApis(user))
 