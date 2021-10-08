# 自动填写信息收集-模拟登陆方式

# 项目说明

- `config.yml` 默认配置文件
- `index.py` 完成自动提交的py脚本
- `generate.py` 帮助生成默认项配置的py脚本
- `login.py` 登陆并生成session.yml的py脚本

# 使用方式
1. clone 或者 下载 此仓库到本地
    ```shell script
    git clone https://github.com/A-Cepheus/auto-submit.git
    ```
2. 进入`auto-submit`目录下，安装依赖，命令`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple`
3. 打开本地仓库文件夹下的`currency`文件夹，配置`config.yml`
4. 本地执行`python login.py`会自动生成`session.yml`
5. 可以配置腾讯云函数、阿里云FC函数、或者直接在本地执行`index.py`
6. enjoy it!!!
7. 注意：如果你本地有多个python环境，请使用`python3和pip3`

### 一些使用建议（非常重要，请仔细阅读）

#### 如果你不会配置表单组默认选项配置，请先配置好`user`信息之后本地执行`generate.py`，根据提示信息手动输入，然后将分割线下的内容复制到配置文件中对应位置

#### 如果问题中有省市县三级联动的位置，按`xx省/xx市/xx县`这个格式输入文本即可

#### 除非问题和答案都完全一样，否则不建议使用多用户配置
