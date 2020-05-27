# coding: utf-8
import index as app
import time


def main():
    while True:
        app.log('脚本开始执行。。。')
        cookies = app.getCookies()
        if str(cookies) != 'None':
            app.log('模拟登陆成功。。。')
            app.log('正在查询最新待填写问卷。。。')
            params = app.queryForm(cookies)
            if str(params) == 'None':
                app.log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
                app.log('无需重启脚本，1小时后，脚本将自动重新尝试。。。')
                time.sleep(60 * 60 * 1)
                continue
            app.log('查询最新待填写问卷成功。。。')
            app.log('正在自动填写问卷。。。')
            form = app.fillForm(params['form'])
            app.log('填写问卷成功。。。')
            app.log('正在自动提交。。。')
            msg = app.submitForm(params['formWid'], app.config['user']['address'], params['collectWid'],
                                 params['schoolTaskWid'], form,
                                 cookies)
            if msg == 'SUCCESS':
                app.log('自动提交成功！24小时后，脚本将再次自动提交。。。')
                time.sleep(24 * 60 * 60)
            elif msg == '该收集已填写无需再次填写':
                app.log('今日已提交！24小时后，脚本将再次自动提交。。。')
                app.sendMessage()
                time.sleep(24 * 60 * 60)
            else:
                app.log('自动提交失败。。。')
                app.log('错误是' + msg)
                exit(-1)
        else:
            app.log('模拟登陆失败。。。')
            app.log('原因可能是学号或密码错误，请检查配置后，重启脚本。。。')
            exit(-1)


if __name__ == '__main__':
    main()
    # 下面的代码测试用
    # app.main_handler({}, {})
