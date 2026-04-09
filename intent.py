from enum import Enum, auto


class Intent(Enum):
    CORRECT = auto()
    PARTIAL = auto()    # said part of the word (2+ consecutive chars)
    WRONG = auto()      # short wrong answer
    OFF_TOPIC = auto()  # long unrelated response
    SILENT = auto()     # empty input


def analyze_intent(user_input: str, expected_word: str) -> Intent:
    if not user_input.strip():
        return Intent.SILENT

    text = user_input.lower().strip()

    if expected_word == text.strip():
        return Intent.CORRECT

    if any(expected_word[i:i + 2] in text for i in range(len(expected_word) - 1)):
        return Intent.PARTIAL

    if len(text.split()) > 4:
        return Intent.OFF_TOPIC

    return Intent.WRONG
