from picamera2 import Picamera2, Preview
from picamera2.controls import Controls
import time

    
class DocumentCamera:
    def __init__(self, directory: str, num_pages:  int = 0) -> None:
        self.camera = Picamera2()
        camera_config = self.camera.create_preview_configuration()
        self.camera.configure(camera_config)
        self.controls = Controls(self.camera)
        self.controls.AfMode = 2  # Auto-focus mode (2 corresponds to Auto)
        self.controls.AfSpeed = 1  # Fast focus speed
        self.directory = directory
        self.num_pages = num_pages

    def capture_image(self) -> str:
        image_file = f'image_{self.num_pages}.jpg'
        self.camera.start()
         time.sleep(2) 
        self.camera.capture_file(image_file)
        self.camera.stop()
        self.num_pages += 1
        return image_file




if __name__ == '__main__':
        picam2 = Picamera2()
        camera_config = picam2.create_preview_configuration()
        picam2.configure(camera_config)
        picam2.start_preview(Preview.QTGL)
        picam2.start()
        time.sleep(2)
        picam2.capture_file("test.jpg")
