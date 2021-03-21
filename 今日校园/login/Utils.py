import yaml


class Utils:
    def __init__(self):
        pass
    @staticmethod
    def getYmlConfig(yaml_file='./login/system.yml'):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        config = yaml.load(file_data, Loader=yaml.FullLoader)
        return dict(config)
