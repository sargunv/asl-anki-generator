import unittest

from .util import get_handspeak_url


class TestGetHandspeakUrl(unittest.TestCase):
    def test_get_handspeak_url(self):
        actual = get_handspeak_url("hello")
        expected = "https://www.handspeak.com/word/h/hel/hello.mp4"
        self.assertEqual(actual, expected)

    def test_get_handspeak_url_short_word(self):
        actual = get_handspeak_url("hi")
        expected = "https://www.handspeak.com/word/h/hi/hi.mp4"
        self.assertEqual(actual, expected)

    def test_get_handspeak_url_single_letter(self):
        actual = get_handspeak_url("a")
        expected = "https://www.handspeak.com/word/a/a-abc.mp4"
        self.assertEqual(actual, expected)

    def test_get_handspeak_url_single_letter_z(self):
        actual = get_handspeak_url("z")
        expected = "https://www.handspeak.com/word/z/z-abc.mp4"
        self.assertEqual(actual, expected)
