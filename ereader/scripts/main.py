import time
import os
from PIL import ImageFont
import json

from display import Display, Menu
from picolistener import PicoListener, Button
from document import Document
from tts import TTSPlayer
from picamera_test import DocumentCamera
from ocr import process_images

SENTENCE_FILE_NAME = 'sentences.txt'


class App:
    def __init__(self) -> None:
        self.button_listener = PicoListener()
        self.button_listener.listening()
        self.display = Display(ImageFont.load_default(), 30, 10)
        self.tts_player = TTSPlayer('tts')
        with open('library/.metadata.json', 'r') as file:
            self.library = json.load(file)
            if not isinstance(self.library, list):
                print("Library metadata is not a json list")

    def start(self) -> None:
        while True:
            match self.menu(["Library", "Settings"]):
                case 0:
                    library_selection = self.menu(self.library + ["Add new document"])
                    if library_selection == len(self.library):
                        pass  # ocr for new doc
                    else:
                        self.read_document(library_selection)
                case 1:
                    pass # settings (font selection)

    def menu(self, items: list[str]) -> int | None:
        menu = Menu(items, self.display.width, self.display.height - self.display.button_height, (20, 20),
                    self.display.font)
        self.display.draw_screen(menu.menu_image())
        self.display.draw_button_labels(["Down", "Back", "Select", "Up"])
        self.display.paint_canvas()
        while True:
            b = self.button_listener.get_interrupt()
            print(b)
            match b:
                case Button.UP:
                    menu.go_prev_item()
                    self.display.draw_screen(menu.menu_image())
                    self.display.paint_canvas()
                case Button.DOWN:
                    menu.go_next_item()
                    self.display.draw_screen(menu.menu_image())
                    self.display.paint_canvas()
                case Button.SELECT:
                    print(menu.selected)
                case Button.BACK:
                    return None

    def read_document(self, id: int) -> None:
        filename = f'doc_{id}/text.txt'
        doc = Document(filename, self.display.width, self.display.height, self.display.font, self.display.line_space)
        page = doc.get_current_page()
        self.display.draw_screen(page.page_image())
        self.display.paint_canvas()
        while True:
            match self.button_listener.get_interrupt():
                case Button.UP:
                    page = doc.next_page()
                    self.display.draw_screen(page.page_image())
                    self.display.paint_canvas()
                case Button.DOWN:
                    page = doc.prev_page()
                    self.display.draw_screen(page.page_image())
                    self.display.paint_canvas()
                case Button.SELECT:
                    self.tts_file(doc)
                case Button.BACK:
                    self.tts_player.clean()
                    return

    def tts_file(self, doc: Document) -> None:
        if self.tts_player.is_playing():
            self.tts_player.pause_resume()
        tts_dir = f'{doc.id}/{doc.current_page}'
        self.tts_player.add_sentences(f'{doc.id}/{doc.current_page}', doc.get_current_page().sentences)
        if doc.get_next_page():
            self.tts_player.add_sentences(f'{doc.id}/{doc.current_page + 1}', doc.get_next_page().sentences)
        while True:
            match self.button_listener.check_interrupt():
                case Button.UP:
                    pass  # volume up
                case Button.DOWN:
                    pass  # volumne down
                case Button.SELECT:
                    self.tts_player.pause_resume()
                    break
                case Button.BACK:
                    self.tts_player.play_prev(tts_dir)
            if not self.tts_player.is_playing():
                if self.tts_player.play_next(tts_dir):
                    self.display.draw_screen(doc.get_current_page().draw_highlight_sentences(
                        [self.tts_player.playing_sent[f'{doc.id}/{doc.current_page}']]))
                    self.display.paint_canvas()
                else:
                    doc.next_page()
                    tts_dir = f'{doc.id}/{doc.current_page}'
                    self.tts_player.play_next(tts_dir)
                    self.tts_player.remove(f'{doc.id}/{doc.current_page - 1}')
                    if doc.get_next_page():
                        self.tts_player.add_sentences(f'{doc.id}/{doc.current_page + 1}', doc.get_next_page().sentences)
            time.sleep(0.01)

    def capture_images(self, directory: str) -> None:
        # TODO: if we want to be able to add to existing files, should count the number of things in the dir here
        camera = DocumentCamera(directory=directory)
        new_images = []
        while True:
            match self.button_listener.check_interrupt():
                case Button.UP:
                    pass  # retake last image?
                case Button.DOWN:
                    pass  # no idea what this would be, trigger auto focus probably?
                case Button.SELECT:
                    new_images.append(camera.capture_image())
                case Button.BACK:
                    break  # done capturing?

        new_text = process_images(new_images)

        with open(os.path.join(directory, SENTENCE_FILE_NAME)) as file:
            file.write(new_text)


if __name__ == '__main__':
    app = App()
    app.menu_test()
    # app.read_file('../library/star_wars.txt')
