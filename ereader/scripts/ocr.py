from PIL import Image,ImageEnhance
import pytesseract
from spacy.lang.en import English


def image_to_text(image: Image, delete_image: bool = True) -> str:
    #image = Image.open(image_file).convert("L")
    contrast_enhancer=ImageEnhance.Contrast(image)
    enhanced=contrast_enhancer.enhance(1.4)
    sharpness_enhancer=ImageEnhance.Sharpness(enhanced)
    final_image=sharpness_enhancer.enhance(1.4)
    text = pytesseract.image_to_string(final_image)
    return text

def process_images(images: list[Image]) -> list[str]: #file_names: list[str]) -> list[str]:
    new_text = ""
    for image in images:
        new_text += image_to_text(image)
    nlp = English()
    nlp.add_pipe("sentencizer")
    doc = nlp(new_text.replace('\n', ' '))

    return [sent.text for sent in doc.sents]

# image_files = [
#     "ereader/test_document/ocr-sample2.png",
#     "ereader/test_document/testocr.png"
# ]


# # some stuff for testing the code on windows
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# text = process_images(image_files)
# print(text)
