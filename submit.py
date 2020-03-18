# coding: utf-8
import configparser
import requests
import json
import time

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
        print('学号或密码错误，请检查配置后 重启脚本')
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

    param = {
        'pageSize': 6,
        'pageNumber': 1
    }

    res = requests.post(queryCollectWidUrl, headers=headers, cookies=cookies, data=json.dumps(params))
    # print(res.text)
    if len(res.json()['datas']['rows']) < 1:
        print('获取collectWid失败，可能是辅导员还没有发布任务，无需重启，脚本将在1小时后自动重新尝试')
        time.sleep(1 * 60 * 60)
        continue
    collectWid = res.json()['datas']['rows'][0]['wid']

    headers = {
        'tenantId': '1018789912947381',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        'extension': '1',
        'Cpdaily-Extension': '7Q881vmOiX7nCAFvYP7Vs0i+EVwTCyEruC4euS0HemoXqaLS/g5g7wovFJVeHrikY1uuQ8gSH5RdZQeCzbsBjk+0DKsec7OiSPZxU3wDCpuvnS12Ikra05lQ B7dFJeUJb/IdN0JXRwTR7xqUfqje7sdXl6C1BRrfwXnWuxmOXh+NXAMxd7t1 UoUMYS2qHw5wNUgO37idqwJjd3Nzfez7XDkRehxMQwCCm7VgcAn6Z741lLzN Mt95ElAtkHp4O26TaCZ5Tmi7fcrZsrNSXQbx1E2HsrjGntoo',
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Length': '4392',
        'Host': 'yibinu.cpdaily.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    global null
    null = ''

    # 默认正常的提交参数json
    params = {"formWid": "47", "address": address, "collectWid": collectWid, "schoolTaskWid": "21551",
              "form": [{"wid": "1322", "formWid": "47", "fieldType": 2, "title": "本人是否接触过武汉（归来）人员", "description": "",
                        "minLength": 0, "sort": "1", "maxLength": null, "isRequired": 1, "imageCount": null,
                        "hasOtherItems": 0, "colName": "field001", "value": "否", "fieldItems": [
                      {"itemWid": "3212", "content": "否", "isOtherItems": 0, "contendExtend": "", "isSelected": null}]},
                       {"wid": "1323", "formWid": "47", "fieldType": 2, "title": "本人是否接触过新型冠状病毒患者", "description": "",
                        "minLength": 0, "sort": "2", "maxLength": null, "isRequired": 1, "imageCount": null,
                        "hasOtherItems": 0, "colName": "field002", "value": "否", "fieldItems": [
                           {"itemWid": "3214", "content": "否", "isOtherItems": 0, "contendExtend": "",
                            "isSelected": null}]},
                       {"wid": "1324", "formWid": "47", "fieldType": 2, "title": "本人是否有新型冠状病毒类似病状", "description": "",
                        "minLength": 0, "sort": "3", "maxLength": null, "isRequired": 1, "imageCount": null,
                        "hasOtherItems": 0, "colName": "field003", "value": "否", "fieldItems": [
                           {"itemWid": "3216", "content": "否", "isOtherItems": 0, "contendExtend": "",
                            "isSelected": null}]},
                       {"wid": "1325", "formWid": "47", "fieldType": 2, "title": "本人隔离方式", "description": "",
                        "minLength": 0, "sort": "4", "maxLength": null, "isRequired": 1, "imageCount": null,
                        "hasOtherItems": 0, "colName": "field004", "value": "家庭自我隔离", "fieldItems": [
                           {"itemWid": "3217", "content": "家庭自我隔离", "isOtherItems": 0, "contendExtend": "",
                            "isSelected": null}]},
                       {"wid": "1326", "formWid": "47", "fieldType": 2, "title": "本人身体状况", "description": "",
                        "minLength": 0, "sort": "5", "maxLength": null, "isRequired": 1, "imageCount": null,
                        "hasOtherItems": 0, "colName": "field005", "value": "身体健康", "fieldItems": [
                           {"itemWid": "3220", "content": "身体健康", "isOtherItems": 0, "contendExtend": "",
                            "isSelected": null}]},
                       {"wid": "1327", "formWid": "47", "fieldType": 2, "title": "共同居住家属情况", "description": "",
                        "minLength": 0, "sort": "6", "maxLength": null, "isRequired": 1, "imageCount": null,
                        "hasOtherItems": 0, "colName": "field006", "value": "正常", "fieldItems": [
                           {"itemWid": "3223", "content": "正常", "isOtherItems": 0, "contendExtend": "",
                            "isSelected": null}]},
                       {"wid": "1328", "formWid": "47", "fieldType": 1, "title": "共同居住家属异常情况描述",
                        "description": "共同居住家属情况为异常时填写。", "minLength": 1, "sort": "7", "maxLength": 300,
                        "isRequired": 0,
                        "imageCount": null, "hasOtherItems": 0, "colName": "field007", "value": "", "fieldItems": []},
                       {"wid": "1329", "formWid": "47", "fieldType": 1, "title": "医学隔离地点",
                        "description": "本人隔离方式为“医学隔离”的填写", "minLength": 1, "sort": "8", "maxLength": 300,
                        "isRequired": 0, "imageCount": null, "hasOtherItems": 0, "colName": "field008", "value": "",
                        "fieldItems": []}, {"wid": "1330", "formWid": "47", "fieldType": 1, "title": "医学隔离开始时间",
                                            "description": "本人隔离方式为“医学隔离”的填写", "minLength": 1, "sort": "9",
                                            "maxLength": 300, "isRequired": 0, "imageCount": -1, "hasOtherItems": 0,
                                            "colName": "field009", "value": "", "fieldItems": [], "date": "",
                                            "time": ""},
                       {"wid": "1331", "formWid": "47", "fieldType": 1, "title": "疑似/确诊为新型冠状病毒感染时间",
                        "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "10",
                        "maxLength": 300, "isRequired": 0, "imageCount": -1, "hasOtherItems": 0, "colName": "field010",
                        "value": "", "fieldItems": [], "date": "", "time": ""},
                       {"wid": "1332", "formWid": "47", "fieldType": 1, "title": "本人身份证号",
                        "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "11",
                        "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0,
                        "colName": "field011",
                        "value": "", "fieldItems": []},
                       {"wid": "1333", "formWid": "47", "fieldType": 1, "title": "本人病情描述",
                        "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "12",
                        "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0,
                        "colName": "field012",
                        "value": "", "fieldItems": []},
                       {"wid": "1334", "formWid": "47", "fieldType": 1, "title": "备注", "description": "需要特别说明的情况",
                        "minLength": 1, "sort": "13", "maxLength": 300, "isRequired": 0, "imageCount": null,
                        "hasOtherItems": 0, "colName": "field013", "value": "", "fieldItems": []}]}
    r = requests.post("http://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/submitForm",
                      headers=headers, cookies=cookies, data=json.dumps(params))
    if r.json()['message'] == 'SUCCESS':
        print('今日提交成功！24小时后，脚本将再次自动提交')
        time.sleep(24 * 60 * 60)
    else:
        print('出错了，错误如下 ' + r.text)
        exit(-1)
