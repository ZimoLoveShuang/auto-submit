# coding: utf-8
import configparser
import sys
import requests
import json
import time


# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ' + str(content))
    sys.stdout.flush()


# 登陆并获取cookies
def getCookies():
    params = {
        'login_url': config['jinzhi']['login_url'],
        'needcaptcha_url': config['jinzhi']['needcaptcha_url'],
        'captcha_url': config['jinzhi']['captcha_url'],
        'username': config['user']['username'],
        'password': config['user']['password']
    }

    cookies = {}
    # 借助上一个项目开放出来的登陆API，模拟登陆
    res = requests.post(config['login']['login_api'], params)

    if str(res.json()['cookies']) == 'None':
        return None

    # 解析cookie
    for line in res.json()['cookies'].split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    return cookies


# 查询表单
def queryForm(cookies):
    queryCollectWidUrl = config['cpdaily_api']['query_collect_wid_url']
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8'
    }

    params = {
        'pageSize': 6,
        'pageNumber': 1
    }

    res = requests.post(queryCollectWidUrl, headers=headers, cookies=cookies, data=json.dumps(params))
    if len(res.json()['datas']['rows']) < 1:
        return None

    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    detailCollector = config['cpdaily_api']['detail_collector']
    res = requests.post(url=detailCollector, headers=headers, cookies=cookies,
                        data=json.dumps({"collectorWid": collectWid}));
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    getFormFields = config['cpdaily_api']['get_form_fields']
    res = requests.post(url=getFormFields, headers=headers, cookies=cookies, data=json.dumps(
        {"pageSize": 100, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form = res.json()['datas']['rows']
    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(form):
    cpdaily = dict(config['cpdaily'])
    cnt = 0
    index = 1
    for item in form:
        # 必填项
        if item['isRequired'] == 1:
            # 文本
            if item['fieldType'] == 1:
                form[cnt]['value'] = cpdaily['default_%d' % index]
            # 单选
            elif item['fieldType'] == 2:
                fieldItems = item['fieldItems']
                for i in range(0, len(fieldItems))[::-1]:
                    if fieldItems[i]['content'] == cpdaily['default_%d' % index]:
                        form[cnt]['value'] = fieldItems[i]['content']
                    else:
                        del fieldItems[i]
            # 其他类型，目前暂时不知道该如何填，所以退出
            else:
                log('cpdaily表单出现了未知填写类型的问题，待优化 ' + str(item))
                exit(-1)
            cnt += 1
            index += 1
    if cnt != index - 1:
        log('cpdaily表单默认值配置不正确，请检查。。。')
        exit(-1)
    return form


# 提交表单
def submitForm(formWid, address, collectWid, schoolTaskWid, form, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        'extension': '1',
        'Cpdaily-Extension': '1wAXD2TvR72sQ8u+0Dw8Dr1Qo1jhbem8Nr+LOE6xdiqxKKuj5sXbDTrOWcaf v1X35UtZdUfxokyuIKD4mPPw5LwwsQXbVZ0Q+sXnuKEpPOtk2KDzQoQ89KVs gslxPICKmyfvEpl58eloAZSZpaLc3ifgciGw+PIdB6vOsm2H6KSbwD8FpjY3 3Tprn2s5jeHOp/3GcSdmiFLYwYXjBt7pwgd/ERR3HiBfCgGGTclquQz+tgjJ PdnDjA==',
        'Content-Type': 'application/json; charset=utf-8',
        'Host': 'yibinu.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    # 默认正常的提交参数json
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": form}
    submitForm = config['cpdaily_api']['submit_form']
    r = requests.post(url=submitForm, headers=headers, cookies=cookies, data=json.dumps(params))
    msg = r.json()['message']
    return msg


# 全局配置
config = configparser.RawConfigParser()
config.read('config.ini', encoding='utf-8')


def main():
    while True:
        log('脚本开始执行。。。')
        cookies = getCookies()
        if str(cookies) != 'None':
            log('模拟登陆成功。。。')
            log('正在查询最新待填写问卷。。。')
            params = queryForm(cookies)
            if str(params) == 'None':
                log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
                log('无需重启脚本，1小时后，脚本将自动重新尝试。。。')
                time.sleep(60 * 60 * 1)
                continue
            log('查询最新待填写问卷成功。。。')
            log('正在自动填写问卷。。。')
            form = fillForm(params['form'])
            log('填写问卷成功。。。')
            log('正在自动提交。。。')
            msg = submitForm(params['formWid'], config['user']['address'], params['collectWid'],
                             params['schoolTaskWid'], form,
                             cookies)
            if msg == 'SUCCESS':
                log('自动提交成功！24小时后，脚本将再次自动提交。。。')
                time.sleep(24 * 60 * 60)
            elif msg == '该收集已填写无需再次填写':
                log('今日已提交！24小时后，脚本将再次自动提交。。。')
                time.sleep(24 * 60 * 60)
            else:
                log('自动提交失败。。。')
                log('错误是' + msg)
                exit(-1)
        else:
            log('模拟登陆失败。。。')
            log('原因可能是学号或密码错误，请检查配置后，重启脚本。。。')
            exit(-1)


if __name__ == '__main__':
    main()
