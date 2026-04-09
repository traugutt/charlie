import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from intent import analyze_intent, Intent


def test_correct():
    assert analyze_intent("cat", "cat") == Intent.CORRECT

def test_correct_within_sentence():
    assert analyze_intent(" cat ", "cat") == Intent.CORRECT

def test_silence():
    assert analyze_intent("", "cat") == Intent.SILENT

def test_silence_whitespace():
    assert analyze_intent("   ", "cat") == Intent.SILENT

def test_partial_two_chars():
    assert analyze_intent("ca", "cat") == Intent.PARTIAL

def test_single_char_is_not_partial():
    assert analyze_intent("a", "cat") != Intent.PARTIAL

def test_wrong():
    assert analyze_intent("hello", "cat") == Intent.WRONG

def test_off_topic():
    assert analyze_intent("I want to go to the park", "cat") == Intent.OFF_TOPIC
