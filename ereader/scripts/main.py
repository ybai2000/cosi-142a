import threading
import time

from display import Display
from picolistener import PicoListener, Button
from library import Document
from tts import TTSPlayer
from picamera_test import DocumentCamera, image_filename
from ocr import process_images
import os


SENTENCE_FILE_NAME = 'sentences.txt'

class App:
    def __init__(self) -> None:
        self.button_listener = PicoListener()
        self.screen = Display()
        self.tts_player = TTSPlayer('../tts')

    def read_file(self, file: str) -> None:
        doc = Document(file)
        while True:
            match self.button_listener.check_interrupt():
                case Button.UP:
                    page = doc.get_next_page()
                case Button.DOWN:
                    page = doc.get_prev_page()
                case Button.SELECT:
                    self.tts_file(doc)
                case Button.BACK:
                    break  # go back to menu
            time.sleep(0.01)
        self.tts_player.clean()

    def go_next_page(self):
        pass

    # always load tts even if not playing?
    def tts_file(self, doc: Document) -> None:
        # maybe better to just have sentence restart when resume instead of continue in middle?
        if self.tts_player.is_playing():
            self.tts_player.pause_resume()
        tts_dir = f'{doc.id}/{doc.current_page}'
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
            
if __name__ == '__main__':
    

