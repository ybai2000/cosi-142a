from typing import Iterable, Sequence
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd4in26
import math


class Page:
    def __init__(self, width: int, height: int, font: ImageFont, line_space: int) -> None:
        # tuple is (start_x, start_y, string)
        self.sentence_segments: list[list[tuple[int, int, str]]] = []
        self.sentences: list[str] = []
        self.width = width
        self.height = height
        self.font = font
        self.line_height, descent = font.getmetrics()
        self.line_space = line_space if line_space >= descent * 2 else descent * 2
        self.max_lines = self.height // (self.line_height + self.line_space)
        if self.height % (self.line_height + self.line_space) >= (self.line_height + descent):
            self.max_lines += 1
        self.lines = ['']
        self.image = Image.new("1", (self.width, self.height), 255)
        self.image_drawn = False
        self.draw = ImageDraw.Draw(self.image)
        self.draw.font = self.font

    def page_image(self) -> Image:
        self.image_drawn = True
        for i, line in enumerate(self.lines):
            self.draw.text((0, i * (self.line_height + self.line_space)), line)
        return self.image

    def draw_highlight_sentences(self, sentences: Sequence[int]) -> Image:
        if not self.image_drawn:
            self.page_image()
        segments = []
        for sentence in sentences:
            segments.extend(self.sentence_segments[sentence])
        print(segments)
        ascent, descent = self.font.getmetrics()
        box_height = ascent + descent
        highlighted_image = self.image.copy()
        draw = ImageDraw.Draw(highlighted_image)
        draw.font = self.font
        for item in segments:
            draw.rectangle((item[0], item[1], item[0] + draw.textlength(item[2]), item[1] + box_height), fill=0)
            draw.text((item[0], item[1]), item[2], fill=255)
        return highlighted_image


    def add_sentence(self, sentence: str) -> str | None:
        # todo make it split words larger than width? currently just breaks
        start_x = self.draw.textlength(self.sentence_segments[-1][-1][2] + ' ') if self.sentence_segments else 0
        segment_start_word = 0
        words = sentence.split(' ')
        for i, word in enumerate(words):
            if not self.lines[-1]:
                new_line = word
            else:
                new_line = self.lines[-1] + ' ' + word
            line_length = self.draw.textlength(new_line)
            if line_length > self.width or i == len(words) - 1:
                added_words = ' '.join(words[segment_start_word:i if i < len(words) - 1 else i + 1])
                if added_words:
                    if segment_start_word == 0:
                        self.sentence_segments.append([])
                    start_y = (len(self.lines) - 1) * (self.line_height + self.line_space)
                    self.sentence_segments[-1].append((start_x, start_y, added_words))
            if line_length > self.width:
                if len(self.lines) == self.max_lines:
                    added_words = ' '.join(words[:i])
                    if added_words:
                        self.sentences.append(added_words)
                    return ' '.join(words[i:])
                segment_start_word = i
                self.lines.append(word)
                start_x = 0
            else:
                self.lines[-1] = new_line
        self.sentences.append(sentence)

    @staticmethod
    def generate_pages(width: int, height: int, font: ImageFont, line_space: int, sentences: Iterable[str]
                       ) -> list['Page']:
        pages = [Page(width, height, font, line_space)]
        for sent in sentences:
            remainder = pages[-1].add_sentence(sent)
            while remainder:
                pages.append(Page(width, height, font, line_space))
                remainder = pages[-1].add_sentence(remainder)
        return pages


class Menu:
    def __init__(self, items: list[str], width: int, height: int, margins: tuple[int, int]) -> None:
        self.items = items
        self.width = width
        self.height =  height
        self.font = ImageFont.load_default(40)
        self.images = []
        self.margins = margins
        ascent, _ = self.font.getmetrics()
        self.box_height = ascent + 2 * margins[1]
        self.items_per_page = self.height // self.box_height
        num_pages = math.ceil(len(items) / self.items_per_page)
        self.images = [Image.new("1", (self.width, self.height), 255) for i in range(num_pages)]
        for i, image in enumerate(self.images):
            draw = ImageDraw.Draw(image)
            draw.font = self.font
            for j in range(self.items_per_page):
                item_num = i * self.items_per_page + j
                if item_num == len(self.items):
                    break
                draw.rectangle((0, j * self.box_height, self.width, (j + 1) * self.box_height), outline=0)
                draw.text((margins[0], int((j + 0.5) * self.box_height)), self.items[item_num], fill="black", anchor="lm")
        self.selected = 0

    def menu_image(self) -> Image:
        image_num = self.selected // self.items_per_page
        image = self.images[image_num].copy()
        index = self.selected % self.items_per_page
        draw = ImageDraw.Draw(image)
        draw.font = self.font
        draw.rectangle((0, index * self.box_height, self.width, (index + 1) * self.box_height), fill=0, outline=0)
        draw.text((self.margins[0], int((index + 0.5) * self.box_height)), self.items[image_num * self.items_per_page + index], fill="white", anchor="lm")
        return image

    def go_item(self, index: int) -> int:
        if index >= len(self.items) or index < 0:
            raise ValueError("Index out of range")
        self.selected = index
        return index

    def go_next_item(self) -> int:
        return self.go_item((self.selected + 1) % len(self.items))

    def go_prev_item(self) -> int:
        return self.go_item((self.selected - 1) % len(self.items))



class Display:
    def __init__(self, button_height: int) -> None:
        self.button_height = button_height
        self.epd = epd4in26.EPD()
        self.epd.init()
        self.epd.Clear()
        self.width = self.epd.width
        self.height = self.epd.height
        self.canvas = Image.new("1", (self.epd.width, self.epd.height))

    def paint_canvas(self) -> None:
        self.epd.display_Partial(self.epd.getbuffer(self.canvas))

    def draw_screen(self, image: Image, margins=(0, 0)) -> None:
        self.canvas.paste(image, margins)

    def draw_button_labels(self, labels: list[str]) -> None:
        if not self.button_height > 0:
            return
        buttons = Image.new("1", (self.epd.width, self.button_height), color="white")
        draw = ImageDraw.Draw(buttons)
        draw.font = ImageFont.load_default(20)
        button_width = self.epd.width / len(labels)
        for i, label in enumerate(labels):
            draw.rectangle((button_width * i, 0, button_width * (i + 1), buttons.height), outline=0)
            draw.text((button_width * (2 * i + 1) / 2, buttons.height / 2), label, fill="black", anchor="mm")
        self.canvas.paste(buttons, (0, self.height - self.button_height))

