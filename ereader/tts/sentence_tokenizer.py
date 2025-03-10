import nltk
import os

class SentenceTokenizer:

    def __init__(self):
        self.tokenizer = nltk.sent_tokenize

    def tokenize_sent(self, corpus: str, file_name="temp", path="ereader/tts/temp_tokenized") -> None:
        sentences = self.tokenizer(corpus)
        complete_name = os.path.join(path, file_name + '.txt')
        os.makedirs(path, exist_ok=True)
        with open(complete_name, "w") as f:
            for sent in sentences:
                f.write("%s\n" % sent)