# auto-submit
# 今日校园每日自动提交疫情上报py脚本

# 项目说明
- config.ini 配置文件
- index.py 配合腾讯云函数食用的py脚本
- submit.py 本地自动提交的py脚本
- A.py 测试模拟登陆API是否适用于xx学校的py脚本

# 白嫖党太多，导致我的服务器响应很不稳定，已采取封禁措施

# 使用

## 宜宾学院的同学

### 方式一：本地执行
1. clone 或者 下载 此仓库到本地
    ```shell script
    git clone https://github.com/ZimoLoveShuang/auto-submit.git
    ```
2. 打开本地仓库文件夹，配置config.ini中对应的学号（username）和密码（password）还有地址（address）等等信息，详情请看config.ini中的注释说明，**注意这里的学号和密码都是智慧校园的学号和密码**
3. 使用pip等 Python 包管理工具安装依赖库
    ```shell script
    pip install requests
    ```
4. 利用python命令执行submit.py脚本
    ```shell script
    python submit.py
    ```
5. 可配合Windows计划任务食用，修改submit.py中的注释即可
    ```python
    if __name__ == '__main__':
        # main()
        # 下面的代码测试用
        app.main_handler({}, {})
    ```
   
### 方式二：配合腾讯云函数食用
1. clone 或者 下载 此仓库到本地
    ```shell script
    git clone https://github.com/ZimoLoveShuang/auto-submit.git
    ```
2. 打开本地仓库文件夹，配置config.ini中对应的学号（username）和密码（password）还有地址（address）等等信息，详情请看config.ini中的注释说明，**注意这里的学号和密码都是智慧校园的学号和密码**
3. 打开百度搜索腾讯云函数，注册认证后，新建云函数，名称随意，运行环境选择python3.6，创建方式选择空白函数
4. 复制本地的index.py覆盖掉模板中含有的index.py
5. 新建config.ini，将本地已经配置好的confi.ini内容复制上去
6. 点击完成之后去配置触发方式，选择定时触发，名称随意，触发周期选择自定义，配置cron表达式，下面的表达式表示每天中午十二点整执行
    ```shell script
   0 0 12 * * 0-6 *
    ```
7. enjoy it!
8. 一些小问题：腾讯云函数的cron表达式执行的时间是utc时间，但是承载的服务器的时间不是utc时间，于是你会发现定时执行是正确的，但是打印的log会差8小时，并不影响使用，强迫症患者请绕道

## 其他学校的同学

1. 抓包，抓到`*.cpdaily.com`和`登录地址`就可以了
2. 配置config.ini
3. 参考宜宾学院同学的两种方式使用

# 说明
1. 此项目默认配置适用于宜宾学院学子，其他学校，可以抓包后配置config.ini后食用
2. 此项目依赖python3.8运行环境，如没有，自行安装
3. 此项目依赖configparser requests json time等python库，如没有，自行安装
4. 此项目依赖上一个爬虫项目[宜宾学院教务系统成绩爬虫](https://github.com/ZimoLoveShuang/yibinu-score-crawler.git)，开放的登陆api
5. 此项目默认提交全部正常的情况，如果有其他情况，请自行在今日校园app上提交

# 设计思路
1. 模拟登陆
2. 获取表单
3. 填充表单
4. 提交表单
5. 推送消息

# 关于模拟登陆API的说明

请看[`wisedu-unified-login-api`项目](https://github.com/ZimoLoveShuang/wisedu-unified-login-api.git)

# 关于金智教务系统的说明

1. 学校接入金智系统的方式有两种：`CLOUD`和`NOTCLOUD`
2. `CLOUD`方式对应的教务系统登陆页通常以`/iap/login`结尾
3. `NOTCLOUD`方式对应的教务系统登陆页通常以`/authserver/login`结尾
4. 目前以上两种接入方式，我提供的模拟登陆API都能支持
5. 以上两种接入方式，登陆原理均为CAS，接口略有一点不同，但大同小异

# 其他
1. 关于Cpdaily-Extension：今日校园APP的处理是登陆时获取，每台设备唯一，但是有个空子就是，只要你不退出登陆，这个就会一直被维持，一直有效，换句话说，就是在APP上手动退出后失效，所以无需重复抓包获取
![意外发现：Cpdaily-Extension](screenshots/13d573c2.png)
![意外发现：Cpdaily-Extension](screenshots/e5f77237.png)
2. 关于抓包：今日校园APP某些接口启动了ssl pinning机制，一般的方法无法抓包
3. 提供一个参考的破解ssl pinning机制的方法：使用逍遥安卓4.4.4模拟器，配合xposed框架，使用justtrustme模块，hook掉验证证书的函数即可抓包
4. 逆向apk亦可破解ssl pinning和sign算法，意外发现是今日校园v8.0.8及之前的版本没有加固
5. **本项目仅供学习交流使用，如作他用所承受的任何直接、间接法律责任一概与作者无关（下载使用或参考项目即代表你同意此观点）**
# 使用了此脚本或者参考了这个项目，请自觉给项目点个star

# 如果觉得写得不错，想支持一下，请帮忙在GitHub点个Star或者扫描下面二维码捐赠我
<table>
    <tr>
        <td ><center><img src="https://img-blog.csdnimg.cn/20200303161837163.jpg" ></center></td>
        <td ><center><img src="https://img-blog.csdnimg.cn/20200303162019613.png"  ></center></td>
    </tr>
</table>
