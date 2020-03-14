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

params = {
    'url': 'http://authserver.yibinu.edu.cn/authserver/login?service=https%3A%2F%2Fyibinu.cpdaily.com%2Fportal%2Flogin',
    'xh': xh,
    'pwd': pwd
}

res = requests.post(login_url, params)
# print(res.json()['cookies'])

cookies = {}
for line in res.json()['cookies'].split(';'):
    name, value = line.strip().split('=', 1)
    cookies[name] = value

collectWid = 4903  # 4682
rangeSet = collectWid + 1

headers = {
    'Host': 'yibinu.cpdaily.com',
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Accept': 'application/json, text/plain, */*',
    'Sec-Fetch-Dest': 'empty',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'http://yibinu.cpdaily.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

global null
null = ''

while collectWid < rangeSet:
    body = {"formWid": "40", "collectWid": collectWid, "schoolTaskWid": "19403", "form": [
        {"wid": "1218", "formWid": "40", "fieldType": 2, "title": "本人是否接触过武汉（归来）人员", "description": "", "minLength": 0,
         "sort": "1", "maxLength": null, "isRequired": 1, "imageCount": null, "hasOtherItems": 0, "colName": "field001",
         "value": "否", "fieldItems": [
            {"itemWid": "3100", "content": "否", "isOtherItems": 0, "contendExtend": "", "isSelected": null}]},
        {"wid": "1219", "formWid": "40", "fieldType": 2, "title": "本人是否接触过新型冠状病毒患者", "description": "", "minLength": 0,
         "sort": "2", "maxLength": null, "isRequired": 1, "imageCount": null, "hasOtherItems": 0, "colName": "field002",
         "value": "否", "fieldItems": [
            {"itemWid": "3102", "content": "否", "isOtherItems": 0, "contendExtend": "", "isSelected": null}]},
        {"wid": "1220", "formWid": "40", "fieldType": 2, "title": "本人是否有新型冠状病毒类似病状", "description": "", "minLength": 0,
         "sort": "3", "maxLength": null, "isRequired": 1, "imageCount": null, "hasOtherItems": 0, "colName": "field003",
         "value": "否", "fieldItems": [
            {"itemWid": "3104", "content": "否", "isOtherItems": 0, "contendExtend": "", "isSelected": null}]},
        {"wid": "1221", "formWid": "40", "fieldType": 2, "title": "本人隔离方式", "description": "", "minLength": 0,
         "sort": "4", "maxLength": null, "isRequired": 1, "imageCount": null, "hasOtherItems": 0, "colName": "field004",
         "value": "家庭自我隔离", "fieldItems": [
            {"itemWid": "3105", "content": "家庭自我隔离", "isOtherItems": 0, "contendExtend": "", "isSelected": null}]},
        {"wid": "1222", "formWid": "40", "fieldType": 2, "title": "本人身体状况", "description": "", "minLength": 0,
         "sort": "5", "maxLength": null, "isRequired": 1, "imageCount": null, "hasOtherItems": 0, "colName": "field005",
         "value": "身体健康", "fieldItems": [
            {"itemWid": "3108", "content": "身体健康", "isOtherItems": 0, "contendExtend": "", "isSelected": null}]},
        {"wid": "1223", "formWid": "40", "fieldType": 2, "title": "共同居住家属情况", "description": "", "minLength": 0,
         "sort": "6", "maxLength": null, "isRequired": 1, "imageCount": null, "hasOtherItems": 0, "colName": "field006",
         "value": "正常", "fieldItems": [
            {"itemWid": "3111", "content": "正常", "isOtherItems": 0, "contendExtend": "", "isSelected": null}]},
        {"wid": "1224", "formWid": "40", "fieldType": 1, "title": "共同居住家属异常情况描述", "description": "共同居住家属情况为异常时填写。",
         "minLength": 1, "sort": "7", "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0,
         "colName": "field007", "value": "", "fieldItems": []},
        {"wid": "1225", "formWid": "40", "fieldType": 1, "title": "医学隔离地点", "description": "本人隔离方式为“医学隔离”的填写",
         "minLength": 1, "sort": "8", "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0,
         "colName": "field008", "value": "", "fieldItems": []},
        {"wid": "1226", "formWid": "40", "fieldType": 1, "title": "医学隔离开始时间", "description": "本人隔离方式为“医学隔离”的填写",
         "minLength": 1, "sort": "9", "maxLength": 300, "isRequired": 0, "imageCount": -1, "hasOtherItems": 0,
         "colName": "field009", "value": "", "fieldItems": [], "date": "", "time": ""},
        {"wid": "1227", "formWid": "40", "fieldType": 1, "title": "疑似/确诊为新型冠状病毒感染时间",
         "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "10", "maxLength": 300,
         "isRequired": 0, "imageCount": -1, "hasOtherItems": 0, "colName": "field010", "value": "", "fieldItems": [],
         "date": "", "time": ""}, {"wid": "1228", "formWid": "40", "fieldType": 1, "title": "本人身份证号",
                                   "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "11",
                                   "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0,
                                   "colName": "field011", "value": "", "fieldItems": []},
        {"wid": "1229", "formWid": "40", "fieldType": 1, "title": "本人病情描述",
         "description": "本人身体状况为“疑似新型冠状病毒感染”或“确诊新型冠状病毒感染”的填写", "minLength": 1, "sort": "12", "maxLength": 300,
         "isRequired": 0, "imageCount": null, "hasOtherItems": 0, "colName": "field012", "value": "", "fieldItems": []},
        {"wid": "1230", "formWid": "40", "fieldType": 1, "title": "备注", "description": "需要特别说明的情况", "minLength": 1,
         "sort": "13", "maxLength": 300, "isRequired": 0, "imageCount": null, "hasOtherItems": 0, "colName": "field013",
         "value": "", "fieldItems": []}]}
    r = requests.post("http://yibinu.cpdaily.com/wec-counselor-collector-apps/stu/collector/submitForm",
                      headers=headers, cookies=cookies, data=json.dumps(body))

    check = r.text.split("\",\"")[1].split("\"")[2]
    checkNO1 = "该收集已结束！"
    checkNO2 = "您无需填写该信息收集，请勿代填"
    checkNO3 = "数据异常，该收集不存在，请联系管理员！"
    checkYES = "SUCCESS"
    if check == checkNO2:
        print("不是本班,自动忽略，一秒钟后自动提交编号：%d的表单" % (num + 1))
        time.sleep(1)
    else:
        pass
    if check == checkNO1:
        print("该次收集已结束，无法提交，编号：", num)
    else:
        pass
    if check == checkNO3:
        print("这条信息还不存在 半小时尝试编号：", num + 1)
        time.sleep(30 * 60)
    else:
        pass
    if check == checkYES:
        print("今日成功提交！ 八小时后再次启动")
        time.sleep(8 * 60 * 60)
    else:
        pass
    collectWid += 1
    rangeSet += 1
