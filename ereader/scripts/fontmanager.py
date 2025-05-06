import configparser
import os
from PIL import ImageFont


class fontmanager():
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.path: str = os.path.join(script_dir, "..", "fonts")
        self.available_fonts: list[str] = [
            name for name in os.listdir(self.path)
            if os.path.isdir(os.path.join(self.path, name))
        ]
        self.config = configparser.ConfigParser()

    def get_font(self) -> ImageFont:
        return self.font
if __name__ == "__main__":
    fm = fontmanager()
    print(fm.available_fonts)
