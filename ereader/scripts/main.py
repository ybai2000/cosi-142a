import time
import os
from PIL import ImageFont, Image, ImageDraw
import json

from display import Display, Menu
from fontmanager import Fontmanager
from picolistener import PicoListener, Button
from document import Document
from tts import TTSPlayer
from camera import DocumentCamera
from ocr import process_images


class App:
    def __init__(self) -> None:
        self.button_listener = PicoListener()
        self.button_listener.listening()
        self.display = Display(50)
        self.tts_player = TTSPlayer('tmp/tts')
        self.library = []
        try:
            with open('library/.metadata.json', 'r') as file:
                self.library = json.load(file)
                if not isinstance(self.library, list):
                    print("Library metadata is not a json list")
        except FileNotFoundError:
            pass
        self.fontmanager = Fontmanager()
        self.font: ImageFont = self.fontmanager.get_current_font()
        self.line_space = 10  # todo - also store in fontconfig?

    def start(self) -> None:
        while True:
            match self.menu(["Library", "Settings"], back=False):
                case 0:
                    self.library_menu()
                case 1:
                    self.settings_menu()

    def library_menu(self) -> None:
        while True:
            doc_selection = self.menu(self.library + ["Add new document"])
            if doc_selection is None:
                return
            if doc_selection == len(self.library):
                self.capture_images(f'library/doc_{len(self.library)}')
                self.library.append(f'Document {len(self.library)}')
                with open('library/.metadata.json', 'w') as file:
                    json.dump(self.library, file)
            else:
                self.read_document(doc_selection)

    def settings_menu(self) -> None:
        while True:
            match self.menu(["Font", "Font Size"]):
                case None:
                    return
                case 0:
                    fonts = self.fontmanager.list_available_fonts()
                    font_selection = self.menu(fonts)
                    if font_selection is not None:
                        self.fontmanager.set_font(fonts[font_selection])
                        self.font = self.fontmanager.get_current_font()
                case 1:
                    sizes = self.fontmanager.list_available_sizes()
                    size_selection = self.menu([str(s) for s in sizes])
                    if size_selection is not None:
                        self.fontmanager.set_size(sizes[size_selection])
                        self.font = self.fontmanager.get_current_font()

    def menu(self, items: list[str], back=True) -> int | None:
        menu = Menu(items, self.display.width, self.display.height - self.display.button_height, (20, 20))
        self.display.draw_screen(menu.menu_image())
        self.display.draw_button_labels(["Down", "Back", "Select", "Up"])
        self.display.paint_canvas()
        while True:
            match self.button_listener.get_interrupt():
                case Button.UP:
                    menu.go_prev_item()
                    self.display.draw_screen(menu.menu_image())
                    self.display.paint_canvas()
                case Button.DOWN:
                    menu.go_next_item()
                    self.display.draw_screen(menu.menu_image())
                    self.display.paint_canvas()
                case Button.SELECT:
                    return menu.selected
                case Button.BACK:
                    if back:
                        return None

    def read_document(self, id: int) -> None:
        filename = f'library/doc_{id}/text.txt'
        doc = Document(filename, self.display.width, self.display.height - self.display.button_height, self.font,
                       self.line_space)
        page = doc.get_current_page()
        self.display.draw_screen(page.page_image())
        self.display.draw_button_labels(["Prev", "Library", "TTS", "Next"])
        self.display.paint_canvas()
        while True:
            match self.button_listener.get_interrupt():
                case Button.UP:
                    page = doc.next_page()
                    if page is not None:
                        self.display.draw_screen(page.page_image())
                        self.display.paint_canvas()
                case Button.DOWN:
                    page = doc.prev_page()
                    if page is not None:
                        self.display.draw_screen(page.page_image())
                        self.display.paint_canvas()
                case Button.SELECT:
                    self.tts_doc(doc)
                    self.display.draw_button_labels(["Prev", "Library", "TTS", "Next"])
                    self.display.paint_canvas()
                case Button.BACK:
                    self.tts_player.clean()
                    return

    def tts_doc(self, doc: Document) -> None:
        if self.tts_player.is_playing():
            self.tts_player.pause_resume()
        tts_dir = f'{doc.id}/{doc.current_page}'
        self.tts_player.add_sentences(f'{doc.id}/{doc.current_page}', doc.get_current_page().sentences)
        if doc.get_next_page():
            self.tts_player.add_sentences(f'{doc.id}/{doc.current_page + 1}', doc.get_next_page().sentences)
        self.display.draw_button_labels(["Volume Down", "", "Stop", "Volume Up"])
        while True:
            match self.button_listener.check_interrupt():
                case Button.UP:
                    self.tts_player.volume_up()
                case Button.DOWN:
                    self.tts_player.volume_down()
                case Button.SELECT:
                    self.tts_player.stop()
                    break
                case Button.BACK:
                    self.tts_player.play_prev(tts_dir)
            if not self.tts_player.is_playing():
                if self.tts_player.play_next(tts_dir):
                    self.display.draw_screen(doc.get_current_page().draw_highlight_sentences(
                        [self.tts_player.playing_sent[f'{doc.id}/{doc.current_page}'] - 1]))
                    self.display.paint_canvas()
                else:
                    doc.next_page()
                    tts_dir = f'{doc.id}/{doc.current_page}'
                    self.tts_player.remove(f'{doc.id}/{doc.current_page - 1}')
                    if doc.get_next_page():
                        self.tts_player.add_sentences(f'{doc.id}/{doc.current_page + 1}', doc.get_next_page().sentences)
            time.sleep(0.01)

    def capture_images(self, directory: str) -> None:
        # TODO: if we want to be able to add to existing files, should count the number of things in the dir here
        camera = DocumentCamera(directory=directory)
        self.display.draw_button_labels(["", "Finish", "Capture", "Retake"])
        image = Image.new("1", (self.display.width, self.display.height - self.display.button_height), 255)
        draw = ImageDraw.Draw(image)
        draw.font = ImageFont.load_default(20)
        draw.text((self.display.width / 2, (self.display.height - self.display.button_height) / 2), "Capturing Images", anchor="mm", fill="black")
        self.display.draw_screen(image)
        self.display.paint_canvas()
        while True:
            match self.button_listener.check_interrupt():
                case Button.UP:
                    camera.retake_image()
                    pass  # retake last image?
                case Button.DOWN:
                    pass  # no idea what this would be, trigger auto focus probably?
                case Button.SELECT:
                    camera.capture_image()
                case Button.BACK:
                    images = camera.done_capturing()
                    self.display.draw_button_labels(["", "", "", ""])
                    image = Image.new("1", (self.display.width, self.display.height - self.display.button_height), 255)
                    draw = ImageDraw.Draw(image)
                    draw.font = ImageFont.load_default(20)
                    draw.text((self.display.width / 2, (self.display.height - self.display.button_height) / 2), "Running OCR (slowly)", anchor="mm", fill="black")
                    self.display.draw_screen(image)
                    self.display.paint_canvas()
                    text_lines = process_images(images)
                    os.makedirs(directory, exist_ok=True)
                    with open(f"{directory}/text.txt", 'w') as file:
                        for line in text_lines:
                            file.write(line + '\n')
                    break  # done capturing?


if __name__ == '__main__':
    app = App()
    app.start()
