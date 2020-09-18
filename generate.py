# -*- coding: utf-8 -*-
import index as app
import yaml


# 生成默认配置
def generate():
    config = app.config
    user = config['users'][0]
    apis = app.getCpdailyApis(user)
    session = app.getSession(user, apis['login-url'])
    form = dict(app.queryForm(session, apis))['form']
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
            if default['type'] == 1 or default['type'] == 5:
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


if __name__ == "__main__":
    generate()
