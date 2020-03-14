# auto-submit
今日校园自动提交疫情上报py脚本

# 使用
1. clone 或者 下载 此仓库到本地
2. 打开本地仓库文件夹，配置config.ini中对应的学号（xh）和密码（pwd）
3. 使用pip等 Python 包管理工具安装依赖库
4. 利用python命令执行submit.py脚本

# 说明
1. 此项目依赖python3.8运行环境，如没有，自行安装
2. 此项目依赖configparser requests json time等python库，如没有，自行安装
3. 此项目依赖上一个爬虫项目[宜宾学院教务系统成绩爬虫](https://github.com/ZimoLoveShuang/yibinu-score-crawler.git)
4. 此项目**不维护**，如有问题，自行debug
5. 此项目默认提交全部正常的情况，如果有其他情况，请自行在今日校园app上提交

# 一些可能存在的问题
1. collectWid不合适，请自行抓包调整
2. 休眠时间不合适，请自行调整
3. 其他问题，自行解决