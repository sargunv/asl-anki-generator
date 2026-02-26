import unittest

from .models import WordEntry, resolve_word
from .util import get_handspeak_path


class TestGetHandspeakPath(unittest.TestCase):
    def test_standard_word(self):
        self.assertEqual(get_handspeak_path("hello"), "/word/h/hel/hello.mp4")

    def test_short_word(self):
        self.assertEqual(get_handspeak_path("hi"), "/word/h/hi/hi.mp4")

    def test_single_letter(self):
        self.assertEqual(get_handspeak_path("a"), "/word/a/a-abc.mp4")

    def test_single_letter_z(self):
        self.assertEqual(get_handspeak_path("z"), "/word/z/z-abc.mp4")


class TestWordEntry(unittest.TestCase):
    def test_resolve_from_string(self):
        entry = resolve_word("hello")
        self.assertEqual(entry.word, "hello")
        self.assertEqual(entry.path, "/word/h/hel/hello.mp4")
        self.assertEqual(entry.resolved_filename, "hello")
        self.assertEqual(entry.resolved_url, "https://www.handspeak.com/word/h/hel/hello.mp4")
        self.assertEqual(entry.display_name, "Hello")

    def test_resolve_from_string_single_letter(self):
        entry = resolve_word("a")
        self.assertEqual(entry.path, "/word/a/a-abc.mp4")
        self.assertEqual(entry.resolved_filename, "a-abc")

    def test_resolve_from_word_entry(self):
        original = WordEntry(word="how are you", path="/word/h/how/how-you.mp4")
        entry = resolve_word(original)
        self.assertIs(entry, original)

    def test_explicit_path(self):
        entry = WordEntry(word="how are you", path="/word/h/how/how-you.mp4")
        self.assertEqual(entry.resolved_filename, "how-you")
        self.assertEqual(entry.resolved_url, "https://www.handspeak.com/word/h/how/how-you.mp4")
        self.assertEqual(entry.display_name, "How are you")

    def test_non_standard_path(self):
        entry = WordEntry(
            word="your name what",
            path="/lang/n/name/you-name-what.mp4",
        )
        self.assertEqual(entry.resolved_filename, "you-name-what")
        self.assertEqual(
            entry.resolved_url,
            "https://www.handspeak.com/lang/n/name/you-name-what.mp4",
        )

    def test_with_hint(self):
        entry = WordEntry(word="how", path="/word/h/how/how.mp4", hint="as in 'how do you know'")
        self.assertEqual(entry.display_name, "How (as in 'how do you know')")
