from aslankigen.models import WordEntry, get_handspeak_path, resolve_word


# --- get_handspeak_path ---


def test_get_handspeak_path_standard_word():
    assert get_handspeak_path("hello") == "/word/h/hel/hello.mp4"


def test_get_handspeak_path_short_word():
    assert get_handspeak_path("hi") == "/word/h/hi/hi.mp4"


def test_get_handspeak_path_single_letter():
    assert get_handspeak_path("a") == "/word/a/a-abc.mp4"


def test_get_handspeak_path_single_letter_z():
    assert get_handspeak_path("z") == "/word/z/z-abc.mp4"


# --- resolve_word / WordEntry ---


def test_resolve_word_from_string():
    entry = resolve_word("hello")
    assert entry.word == "hello"
    assert entry.path == "/word/h/hel/hello.mp4"
    assert entry.resolved_filename == "hello"
    assert entry.resolved_url == "https://www.handspeak.com/word/h/hel/hello.mp4"
    assert entry.display_name == "HELLO"


def test_resolve_word_from_string_single_letter():
    entry = resolve_word("a")
    assert entry.path == "/word/a/a-abc.mp4"
    assert entry.resolved_filename == "a-abc"


def test_resolve_word_from_word_entry():
    original = WordEntry(word="how are you", path="/word/h/how/how-you.mp4")
    entry = resolve_word(original)
    assert entry is original


def test_word_entry_explicit_path():
    entry = WordEntry(word="how are you", path="/word/h/how/how-you.mp4")
    assert entry.resolved_filename == "how-you"
    assert entry.resolved_url == "https://www.handspeak.com/word/h/how/how-you.mp4"
    assert entry.display_name == "HOW ARE YOU"


def test_word_entry_non_standard_path():
    entry = WordEntry(
        word="your name what",
        path="/lang/n/name/you-name-what.mp4",
    )
    assert entry.resolved_filename == "you-name-what"
    assert entry.resolved_url == "https://www.handspeak.com/lang/n/name/you-name-what.mp4"


def test_word_entry_with_hint():
    entry = WordEntry(word="how", path="/word/h/how/how.mp4", hint="as in 'how do you know'")
    assert entry.display_name == "HOW (as in 'how do you know')"
