from PIL import Image
import pytesseract
from spacy.lang.en import English


def image_to_text(image_file: str, delete_image: bool = True) -> str:
    image = Image.open(image_file).convert("L")
    text = pytesseract.image_to_string(image)
    return text

def process_images(file_names: list[str]) -> list[str]:
    new_text = ""
    for file in file_names:
        new_text += image_to_text(file)
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
