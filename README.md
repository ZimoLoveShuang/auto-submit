# auto-submit
今日校园自动提交疫情上报py脚本

# 用了我的脚本或者参考了这个项目，请自觉给项目点个star

# 使用
1. clone 或者 下载 此仓库到本地
    ```shell script
    git clone https://github.com/ZimoLoveShuang/auto-submit.git
    ```
2. 打开本地仓库文件夹，配置config.ini中对应的学号（xh）和密码（pwd）还有地址（address），**注意这里的学号和密码都是智慧校园的学号和密码**
3. 使用pip等 Python 包管理工具安装依赖库
    ```shell script
    pip install requests
    ```
4. 利用python命令执行submit.py脚本
    ```shell script
    python submit.py
    ```

# 说明
1. 此项目依赖python3.8运行环境，如没有，自行安装
2. 此项目依赖configparser requests json time等python库，如没有，自行安装
3. 此项目依赖上一个爬虫项目[宜宾学院教务系统成绩爬虫](https://github.com/ZimoLoveShuang/yibinu-score-crawler.git)
5. 此项目默认提交全部正常的情况，如果有其他情况，请自行在今日校园app上提交
