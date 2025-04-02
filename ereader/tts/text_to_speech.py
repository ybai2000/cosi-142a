import gtts
from gtts import gTTS
from io import BytesIO

class MyTTS:
    langs = gtts.lang.tts_langs().keys()

    def __init__(self, lang: str='en') -> None:
        self.tts = gTTS
        if (lang not in MyTTS.langs):
            self.lang = 'en'
        else:
            self.lang = lang
    
    

if __name__ == "__main__":
    tts = MyTTS()
