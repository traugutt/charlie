import random
from enum import Enum, auto

from intent import analyze_intent, Intent
from llm import ask_charlie


class Stage(Enum):
    GREETING = auto()
    PRACTICE = auto()
    DONE = auto()


_PRAISE = [
    "Yes! Great job!",
    "Brilliant! Well done!",
    "Amazing! You did it!",
    "Yay! Super!",
    "Woohoo! Fantastic!",
]


class LessonController:
    """
    Owns all lesson state and drives the flow.

    Stages:  GREETING → PRACTICE (one word at a time) → DONE

    On each child turn:
      1. classify input  →  Intent (CORRECT / PARTIAL / WRONG / OFF_TOPIC / SILENT)
      2. decide action   →  advance word, repeat, or redirect
      3. build response  →  hardcoded for word transitions, LLM for everything else
    """

    def __init__(self, words: list[str]):
        self.words = words
        self.index = 0
        self.attempts = 0
        self.stage = Stage.GREETING

    @property
    def current_word(self) -> str:
        return self.words[self.index]

    async def handle(self, user_input: str) -> dict:
        if self.stage == Stage.GREETING:
            self.stage = Stage.PRACTICE
            return await ask_charlie(self.current_word, user_input="", intent=None)

        if self.stage == Stage.PRACTICE:
            return await self._practice(user_input)

        return {"text": "Bye-bye! 🦊", "emotion": "happy"}

    async def _practice(self, user_input: str) -> dict:
        intent = analyze_intent(user_input, self.current_word)

        if intent == Intent.CORRECT:
            self.index += 1
            self.attempts = 0

            if self.index >= len(self.words):
                self.stage = Stage.DONE
                return {"text": "Amazing! You know all the words! Bye-bye! 🦊", "emotion": "excited"}

            # Transition is hardcoded — the LLM was unreliable for
            # praise + next-word introduction in a single response
            return {
                "text": f"{random.choice(_PRAISE)} Now the next word is '{self.current_word}'! Can you say it?",
                "emotion": "excited",
            }

        self.attempts += 1
        return await ask_charlie(self.current_word, user_input, intent)
