## 本地化登陆以及模块化类的使用说明



#### 博客教程：[https://blog.ruoli.cc/archives/29.html](https://blog.ruoli.cc/archives/29.html)

#### 视频教程：[https://pan.ruoli.cc/nanjing/video/fucktoday/](https://pan.ruoli.cc/nanjing/video/fucktoday/)

#### 1、本地化登陆

目前仅仅完成了iap以及部分cas学校的登陆

自动识别验证码需要开通 `通用文字识别`（OCR）最普通的版本

然后通过python访问`腾讯通用文字识别`需要`访问密钥`进行认证

并且需要配置路径`今日校园/login/system.yml`里的`SecretId`以及`SecretKey`

腾讯OCR开通地址：[点击这里](https://console.cloud.tencent.com/ocr/overview)

腾讯访问密钥开通地址：[点击这里](https://console.cloud.tencent.com/cam/capi)

**当然**，如果你能确保你的登陆不需要验证码（也就是确保最近一次登陆自己的智慧校园是登陆成功的），那么请在这里随意填写

~~后续其他学校的模拟登陆请提供你的账号密码学校名称等给我，来进行适配（又一波坑）~~

#### 2、信息收集

如何使用信息收集，基本只需要修改`今日校园/config.yml`中的`- user`里的配置信息

其中有个type选项，在`config.yml`有着详尽的说明，如果您不会使用，那么请询问吧

信息收集是在`config.yml`中的第二个用户配置里，有着对应的模板，默认模板仅试用于`宜宾学院`

#### 3、签到

如何使用签到，基本只需要修改`今日校园/config.yml`中的`- user`里的配置信息

其中有个type选项，在`config.yml`有着详尽的说明，如果您不会使用，那么请询问吧

信息收集是在`config.yml`中的第三个用户配置里，有着对应的模板，默认模板仅试用于`武汉船舶职业技术学院`

#### 4、查寝

如何使用查寝，基本只需要修改`今日校园/config.yml`中的`- user`里的配置信息

其中有个type选项，在`config.yml`有着详尽的说明，如果您不会使用，那么请询问吧

信息收集是在`config.yml`中的第四个用户配置里，有着对应的模板，默认模板仅试用于`四川信息技术职业学院`

#### 5、工作日志

如何使用工作日志，基本只需要修改`今日校园/config.yml`中的`- user`里的配置信息

其中有个type选项，在`config.yml`有着详尽的说明，如果您不会使用，那么请询问吧

信息收集是在`config.yml`中的第一个用户配置里，有着对应的模板，默认模板仅试用于`宜宾学院`

#### 6、多用户配置

同样的，多用户配置方法已经在`config.yml`中给出了对应的模板，并且可以签到、信息收集、查寝、工作日志

#### 5、查寝

等待开发ing~~（日常挖坑）~~

#### 7、关于依赖

1. 腾讯云的云函数已经拥有了自己的终端，那么我们不再需要创建层了，请将`今日校园`文件夹里的代码打包成`zip`并上传到腾讯云，最后到`requirements.txt`目录（一般情况应该也就是上传后的`src`目录里）执行以下命令

   （腾讯云函数新版本编辑器，下方有个终端，打开它，并且执行`cd ./src`即可进入到`src`目录）

   `pip install -r requirements.txt -t ./ -i https://mirrors.aliyun.com/pypi/simple`

   当然，盲猜你们都是`python3`，那么请使用`pip3`代替`pip`

   也就是

   `pip3 install -r requirements.txt -t ./ -i https://mirrors.aliyun.com/pypi/simple`

2. 如果你是阿里云，先将`依赖.zip`解压到`依赖`文件夹，然后将`今日校园`文件夹里的所有文件及代码全部复制到`依赖`文件夹。并且重新将整个`依赖`文件夹打包成`zip`格式一并上传到阿里云。

3. 如果你是本地环境，那么请直接进入到`requirements.txt `对应目录执行命令

   `pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple`

#### 8、食用方法

1. 下载全部源码，然后请查看**第6步：关于依赖**，以解决对应环境的依赖问题
2. 修改对应的`config.yml`文件，记得删除多余的配置项，默认使用了两个用户的配置项，并且第一个`- user`是`签到`配置，第二个`- user`是`信息收集的配置`
3. 之后即可*enjoy it*~~（师兄最爱的话语）~~

#### 9、关于推送

由于个人觉得推送没啥用，所以就没写，如果你会代码，那么请自行加上推送代码，如果不会代码的人多且想要推送功能，我将添加一个邮件推送功能

PS:正在尝试着自己借助于 [YuQ](https://yuqworks.gitee.io/yuq-doc/#/) 制作一个类似于`qmsg`的QQ推送平台

#### 10、更新日志

- 新增查寝模块`sleepCheck`，添加`debug`模式，可在`config.yml`中修改，用以找到错误是哪个位置 `v1.1.1`
- 新增邮件推送开关，当`config.yml`中的`- user`里的`email`为如下格式：`email: ''`，将不推送邮件 `v1.1.0`
- 新增一个`cas`学校的登陆（河南大学），新增`henuLogin`模块 `v1.0.9`
- 完成邮件推送功能 `v1.0.8`
- 修复签到值错误但不提示的bug `v1.0.7`
- 完成`教师端`的`工作日志`：新增`workLog`类 `v1.0.6`
- 制作视频，提取`Utils`公用模块 `v1.0.5`
- 修复签到失效 `v1.0.4`
- 完成`签到任务`，新增`autoSign`模块，修复bug `v1.0.3`
- 完成`iap`学校的登陆，新增`iapLogin`模块完善文档 `v1.0.2`
- 完成部分通用`cas`学校的登陆适配，并完成`信息收集`，新增`casLogin`模块和`collection`模块 `v1.0.1`
- 项目初始化（克隆自`子墨师兄`的代码）`v1.0`，新建`ruoli`分支并在其上魔改