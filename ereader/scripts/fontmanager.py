import configparser
from PIL import ImageFont


class fontmanager():
    def __init__(self):
        self.config = configparser.ConfigParse()
        self.config.read("../fonts/fontconfig.cfg")
        