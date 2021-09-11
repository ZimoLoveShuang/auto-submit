import yaml
import time
from todayLoginService import TodayLoginService
from actions.autoSign import AutoSign
from actions.collection import Collection
from actions.workLog import workLog
from actions.sleepCheck import sleepCheck
from actions.rlMessage import RlMessage


def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


def main():
    config = getYmlConfig()
    for user in config['users']:
        rl = RlMessage(user['user']['email'],user['user']['sc'],user['user']['pp'])
        max_tries = 0
        if config['debug']:
            msg = working(user)
        else:
            while max_tries < 5:
                try:
                    msg = working(user)
                    print(msg)
                    msg = rl.send('成功', msg)
                    break;
                except Exception as e:
                    msg = str(e)
                    print(msg)
                    time.sleep(5)
                    print('出错！五秒后重试……')
                    if max_tries >= 4:
                        msg = rl.send('出错', msg)
                max_tries+=1
        print(msg)

def working(user):
    today = TodayLoginService(user['user'])
    today.login()
    # 登陆成功，通过type判断当前属于 信息收集、签到、查寝
    # 信息收集
    if user['user']['type'] == 0:
        # 以下代码是信息收集的代码
        collection = Collection(today, user['user'])
        collection.queryForm()
        collection.fillForm()
        msg = collection.submitForm()
        return msg
    elif user['user']['type'] == 1:
        # 以下代码是签到的代码
        sign = AutoSign(today, user['user'])
        sign.getUnSignTask()
        sign.getDetailTask()
        sign.fillForm()
        msg = sign.submitForm()
        return msg
    elif user['user']['type'] == 2:
        # 以下代码是查寝的代码
        check = sleepCheck(today, user['user'])
        check.getUnSignedTasks()
        check.getDetailTask()
        check.fillForm()
        msg = check.submitForm()
        return msg
    elif user['user']['type'] == 3:
        # 以下代码是工作日志的代码
        work = workLog(today, user['user'])
        work.checkHasLog()
        work.getFormsByWids()
        work.fillForms()
        msg = work.submitForms()
        return msg
# 阿里云的入口函数
def handler(event, context):
    main()


# 腾讯云的入口函数
def main_handler(event, context):
    main()
    return 'ok'


if __name__ == '__main__':
    main()
