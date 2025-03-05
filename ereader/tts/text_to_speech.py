import pyttsx3


class MyTTS:
    def __init__(self) -> None:
        '''
        Initialize the TTS engine
        '''
        self.engine = pyttsx3.init()
        self.engine.say("Hello, I am your eReader. How can I help you?")
        self.engine.runAndWait()


if __name__ == "__main__":
    tts = MyTTS()
