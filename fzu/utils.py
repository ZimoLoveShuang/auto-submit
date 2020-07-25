import sys
import json
import uuid
import yaml
from fzu.encrypt import *
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
    cpdailyInfo = DESEncrypt(json.dumps(extension))
    return cpdailyInfo


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


if __name__ == '__main__':
    config = getYmlConfig('config.yml')
    user = config['user']
    print(getCpdailyInfo(user))
