# coding: utf-8
import configparser
import sys
import requests
import json
import time


def printa(content):
    print(content)
    sys.stdout.flush()


file = 'config.ini'
config = configparser.ConfigParser()
config.read(file, encoding='utf-8')

login_url = config['login']['url']
xh = config['user']['xh']
pwd = config['user']['pwd']
address = config['user']['address']

params = {
    'url': 'http://authserver.yibinu.edu.cn/authserver/login?service=https%3A%2F%2Fyibinu.cpdaily.com%2Fportal%2Flogin',
    'xh': xh,
    'pwd': pwd
}

while True:
    cookies = {}
    # 模拟登陆
    res = requests.post(login_url, params)
    # print(res.json()['cookies'])
    if str(res.json()['cookies']) == 'None':
        printa('学号或密码错误，请检查配置后 重启脚本')
        exit(-1)

    # 解析cookie

    for line in res.json()['cookies'].split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value

    # 携带cookie查询最新待提交表单
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
    # print(res.text)
    if len(res.json()['datas']['rows']) < 1:
        printa('获取collectWid失败，可能是辅导员还没有发布任务，无需重启，脚本将在1小时后自动重新尝试')
        time.sleep(1 * 60 * 60)
        continue
    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    res = requests.post(url='https://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/detailCollector',
                        headers=headers, cookies=cookies, data=json.dumps({"collectorWid": collectWid}));
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    res = requests.post(url='https://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/getFormFields',
                        headers=headers, cookies=cookies, data=json.dumps(
            {"pageSize": 10, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form = res.json()['datas']['rows']
    # for item in form:
    #     printa(item)

    res = requests.post(url='https://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/getFormFields',
                        headers=headers, cookies=cookies, data=json.dumps(
            {"pageSize": 10, "pageNumber": 2, "formWid": formWid, "collectorWid": collectWid}))
    moreForm = res.json()['datas']['rows']
    # printa('\n')
    # for item in moreForm:
    #     printa(item)

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

    global null
    null = ''

    # 默认正常的提交参数json
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": [
                  {"wid": form[0]['wid'], "formWid": formWid, "fieldType": 2, "title": "本人是否接触过武汉（归来）人员",
                   "description": "",
                   "minLength": 0, "sort": "1", "maxLength": null, "isRequired": 1, "imageCount": null,
                   "hasOtherItems": 0, "colName": "field001", "value": "否", "fieldItems": [
                      {"itemWid": form[0]['fieldItems'][1]['itemWid'], "content": "否", "isOtherItems": 0,
                       "contendExtend": "", "isSelected": null}]},
                  {"wid": form[1]['wid'], "formWid": formWid, "fieldType": 2, "title": "本人是否接触过新型冠状病毒患者",
                   "description": "",
                   "minLength": 0, "sort": "2", "maxLength": null, "isRequired": 1, "imageCount": null,
                   "hasOtherItems": 0, "colName": "field002", "value": "否", "fieldItems": [
                      {"itemWid": form[1]['fieldItems'][1]['itemWid'], "content": "否", "isOtherItems": 0,
                       "contendExtend": "",
                       "isSelected": null}]},
                  {"wid": form[2]['wid'], "formWid": formWid, "fieldType": 2, "title": "本人是否有新型冠状病毒类似病状",
                   "description": "",
                   "minLength": 0, "sort": "3", "maxLength": null, "isRequired": 1, "imageCount": null,
                   "hasOtherItems": 0, "colName": "field003", "value": "否", "fieldItems": [
                      {"itemWid": form[2]['fieldItems'][1]['itemWid'], "content": "否", "isOtherItems": 0,
                       "contendExtend": "",
                       "isSelected": null}]},
                  {"wid": form[3]['wid'], "formWid": formWid, "fieldType": 2, "title": "本人隔离方式", "description": "",
                   "minLength": 0, "sort": "4", "maxLength": null, "isRequired": 1, "imageCount": null,
                   "hasOtherItems": 0, "colName": "field004", "value": "家庭自我隔离", "fieldItems": [
                      {"itemWid": form[3]['fieldItems'][0]['itemWid'], "content": "家庭自我隔离", "isOtherItems": 0,
                       "contendExtend": "",
                       "isSelected": null}]},
                  {"wid": form[4]['wid'], "formWid": formWid, "fieldType": 2, "title": "本人身体状况", "description": "",
                   "minLength": 0, "sort": "5", "maxLength": null, "isRequired": 1, "imageCount": null,
                   "hasOtherItems": 0, "colName": "field005", "value": "身体健康", "fieldItems": [
                      {"itemWid": form[4]['fieldItems'][0]['itemWid'], "content": "身体健康", "isOtherItems": 0,
                       "contendExtend": "",
                       "isSelected": null}]},
                  {"wid": form[5]['wid'], "formWid": formWid, "fieldType": 2, "title": "共同居住家属情况", "description": "",
                   "minLength": 0, "sort": "6", "maxLength": null, "isRequired": 1, "imageCount": null,
                   "hasOtherItems": 0, "colName": "field006", "value": "正常", "fieldItems": [
                      {"itemWid": form[5]['fieldItems'][0]['itemWid'], "content": "正常", "isOtherItems": 0,
                       "contendExtend": "",
                       "isSelected": null}]},
                  {"wid": form[6]['wid'], "formWid": formWid, "fieldType": 1, "title": "共同居住家属异常情况描述",
                   "description": "共同居住家属情况为异常时填写。", "minLength": 1, "sort": "7", "maxLength": 300,
                   "isRequired": 0, "imageCount": null, "hasOtherItems": 0, "colName": "field007", "value": "",
                   "fieldItems": []},
                  {"wid": form[7]['wid'], "formWid": formWid, "fieldType": 1, "title": "医学隔离地点",
                   "description": "本人隔离方式为“医学隔离”的填写", "minLength": 1, "sort": "8",
                   "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0,
                   "colName": "field008", "value": "", "fieldItems": []},
                  {"wid": form[8]['wid'], "formWid": formWid, "fieldType": 1, "title": "医学隔离开始时间",
                   "description": "本人隔离方式为“医学隔离”的填写", "minLength": 1, "sort": "9", "maxLength": 300,
                   "isRequired": 0, "imageCount": -1, "hasOtherItems": 0, "colName": "field009", "value": "",
                   "fieldItems": [], "date": "", "time": ""},
                  {"wid": form[9]['wid'], "formWid": formWid, "fieldType": 1, "title": "疑似/确诊为新型冠状病毒感染时间",
                   "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "10",
                   "maxLength": 300, "isRequired": 0, "imageCount": -1, "hasOtherItems": 0, "colName": "field010",
                   "value": "", "fieldItems": [], "date": "", "time": ""},
                  {"wid": moreForm[0]['wid'], "formWid": formWid, "fieldType": 1, "title": "本人身份证号",
                   "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "11",
                   "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0,
                   "colName": "field011", "value": "", "fieldItems": []},
                  {"wid": moreForm[1]['wid'], "formWid": formWid, "fieldType": 1, "title": "本人病情描述",
                   "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "12",
                   "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0,
                   "colName": "field012", "value": "", "fieldItems": []},
                  {"wid": moreForm[2]['wid'], "formWid": formWid, "fieldType": 1, "title": "备注",
                   "description": "需要特别说明的情况",
                   "minLength": 1, "sort": "13", "maxLength": 300, "isRequired": 0, "imageCount": null,
                   "hasOtherItems": 0, "colName": "field013", "value": "", "fieldItems": []}]}

    # printa(params['form'])

    r = requests.post("http://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/submitForm",
                      headers=headers, cookies=cookies, data=json.dumps(params))
    msg = r.json()['message']
    if msg == 'SUCCESS':
        printa('今日提交成功！24小时后，脚本将再次自动提交')
        time.sleep(24 * 60 * 60)
    elif msg == '该收集已填写无需再次填写':
        printa(msg + ' 24小时后，脚本将再次自动提交')
        time.sleep(24 * 60 * 60)
    else:
        printa('出错了，错误如下 ' + r.text)
        exit(-1)
