import yaml
from todayLoginService import TodayLoginService
from autoSign import AutoSign
from collection import Collection


def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


def main():
    try:
        config = getYmlConfig()
        for user in config['users']:
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
                print(msg)
            elif user['user']['type'] == 1:
                # 以下代码是签到的代码
                sign = AutoSign(today, user['user'])
                sign.getUnSignTask()
                sign.getDetailTask()
                sign.fillForm()
                msg = sign.submitForm()
                print(msg)
    except Exception as e:
        print(str(e))


# 阿里云的入口函数
def handler(event, context):
    main()


# 腾讯云的入口函数
def main_handler(event, context):
    main()
    return 'ok'


if __name__ == '__main__':
    main()
