# -*- coding: utf-8 -*-
import sys
import json
import uuid
import yaml
from encrypt import *
from email.utils import formatdate
from datetime import datetime, timedelta, timezone


# 获取Cpdaily-Extension
def getCpdailyInfo(user):
    extension = {
        "lon": user['lon'],
        "model": "PCRT00",
        "appVersion": "8.0.8",
        "systemVersion": "4.4.4",
        "userId": user['username'],
        "systemName": "android",
        "lat": user['lat'],
        "deviceId": str(uuid.uuid1())
    }
    CpdailyInfo = DESEncrypt(json.dumps(extension))
    print('CpdailyInfo')
    print(CpdailyInfo)
    return CpdailyInfo


# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()


# 读取yml配置
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


# 将cookieStr转换为字典
def cookieStrToDict(cookieStr):
    cookies = {}
    for line in cookieStr.split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    return cookies


# 获取当前的GMT格式时间
def getNowGMTTIme():
    dt = formatdate(None, usegmt=True)
    return dt

