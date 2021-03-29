

class currencyLogin:
    # 初始化通用登陆类
    def __init__(self, username, password, login_url, host, session):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.host = host
        self.session = session

    # 定义一个登陆方法
    def login(self):
        print(self.login_url)
        print('通用登陆正在制作中，please wait for a long time...')
        exit()