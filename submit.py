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


# 读取配置
def getConfig(file='config.ini'):
    config = configparser.ConfigParser()
    config.read(file, encoding='utf-8')

    login_url = config['login']['url']
    xh = config['user']['xh']
    pwd = config['user']['pwd']
    address = config['user']['address']
    return {"login_url": login_url, "xh": xh, "pwd": pwd, "address": address}


# 登陆并获取cookies
def getCookies(config):
    params = {
        'url': 'http://authserver.yibinu.edu.cn/authserver/login?service=https%3A%2F%2Fyibinu.cpdaily.com%2Fportal%2Flogin',
        'xh': config['xh'],
        'pwd': config['pwd']
    }

    cookies = {}
    # 借助上一个项目开放出来的登陆API，此API只适用于宜宾学院
    res = requests.post(config['login_url'], params)

    if str(res.json()['cookies']) == 'None':
        return None

    # 解析cookie

    for line in res.json()['cookies'].split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    return cookies


# 查询表单
def queryForm(cookies):
    queryCollectWidUrl = 'https://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'
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

    res = requests.post(url='https://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/detailCollector',
                        headers=headers, cookies=cookies, data=json.dumps({"collectorWid": collectWid}));
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    res = requests.post(url='https://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/getFormFields',
                        headers=headers, cookies=cookies, data=json.dumps(
            {"pageSize": 10, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form = res.json()['datas']['rows']
    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(form):
    form[0]['value'] = '否'
    del form[0]['fieldItems'][0]
    form[1]['value'] = '否'
    del form[1]['fieldItems'][0]
    form[2]['value'] = '否'
    del form[2]['fieldItems'][0]
    form[3]['value'] = '家庭自我隔离'
    del form[3]['fieldItems'][2]
    del form[3]['fieldItems'][1]
    form[4]['value'] = '身体健康'
    del form[4]['fieldItems'][2]
    del form[4]['fieldItems'][1]
    form[5]['value'] = '正常'
    del form[5]['fieldItems'][1]
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

    r = requests.post("http://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/submitForm",
                      headers=headers, cookies=cookies, data=json.dumps(params))
    msg = r.json()['message']
    return msg


def main():
    config = getConfig()
    while True:
        log('脚本开始执行。。。')
        cookies = getCookies(config)
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
            msg = submitForm(params['formWid'], config['address'], params['collectWid'], params['schoolTaskWid'], form,
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
