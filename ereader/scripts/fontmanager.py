from collections import defaultdict
import os
import json
import re
from PIL import ImageFont, ImageDraw, Image

# FontManager: A class to manage font loading and configuration
# FontCollection: A class to load and manage a collection of fonts
# Fontinfo: A class to represent font information
# FontNotAvailableError: A custom exception for when a font is not available
class FontNotAvailableError(Exception):
    pass

class FontCollection:
    """A class to manage a collection of fonts."""
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
        """Load styles (regular, italic, bold, bolditalic) for a font family."""
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
    """A class to represent system font information."""
    def __init__(self, font_path=None, size=12):
        self.font_path = font_path
        self.size = size
        # Load the font if a path is provided
        if font_path and os.path.exists(font_path):
            self.font = ImageFont.truetype(font_path, size)
        # If no font path is provided, load the default font
        else:
            self.font = ImageFont.load_default(self.size)

    def to_dict(self) -> dict:
        """Serialize the font information to a dictionary."""
        return {"font_path": self.font_path, "size": self.size}

    def get_font(self) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Retrieve the font object."""
        if self.font_path is None:
            return ImageFont.load_default()
        else:
            return ImageFont.truetype(self.font_path, self.size)

    def get_size(self) -> float:
        """Get the font size."""
        return self.size
    
    def set_size(self, size: float) -> None:
        """Set the font size."""
        self.size = size
        if self.font_path:
            self.font = ImageFont.truetype(self.font_path, size)
        else:
            self.font = ImageFont.load_default(size=size)
            self.font_path = None

class Fontmanager:
    """
    A class to manage font loading and configuration.
    It handles loading fonts from a specified directory, managing font styles,
    and saving the current font configuration to a JSON file.
    
    Attributes:
        font_dir_path (str): Path to the directory containing font files.
        font_config_path (str): Path to the JSON file for saving font configuration.
        font_collection (FontCollection): Instance of FontCollection to manage fonts.
        current (Fontinfo): Instance of Fontinfo representing the current font configuration.

    Methods:
        list_available_fonts() -> list[str]: List all available fonts in the collection.
        list_available_styles(font_name: str) -> list[str]: List all available styles for a given font.
        set_font(font_name: str, style: str) -> None: Set the font and style for the Fontinfo object.
        get_current_font() -> ImageFont.FreeTypeFont: Get the current font object.
        get_currnent_size() -> float: Get the current font size.
        increase_font_size() -> None: Increase the font size by 1.
        decrease_font_size() -> None: Decrease the font size by 1, ensuring it doesn't go below 1.
    """
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.font_dir_path = os.path.join(script_dir, "..", "fonts")
        self.font_config_path = os.path.join(self.font_dir_path, "fontconfig.json")
        self.font_collection = FontCollection(self.font_dir_path)

        # Initialize default config if it does not exist
        if not os.path.exists(self.font_config_path):
            self.current = Fontinfo()
            self._save_font_config()
        # Load the current font configuration
        else:
            try:
                with open(self.font_config_path, "r") as f:
                    data = json.load(f)
                    self.current = Fontinfo(**data)
            # Handle case where JSON is malformed or missing
            except json.JSONDecodeError:
                self.current = Fontinfo()
                self._save_font_config()

    def list_available_fonts(self) -> list[str]:
        """List all available fonts in the collection."""
        return list(self.font_collection.fonts.keys())
    
    def list_available_styles(self, font_name: str) -> list[str]:
        """List all available styles for a given font."""
        if font_name in self.font_collection.fonts:
            return list(self.font_collection.fonts[font_name].keys())
        else:
            raise FontNotAvailableError(f"Font '{font_name}' not found.")

    def set_font(self, font_name: str, style: str) -> None:
        """Set the font and style for the Fontinfo object."""
        try:
            font_path = self.font_collection.get_font(font_name, style)
            self.current.font_path = font_path
            with open(self.font_config_path, "w") as f:
                json.dump(self.current.to_dict(), f, indent=4)
        except FontNotAvailableError as e:
            print(e)

    def get_current_font(self) -> ImageFont.FreeTypeFont:
        """Get the current font object."""
        return self.current.get_font()

    def get_currnent_size(self) -> float:
        """Get the current font size."""
        return self.current.get_size()
    
    def increase_font_size(self) -> None:
        """Increase the font size by 1."""
        self.current.size += 1
        self._save_font_config()

    def decrease_font_size(self) -> None:
        """Decrease the font size by 1, ensuring it doesn't go below 1."""
        if self.current.size > 1:
            self.current.size -= 1
            self._save_font_config()
        
    def _save_font_config(self) -> None:
        """Save the current font configuration to the JSON file."""
        with open(self.font_config_path, "w") as f:
            json.dump(self.current.to_dict(), f, indent=4)

if __name__ == "__main__":
    fm = Fontmanager()
    print("Available fonts:", fm.list_available_fonts())
    font_name = fm.list_available_fonts()[1]
    print("Available styles for", font_name, ":", fm.list_available_styles(font_name))
    fm.set_font(font_name, "regular")
    print("Current font object:", fm.get_current_font())
    print("Font size:", fm.get_currnent_size)

    sample_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    out = Image.new("1", (500, 500), 1)
    draw = ImageDraw.Draw(out)
    draw.text((10, 10), sample_text, font=fm.get_current_font(), fill=0)
    out.show()
    out.save("test.png")
    out.close()
    os.remove("test.png")
