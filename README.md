# auto-submit
# 今日校园每日自动提交疫情上报py脚本

# 使用
1. clone 或者 下载 此仓库到本地
    ```shell script
    git clone https://github.com/ZimoLoveShuang/auto-submit.git
    ```
2. 打开本地仓库文件夹，配置config.ini中对应的学号（username）和密码（password）还有地址（address），**注意这里的学号和密码都是智慧校园的学号和密码**
3. 使用pip等 Python 包管理工具安装依赖库
    ```shell script
    pip install requests
    ```
4. 利用python命令执行submit.py脚本
    ```shell script
    python submit.py
    ```

# 说明
1. 此项目只适用于宜宾学院学子，其他学校，可以按照设计思路，抓包实现
2. 此项目依赖python3.8运行环境，如没有，自行安装
3. 此项目依赖configparser requests json time等python库，如没有，自行安装
4. 此项目依赖上一个爬虫项目[宜宾学院教务系统成绩爬虫](https://github.com/ZimoLoveShuang/yibinu-score-crawler.git)
5. 此项目默认提交全部正常的情况，如果有其他情况，请自行在今日校园app上提交

# 设计思路
1. 模拟登陆
2. 获取表单
3. 填充表单
4. 提交表单

# 关于模拟登陆API的说明
1. 此项目依赖的模拟登陆API已经更新，理论上适用于几乎所有金智开发的教务系统（智慧校园统一登陆接口），**无论是加密了还是没加密**
2. login_url：金智教务系统登陆页的地址 类似这样 `http://authserver.swun.edu.cn/authserver/login`
3. needcaptcha_url：金智教务系统是否需要验证码接口的地址 类似这样 `http://authserver.swun.edu.cn/authserver/needCaptcha.html`
4. captcha_url: 金智教务系统是否需要验证码接口地址 类似这样 `http://authserver.swun.edu.cn/authserver/needCaptcha.html`
5. 以上三个参数，宜宾学院学子二次开发时可以不用考虑，不用提交，后台默认
6. 以上三个参数，均只需要基础的地址即可，不要**画蛇添足增加参数**
7. 登陆API共有五个参数，除了上面三个。另外两个是username（学号）和password（密码）
8. 关于开源登陆模块，等我忙完这段时间吧
9. 服务器是阿里云学生机，大家手下留情，不要搞宕机了
10. 如果你测试到此接口不适用与你们学校，欢迎来和我聊一聊（QQ：461009747）
11. 接口调用成功的返回
    ```json
    {"msg":"login success!","code":0,"cookies":"route=4ea9584fdef38a06ae81242b05d75a55;JSESSIONID=4DeiqpNPevLZsxkM6GeigG2t-Yao640K4Y_HkMH9UGGzSdPaLb-l!656361978;CASTGC=TGT-14652-pxjTAmLrgOILV3fUrkICgwwUvqxEEf9LyH3WTjbon2H3QBD9tL1587572020963-jnjP-cas;CASPRIVACY=;iPlanetDirectoryPro=Y5pcJgWfgXGOz5OciWVjfa"}
    ```
12. 接口调用失败的返回
    ```json
    {"msg":"login failed!","code":1,"cookies":null}
    ```
13. 关于API使用的一个python示例，请看A.py

# 其他
1. 关于Cpdaily-Extension：今日校园APP的处理是登陆时获取，每台设备唯一，但是有个空子就是，只要你不退出登陆，这个就会一直被维持，一直有效，换句话说，就是在APP上手动退出后失效，所以无需重复抓包获取
![意外发现：Cpdaily-Extension](screenshots/13d573c2.png)
![意外发现：Cpdaily-Extension](screenshots/e5f77237.png)
2. 关于抓包：今日校园APP某些接口启动了ssl pinning机制，一般的方法无法抓包
3. 提供一个参考的破解ssl pinning机制的方法：使用逍遥安卓4.4.4模拟器，配合xposed框架，使用justtrustme模块，hook掉验证证书的函数即可抓包
4. 逆向apk亦可破解ssl pinning和sign算法，意外发现是今日校园v8.0.8及之前的版本没有加固
5. **本项目仅供学习交流使用，如作他用所承受的任何直接、间接法律责任一概与作者无关（下载使用或参考项目即代表你同意此观点）**
# 使用了此脚本或者参考了这个项目，请自觉给项目点个star