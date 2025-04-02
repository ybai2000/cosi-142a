import unittest
import os
import sys

sys.path.append("ereader/tts")

from sentence_tokenizer import SentenceTokenizer

class TestSentenceTokenizer(unittest.TestCase):

    def setUp(self):
        self.tokenizer = SentenceTokenizer()
        self.test_corpus = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
                            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
                            "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
        self.test_path = "ereader/tts/temp_tokenized"
        self.test_file_name = "test_output"

    def tearDown(self):
        # Clean up the created file after the test
        complete_name = os.path.join(self.test_path, self.test_file_name + '.txt')
        if os.path.exists(complete_name):
            os.remove(complete_name)
        if os.path.exists(self.test_path) and not os.listdir(self.test_path):
            os.rmdir(self.test_path)

    def test_tokenize_sent(self):
        self.tokenizer.tokenize_sent(self.test_corpus, self.test_file_name, self.test_path)
        complete_name = os.path.join(self.test_path, self.test_file_name + '.txt')
        self.assertTrue(os.path.exists(complete_name), "The output file was not created.")
        
        with open(complete_name, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 4, "The number of sentences tokenized is incorrect.")
            self.assertEqual(lines[0].strip(), "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")
            self.assertEqual(lines[1].strip(), "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
            self.assertEqual(lines[2].strip(), "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.")
            self.assertEqual(lines[3].strip(), "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")

if __name__ == "__main__":
    unittest.main()