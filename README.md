# auto-submit

#### 今日校园每日自动提交疫情上报py脚本，支持邮件推送提交结果消息，支持几乎所有学校

#### 使用了此脚本或者参考了这个项目，请自觉给项目点个star

#### 本项目仅供学习交流使用，如作他用所承受的任何直接、间接法律责任一概与作者无关

#### 如果此项目侵犯了您或者您公司的权益，请立即联系我删除

# 项目说明

- `config.yml` 默认配置文件
- `config_xxxx.yml` xx学校的配置文件，xxxx是学校英文简称
- `index.py` 完成自动提交的py脚本
- `generate.py` 帮助生成默认项配置的py脚本
- `requirements.txt` py依赖库以及版本说明文件
- `fzu` 针对福州大学的同学们

# 使用方式

## 宜宾学院的同学
   
### 配合腾讯云函数使用（免费）

1. clone 或者 下载 此仓库到本地
    ```shell script
    git clone https://github.com/ZimoLoveShuang/auto-submit.git
    ```
2. 打开本地仓库文件夹，配置`config.yml`中对应的学号（username）和密码（password）还有地址（address）等等信息，详情请看`config.yml`中的注释说明，**注意这里的学号和密码都是智慧校园的学号和密码**
3. 打开百度搜索[腾讯云函数](https://console.cloud.tencent.com/scf/index?rid=1)，注册认证后，进入控制台，点击左边的层，然后点新建，名称随意，然后点击上传zip，选择release中的`dependency.zip`上传，然后选择运行环境`python3.6`，然后点击确定，耐心等待一下，上传依赖包需要花费的时间比较长
![新建腾讯云函数依赖](screenshots/ed6044e6.png)
4. 点左边的函数服务，新建云函数，名称随意，运行环境选择`python3.6`，创建方式选择空白函数，然后点击下一步
![新建腾讯云函数](screenshots/a971478e.png)
5. 提交方法选择在线编辑，把本地修改好的`index.py`直接全文复制粘贴到云函数的`index.py`，然后点击文件->新建，文件名命名为`config.yml`，然后把本地配置好的`config.yml`文件中的内容直接全文复制粘贴到云函数的`config.yml`文件，点击下面的高级设置，设置超时时间为`60秒`，添加层为刚刚新建的函数依赖层，然后点击完成
![配置腾讯云函数](screenshots/1aa80c41.png)
6. 进入新建好的云函数，左边点击触发管理，点击创建触发器，名称随意，触发周期选择自定义，然后配置cron表达式，下面的表达式表示每天中午十二点整执行
    ```shell script
   0 0 12 * * * *
    ```
7. 然后就可以测试云函数了，绿色代表云函数执行成功，红色代表云函数执行失败（失败的原因大部分是由于依赖造成的）。返回结果是`auto submit fail.`代表自动提交失败；返回结果是`auto submit success.`，代表自动提交成功，如遇到问题，请仔细查看日志
8. enjoy it!
9. 也可配合Windows计划任务或者使用linux定时任务，将脚本挂在自己的云服务器上，不会就搜索一下，过程不再赘述

#### 如果你不会配置表单组默认选项配置，请先配置好`user`信息之后本地执行`generate.py`，根据提示信息手动输入，然后将分割线下的内容复制到配置文件中对应位置；如果问题中有省市县三级联动的位置，按`xx省/xx市/xx县`这个格式输入文本即可

## 其他学校的同学

使用方式同宜宾学院同学，但请注意修改`index.py`中`21`行，读取的配置文件要和你的配置文件名称对应
```python
config = getYmlConfig(yaml_file='config.yml')
```

## 福州大学的同学

1. clone 或者 下载 此仓库到本地
    ```shell script
    git clone https://github.com/ZimoLoveShuang/auto-submit.git
    ```
2. 进入`auto-submit`目录下，安装依赖，命令`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple`
3. 打开本地仓库文件夹下的`fzu`文件夹，配置`config.yml`
4. 本地执行`python login.py`获取到`sessionToken`，`acw_tc`，`MOD_AUTH_CAS`和`CpdailyInfo`，填入`fzu/index.py`对应位置
5. 配置腾讯云函数，依赖层配置和上面一样，提交方法选择提交文件夹，请选择`fzu`文件夹，触发管理和上面一样
6. enjoy it!!!
7. 注意：如果你本地有多个python环境，请使用`python3`

# 封禁白嫖说明

#### 白嫖党太多且几乎定时为同一时刻，导致高并发，使得提供模拟登陆API的服务器响应很不稳定，已采取封禁措施

#### 封禁策略：未授权的账号只能使用一次模拟登陆API接口

#### 解封联系QQ：461009747，捐赠（金额不限），收到的捐赠将会用于购买和续费或者购买更好的服务器

#### 也欢迎有服务器的同学贡献出服务器，造福本校同学；如不会部署模拟登陆API服务，可以联系我

#### 目前通过测试的学校

<table>
    <thead>
        <tr>
            <th>学校名称</th>
            <th>学校英文简称</th>
            <th>加入今日校园的方式</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>宜宾学院</td>
            <td>yibinu</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>安徽农业大学经济技术学院</td>
            <td>jjjs</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>中国矿业大学</td>
            <td>cumt</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>惠州市技师学院</td>
            <td>hzti</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>西南大学</td>
            <td>swu</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>长江师范学院</td>
            <td>yznu</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>新乡医学院</td>
            <td>xxmu</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>天津天狮学院</td>
            <td>tianshi</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>河南大学</td>
            <td>henu</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>韩山师范学院</td>
            <td>hstc</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>白城师范学院</td>
            <td>bcnu</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>成都师范学院</td>
            <td>cdsf</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>江西理工大学</td>
            <td>jxust</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>南京农业大学</td>
            <td>njau</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>贵州医科大学</td>
            <td>gmc</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>大连海洋大学</td>
            <td>dlou</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>广东工贸职业技术学院</td>
            <td>gdgm</td>
            <td>NOTCLOUD</td>
        </tr>
        <tr>
            <td>合肥工业大学</td>
            <td>hfut</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>河南中医药大学</td>
            <td>hactcm</td>
            <td>NOtCLOUD</td>
        </tr>
        <tr>
            <td>新乡学院</td>
            <td>xxu</td>
            <td>CLOUD</td>
        </tr>
        <tr>
            <td>华侨大学</td>
            <td>hqu</td>
            <td>NOTCLOUD</td>
        </tr>
    </tbody>
</table>

#### 福州大学的同学自动签到和每日一报均已支持，每日一报请看fzu文件夹，签到请看[auto-sign项目的fzu文件夹](https://github.com/ZimoLoveShuang/auto-sign)

# 说明

1. 此项目**默认配置适用于宜宾学院学子，也欢迎其他学校同学提交适合自己学校的配置**，命名为`config_学校英文简称.yml`，示例：`config_hzti.yml`，hzti是惠州市技师学院的英文简称，不需要<s>抓包</s>
2. 此项目依赖`python3.8`运行环境，如没有，自行安装
3. 此项目依赖`PyYAML oss2 urllib requests json `等python库，如没有，自行安装，**参考命令**
    ```shell script
    pip install -r requirements.txt -t . -i https://mirrors.aliyun.com/pypi/simple
    ```
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
4. 目前以上两种接入方式，我提供的[模拟登陆API](https://github.com/ZimoLoveShuang/wisedu-unified-login-api.git)都能支持
5. 以上两种接入方式，登陆原理均为CAS，接口略有一点不同，但大同小异

# 其他

1. 关于[Cpdaily-Extension](https://github.com/ZimoLoveShuang/yibinu-score-crawler/blob/master/src/main/java/wiki/zimo/scorecrawler/helper/DESHelper.java)：今日校园APP的处理是登陆时获取，每台设备唯一，但是有个空子就是，只要你不退出登陆，这个就会一直被维持，一直有效，换句话说，就是在APP上手动退出后失效，所以无需重复抓包获取
![意外发现：Cpdaily-Extension](screenshots/13d573c2.png)
![意外发现：Cpdaily-Extension](screenshots/e5f77237.png)
2. 关于抓包：今日校园APP某些接口启动了`ssl pinning`机制，一般的方法无法抓包
3. 提供一个参考的 绕过 `ssl pinning`机制的方法：使用`逍遥安卓4.4.4`模拟器，配合`xposed框架`，使用`justtrustme模块`，`hook`掉验证证书的函数即可抓包
4. 此项目为自动提交疫情收集表，自动签到请参考另一个开源项目[auto-sign](https://github.com/ZimoLoveShuang/auto-sign)

# 反馈bug或者小问题 请提供完整运行日志

# 更新日志

- 2020-08-07 账号和密码都统一使用英文单引号引起来，避免某些账号会出现yml读取的内容错误的问题
- 2020-08-05 福州大学的学子不再需要手动抓包，基本完美使用
- 2020-07-31 修复某些学校校验了非必填项导致提交失败的问题
- 2020-07-25 新增针对福州大学的一些脚本，不完美
- 2020-07-17 优化自动获取登陆地址的函数，处理某些学校转发到另一个域名去进行登陆认证的情况
- 2020-07-12 新增对配置文件默认项不正确的检查，并提示
- 2020-07-09 由于根据joinType确定的登陆地址不准确，所以将自动确定登陆地址的方式，改为根据关键字确定
- 2020-07-07 新增帮助生成默认项配置的脚本，进一步降低使用难度
- 2020-07-05 打包好云函数依赖，便于将脚本部署在腾讯云函数上定时执行
- 2020-07-04 完善自动填写表单函数，增加对文本，多选，图片等表单内容的支持；其他学校的学子不需要再自己抓包，通过简化的配置文件配置完成之后即可使用，降低使用难度
- 2020-06-15 加入多用户配置，去掉容易死的休眠策略，配置文件改为yml方式，更直观，恢复默认值配置，配合log输出日志，方便debug
- 2020-06-03 去掉比较难配置的微信消息推送，改为开放邮件服务，由邮件推送消息
- 2020-05-31 由于高并发，导致提供模拟登陆API的服务器崩溃，于是尝试封禁白嫖党
- 2020-05-27 去掉繁琐的默认项配置，加入消息推送配置
- 2020-05-13 开源模拟登陆api
- 2020-04-26 优化自动填充表单的函数
- 2020-04-25 更新配置文件，使脚本支持大部分学校
- 2020-04-13 重构项目编码，抽取函数
- 2020-03-27 更新提交的表单项，适应金智更新后的接口验证
- 2020-03-18 抓到获取wid的接口，脚本不再暴力尝试，支持提交位置信息
- 2020-03-14 发布暴力尝试脚本

# 致谢

@suqir

# 回答一些问题

## 1. 为什么登陆api是用java写的，而此项目是用python写的？

> 三月初的时候，我是先用java写了宜宾学院的教务系统成绩单爬虫，然后回过头来才写的这个脚本，另一方面，java处理这样的数据，会显得过于冗余，要写的代码会多很多（我想偷懒）

## 2. 为什么要抽取出登陆过程作为另一个项目？

> 答案跟上面差不多，其实是写过一遍登陆过程了，懒得再写第二遍。另外，抽取出来有一个好处，就是模块化，可以在不影响这个项目的情况下，升级登陆api，便于更新和维护

## 3. 为什么代码写的这么烂？

> 其实是我没学过python，这应该算是我用python写的第一个小项目吧，还挺好用的，没有上手难度，拿到就能写

## 4. 为什么去掉了微信消息推送？

> 其实是有不少人跟我反馈微信消息推送配置要自己手动操作几步，嫌麻烦，不如直接输入个邮箱地址，来得方便，所以我就开放了邮件服务，其实QQ邮件也可以发送到微信通知，去邮箱app设置就好了，可以参考[https://jingyan.baidu.com/article/d5a880ebccafd813f147ccb0.html](https://jingyan.baidu.com/article/d5a880ebccafd813f147ccb0.html)，另外，如果想要微信消息推送，也可以跟我联系，如果人多，我就考虑更新，因为我找到了一个比server酱更好的解决方案，也不需要大家配置什么，大概的操作过程就是微信扫码，关注公众号，然后会收到一个key，将这个key放到配置文件，基本上就像输入邮件地址一样简单方便

## 5. 邮件接口有次数限制吗？

> 有，每个邮箱地址每天上限10条，0点刷新，正常使用完全够了，加入限制主要是 为了防止接口被滥用，毕竟这是我的私人邮箱

## 6. 这个项目会一直维护下去吗？

> 不会，因为个人精力有限，大概最多维护到九月

# 捐赠
<table>
    <tr>
        <td ><center><img src="https://img-blog.csdnimg.cn/20200303161837163.jpg" ></center></td>
        <td ><center><img src="https://img-blog.csdnimg.cn/20200303162019613.png"  ></center></td>
    </tr>
</table>
