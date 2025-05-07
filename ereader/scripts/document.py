from PIL import ImageFont

from display import Page

class Document:
    def __init__(self, path: str, width: int, height: int, font: ImageFont, line_space: int) -> None:
        with open(path, 'r') as file:
            self.sentences: list[str] = file.read().splitlines()
        self.pages: list[Page] = Page.generate_pages(width, height, font, line_space, self.sentences)
        self.current_page = 1  # read from metadata if not 1
        self.id = 0 # numerical designation of document

    def get_page(self, num: int) -> Page:
        if num < 1 or num > len(self.pages):
            raise ValueError(f'Page {num} is out of range')
        return self.pages[num - 1]

    def get_current_page(self) -> Page:
        return self.get_page(self.current_page)

    def get_next_page(self) -> Page:
        return self.get_page(self.current_page + 1)

    def get_prev_page(self) -> Page:
        return self.get_page(self.current_page - 1)

    def next_page(self) -> Page | None:
        if self.current_page == len(self.pages):
            return None
        self.current_page += 1
        return self.get_page(self.current_page)

    def prev_page(self) -> Page | None:
        if self.current_page == 1:
            return None
        self.current_page -= 1
        return self.get_page(self.current_page)
