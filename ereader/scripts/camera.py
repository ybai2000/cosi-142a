from picamera2 import Picamera2, Preview
from libcamera import controls
import time
from PIL import Image

    
class DocumentCamera:
    def __init__(self, directory: str, num_pages:  int = 0) -> None:
        #self.camera = Picamera2()
        #self.capture_config = self.camera.create_still_configuration()
        #self.camera.configure("preview")
        self.camera = Picamera2()
        self.camera.configure("preview")
        self.camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        self.camera.start_preview(Preview.QTGL)
        self.camera.start()
        self.directory = directory
        self.images = []

    def capture_image(self) -> str:
        self.capture_config = self.camera.create_still_configuration()
        array = self.camera.switch_mode_and_capture_array(self.capture_config, "main")
        img = Image.fromarray(array)
        self.images.append(img)
        img.show()
        
    def retake_image(self) -> str:
        if len(self.images) > 0:
            self.images = self.images[:-1]
        self.capture_image()
        
    def done_capturing(self):
        self.camera.close()
        return self.images
                




if __name__ == '__main__':
        picam2 = Picamera2()
        capture_config = picam2.create_still_configuration()
        picam2.start(show_preview=True)
        time.sleep(3)
        array = picam2.switch_mode_and_capture_array(capture_config, "main")
        img = Image.fromarray(array)
        img.show()
