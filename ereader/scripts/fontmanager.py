from collections import defaultdict
import os
import json
import re
from PIL import ImageFont

class FontNotFoundError(Exception):
    pass

class FontNotAvailableError(Exception):
    pass

class FontCollection:
    def __init__(self, collection_path=None):
        self.collection_path = collection_path
        self.fonts = defaultdict(dict)  # Store fonts by name and style
        if collection_path and os.path.exists(collection_path):
            self._load_fonts()

    def _load_fonts(self) -> None:
        """Load all fonts from the collection path."""
        for font_dir in os.listdir(self.collection_path):
            font_path = os.path.join(self.collection_path, font_dir)
            if os.path.isdir(font_path):
                self._load_font_styles(font_dir, font_path)

    def _load_font_styles(self, font_name, font_path) -> None:
        """Load styles (e.g., regular, italic, bold) for a font family."""
        style_map = {
            "regular": re.compile(r".*-Regular\.ttf$", re.IGNORECASE),
            "italic": re.compile(r".*-Italic\.ttf$", re.IGNORECASE),
            "bold": re.compile(r".*-Bold\.ttf$", re.IGNORECASE),
            "bolditalic": re.compile(r".*-BoldItalic\.ttf$", re.IGNORECASE),
        }
        for file in os.listdir(font_path):
            for style, pattern in style_map.items():
                if pattern.match(file):
                    self.fonts[font_name][style] = os.path.join(font_path, file)

    def get_font(self, name, style='regular') -> str:
        """Retrieve the font path for a given name and style."""
        if name in self.fonts and style in self.fonts[name]:
            return self.fonts[name][style]
        raise FontNotAvailableError(f"Font '{name}' with style '{style}' not found.")

    def list_fonts(self) -> dict:
        """List all available fonts with their styles."""
        return {name: list(styles.keys()) for name, styles in self.fonts.items()}

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

        self.fonts_to_path = {
            name: os.path.join(self.font_dir_path, name)
            for name in os.listdir(self.font_dir_path)
            if os.path.isdir(os.path.join(self.font_dir_path, name))
        }

    def list_available_fonts(self) -> list[str]:
        return list(self.fonts_to_path.keys())

    def set_font(self, name: str, size: float=12):
        if name in self.list_available_fonts():
            self.info = Fontinfo(self.fonts_to_path[name], size)
            with open(self.font_config_path, "w") as f:
                json.dump(self.info.to_dict(), f, indent=4)

    def get_font(self) -> ImageFont:
        return self.info.get_font()

if __name__ == "__main__":
    fc = FontCollection()

    # List all fonts and their available styles
    print(fc.list_fonts())

    # Get the path to a specific font and style
    try:
        font_path = fc.get_font("Arial", "italic")
        print(f"Path to Arial italic: {font_path}")
    except FontNotAvailableError as e:
        print(e)