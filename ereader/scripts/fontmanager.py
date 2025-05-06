import os
import json
from PIL import ImageFont

class Fontinfo:
    def __init__(self, font_path=None, size=12):
        self.font_path = font_path
        self.size = size
        if font_path and os.path.exists(font_path):
            self.font = ImageFont.truetype(font_path, size)
        else:
            self.font = ImageFont.load_default()

    def to_dict(self):
        return {"font_path": self.font_path, "size": self.size}

    def get_font(self) -> ImageFont:
        if self.font_path is None:
            return ImageFont.load_default()
        else:
            return ImageFont.truetype(self.font_path, self.size)

    def get_size(self):
        return self.size

class Fontmanager:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_dir_path = os.path.join(script_dir, "..", "fonts")
        self.font_config_path = os.path.join(self.font_dir_path, "fontconfig.json")

        # Initialize default config if it does not exist
        if not os.path.exists(self.font_config_path):
            self.info = Fontinfo()
            with open(self.font_config_path, "w") as f:
                json.dump(self.info.to_dict(), f, indent=4)
        else:
            with open(self.font_config_path, "r") as f:
                data = json.load(f)
                self.info = Fontinfo(**data)

        self.available_fonts = [
            name for name in os.listdir(self.font_dir_path)
            if os.path.isdir(os.path.join(self.font_dir_path, name))
        ]

    def list_available_fonts(self) -> list[str]:
        return self.available_fonts

    def get_font(self) -> ImageFont:
        return self.info.get_font()
    
    def select_font(self):
        # TODO: Implement font selection logic
        return

if __name__ == "__main__":
    fm = Fontmanager()
    print(fm.list_available_fonts())