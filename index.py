# coding: utf-8
import sys
import requests
import json
import yaml
from datetime import datetime, timedelta, timezone


# 读取yml配置
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


# 全局配置
config = getYmlConfig()


# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()


# 登陆并获取cookies
def getCookies(user):
    user = user['user']
    params = {
        'login_url': config['login']['params']['login-url'],
        'needcaptcha_url': config['login']['params']['needcaptcha-url'],
        'captcha_url': config['login']['params']['captcha-url'],
        'username': user['username'],
        'password': user['password']
    }

    cookies = {}
    # 借助上一个项目开放出来的登陆API，模拟登陆
    res = requests.post(config['login']['api'], params)
    cookieStr = str(res.json()['cookies'])
    if cookieStr == 'None':
        return None

    # 解析cookie
    for line in cookieStr.split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    return cookies


# 查询表单
def queryForm(cookies):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8'
    }

    queryCollectWidUrl = config['cpdaily']['api']['query-collect-wid-api']['url']
    params = config['cpdaily']['api']['query-collect-wid-api']['params']
    res = requests.post(queryCollectWidUrl, headers=headers, cookies=cookies, data=json.dumps(params))
    if len(res.json()['datas']['rows']) < 1:
        return None

    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    detailCollector = config['cpdaily']['api']['detail-collector']['url']
    res = requests.post(url=detailCollector, headers=headers, cookies=cookies,
                        data=json.dumps({"collectorWid": collectWid}))
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    getFormFields = config['cpdaily']['api']['get-form-fields']['url']
    res = requests.post(url=getFormFields, headers=headers, cookies=cookies, data=json.dumps(
        {"pageSize": 100, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form = res.json()['datas']['rows']
    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(form):
    for formItem in form:
        # 只处理必填项
        if formItem['isRequired'] == 1:
            sort = int(formItem['sort'])
            default = config['cpdaily']['defaults'][sort - 1]['default']
            # 填充默认值
            formItem['value'] = default['value']
            log('必填问题%d：' % sort + formItem['title'] + '?')
            log('答案%d：' % sort + formItem['value'])
            # 单选框需要删掉其他选项
            if formItem['fieldType'] == 2:
                fieldItems = formItem['fieldItems']
                for i in range(0, len(fieldItems))[::-1]:
                    if fieldItems[i]['content'] != default['value']:
                        del fieldItems[i]
            # 多选或者其他格式需要单独处理的可以写在下面
    return form


# 提交表单
def submitForm(formWid, address, collectWid, schoolTaskWid, form, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        'extension': '1',
        'Cpdaily-Extension': '1wAXD2TvR72sQ8u+0Dw8Dr1Qo1jhbem8Nr+LOE6xdiqxKKuj5sXbDTrOWcaf v1X35UtZdUfxokyuIKD4mPPw5LwwsQXbVZ0Q+sXnuKEpPOtk2KDzQoQ89KVs gslxPICKmyfvEpl58eloAZSZpaLc3ifgciGw+PIdB6vOsm2H6KSbwD8FpjY3 3Tprn2s5jeHOp/3GcSdmiFLYwYXjBt7pwgd/ERR3HiBfCgGGTclquQz+tgjJ PdnDjA==',
        'Content-Type': 'application/json; charset=utf-8',
        # 请注意这个应该和配置文件中的host保持一致
        'Host': config['cpdaily']['api']['host'],
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    # 默认正常的提交参数json
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": form}
    submitForm = config['cpdaily']['api']['submit-form']['url']
    r = requests.post(url=submitForm, headers=headers, cookies=cookies, data=json.dumps(params))
    msg = r.json()['message']
    return msg


# 腾讯云函数启动函数
def main_handler(event, context):
    try:
        for user in config['users']:
            log('当前用户：' + str(user['user']['username']))
            log('脚本开始执行。。。')
            log('开始模拟登陆。。。')
            cookies = getCookies(config['users'][0])
            if str(cookies) != 'None':
                log('模拟登陆成功。。。')
                log('正在查询最新待填写问卷。。。')
                params = queryForm(cookies)
                if str(params) == 'None':
                    log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
                    exit(-1)
                log('查询最新待填写问卷成功。。。')
                log('正在自动填写问卷。。。')
                form = fillForm(params['form'])
                log('填写问卷成功。。。')
                log('正在自动提交。。。')
                msg = submitForm(params['formWid'], config['users'][0]['user']['address'], params['collectWid'],
                                 params['schoolTaskWid'],
                                 form,
                                 cookies)
                if msg == 'SUCCESS':
                    log('自动提交成功！')
                    sendMessage(user['user']['email'], '自动提交成功！')
                elif msg == '该收集已填写无需再次填写':
                    log('今日已提交！')
                else:
                    log('自动提交失败。。。')
                    log('错误是' + msg)
                    sendMessage(user['user']['email'], '自动提交失败！错误是' + msg)
                    exit(-1)
            else:
                log('模拟登陆失败。。。')
                log('原因可能是学号或密码错误，请检查配置后，重启脚本。。。')
                exit(-1)
    except:
        return 'auto submit fail.'
    else:
        return 'auto submit success.'


# 发送邮件通知
def sendMessage(send, msg):
    if send != '':
        log('正在发送邮件通知。。。')
        res = requests.post(url='http://www.zimo.wiki:8080/mail-sender/sendMail',
                            data={'title': '今日校园疫情上报自动提交结果通知', 'content': getTimeStr() + str(msg), 'to': send})
        code = res.json()['code']
        if code == 0:
            log('发送邮件通知成功。。。')
        else:
            log('发送邮件通知失败。。。')
            log(res.json())


if __name__ == '__main__':
    # 配合Windows计划任务使用
    print(main_handler({}, {}))
