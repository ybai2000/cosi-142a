import time
import os
from PIL import ImageFont

from display import Display, Menu
from fontmanager import Fontmanager
from picolistener import PicoListener, Button
from library import Document
from tts import TTSPlayer
from picamera_test import DocumentCamera
from ocr import process_images


SENTENCE_FILE_NAME = 'sentences.txt'

class App:
    def __init__(self) -> None:
        self.button_listener = PicoListener()
        self.button_listener.listening()
        self.screen = Display(600, 400, ImageFont.load_default(), 30, 10)
        self.tts_player = TTSPlayer('../tts')

    def menu_test(self):
        menu = Menu(["a", "b", "c", "d"], self.screen.width, self.screen.height - self.screen.button_height, (20, 20), self.screen.font)
        self.screen.draw_screen(menu.menu_image())
        self.screen.draw_button_labels(["Down", "Back", "Select", "Up"])
        self.screen.paint_canvas()
        while True:
            b = self.button_listener.get_interrupt()
            print(b)
            match b:
                case Button.UP:
                    menu.go_prev_item()
                    self.screen.draw_screen(menu.menu_image())
                    self.screen.paint_canvas()
                case Button.DOWN:
                    menu.go_next_item()
                    self.screen.draw_screen(menu.menu_image())
                    self.screen.paint_canvas()
                case Button.SELECT:
                    print(menu.selected)
                case Button.BACK:
                    break  # go back to menu



    def read_file(self, file: str) -> None:
        doc = Document(file, self.screen.width, self.screen.height, self.screen.height, self.screen.line_space)
        page = doc.get_current_page()
        self.screen.draw_screen(page.page_image())
        while True:
            match self.button_listener.check_interrupt():
                case Button.UP:
                    page = doc.next_page()
                    self.screen.draw_screen(page.page_image())
                case Button.DOWN:
                    page = doc.prev_page()
                    self.screen.draw_screen(page.page_image())
                case Button.SELECT:
                    self.tts_file(doc)
                case Button.BACK:
                    break  # go back to menu
            time.sleep(0.01)
        self.tts_player.clean()


    # always load tts even if not playing?
    def tts_file(self, doc: Document) -> None:
        # maybe better to just have sentence restart when resume instead of continue in middle?
        if self.tts_player.is_playing():
            self.tts_player.pause_resume()
        tts_dir = f'{doc.id}/{doc.current_page}'
        while True:
            match self.button_listener.check_interrupt():
                case Button.UP:
                    self.tts_player.volume_up()
                case Button.DOWN:
                    self.tts_player.volume_down()
                case Button.SELECT:
                    self.tts_player.pause_resume()
                    break
                case Button.BACK:
                    self.tts_player.play_prev(tts_dir)
            if not self.tts_player.is_playing() and not self.tts_player.play_next(tts_dir):
                doc.next_page()
                tts_dir = f'{doc.id}/{doc.current_page}'
                self.tts_player.play_next(tts_dir)
                self.tts_player.remove(f'{doc.id}/{doc.current_page - 1}')
                self.tts_player.add_sentences(f'{doc.id}/{doc.current_page + 1}', doc.get_next_page())
                # todo change page on screen - shared function between tts mode and read mode? - that maybe updates tts too
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

        with open(os.path.join(directory,SENTENCE_FILE_NAME)) as file:
            file.write(new_text)


    def set_font(self) -> None:
        fontmanager = Fontmanager()
        
        while True:
            match self.button_listener.check_interrupt():
                case Button.UP:
                    # TODO
                    pass
                case Button.DOWN:
                    # TODO
                    pass
                case Button.SELECT:
                    # TODO
                    pass
                case Button.BACK:
                    # TODO
                    break

        self.screen = Display(600, 400, fontmanager.get_current_font(), 0, 10)


if __name__ == '__main__':
    app = App()
    app.menu_test()
    # app.read_file('../library/star_wars.txt')
