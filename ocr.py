from PIL import Image

import pytesseract

print(pytesseract.image_to_string(Image.open('test-image-for-recognition.png')))


print('done')