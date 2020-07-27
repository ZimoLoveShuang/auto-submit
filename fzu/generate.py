# encoding: utf-8
from fzu import index as app
import yaml
import time


# 生成默认配置
def generate():
    form = dict(app.queryForm())['form']
    # app.log(form)
    defaults = []
    sort = 1
    for formItem in form:
        if formItem['isRequired'] == 1:
            default = {}
            one = {}
            default['title'] = formItem['title']
            default['type'] = formItem['fieldType']
            print('问题%d：' % sort + default['title'])
            if default['type'] == 1:
                default['value'] = input("请输入文本：")
            if default['type'] == 2:
                fieldItems = formItem['fieldItems']
                num = 1
                for fieldItem in fieldItems:
                    print('\t%d ' % num + fieldItem['content'])
                    num += 1
                choose = int(input("请输入序号："))
                if choose < 1 or choose > num:
                    print('输入错误，请重新执行此脚本')
                    exit(-1)
                default['value'] = fieldItems[choose - 1]['content']
            if default['type'] == 3:
                fieldItems = formItem['fieldItems']
                num = 1
                for fieldItem in fieldItems:
                    print('\t%d ' % num + fieldItem['content'])
                    num += 1
                chooses = list(map(int, input('请输入序号（可输入多个，请用空格隔开）：').split()))
                default['value'] = ''
                for i in range(0, len(chooses)):
                    choose = chooses[i]
                    if choose < 1 or choose > num:
                        print('输入错误，请重新执行此脚本')
                        exit(-1)
                    if i != len(chooses) - 1:
                        default['value'] += fieldItems[choose - 1]['content'] + ','
                    else:
                        default['value'] += fieldItems[choose - 1]['content']
            if default['type'] == 4:
                default['value'] = input("请输入图片名称：")
            one['default'] = default
            defaults.append(one)
            sort += 1
    print('======================分隔线======================')
    print(yaml.dump(defaults, allow_unicode=True))


def MOD_AUTH_TOKEN():
    # 3.4获取MOD_AUTH_CAS
    url = 'https://{host}/wec-counselor-collector-apps/stu/mobile/index.html?timestamp='.format(host=app.host) + str(
        int(round(time.time() * 1000)))
    headers3 = {
        'Host': app.host,
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; PCRT00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 cpdaily/8.0.8 wisedu/8.0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'X-Requested-With': 'com.wisedu.cpdaily',
    }

    res = app.session.get(url=url, headers=headers3)
    print(res.text)
    print(res.headers)
    print(app.session.cookies)

if __name__ == "__main__":
    generate()
    # MOD_AUTH_TOKEN()
