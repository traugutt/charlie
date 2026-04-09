import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, AsyncMock
from lesson import LessonController, Stage


MOCK_RESPONSE = {"text": "Say cat!", "emotion": "happy"}
MOCK_INTRO = {"text": "A dog is a friendly animal! Can you say dog?", "emotion": "excited"}


@pytest.fixture
def controller():
    return LessonController(["cat", "dog", "bird"])


@pytest.mark.asyncio
async def test_greeting_transitions_to_practice(controller):
    with patch("lesson.introduce_word", new=AsyncMock(return_value=MOCK_INTRO)):
        await controller.handle("hi")
    assert controller.stage == Stage.PRACTICE


@pytest.mark.asyncio
async def test_correct_answer_advances_and_introduces_next(controller):
    controller.stage = Stage.PRACTICE
    with patch("lesson.introduce_word", new=AsyncMock(return_value=MOCK_INTRO)):
        response = await controller.handle("cat")
    assert controller.index == 1
    assert "dog" in response["text"]


@pytest.mark.asyncio
async def test_wrong_answer_does_not_advance(controller):
    controller.stage = Stage.PRACTICE
    with patch("lesson.ask_charlie", new=AsyncMock(return_value=MOCK_RESPONSE)):
        await controller.handle("xyz")
    assert controller.index == 0


@pytest.mark.asyncio
async def test_all_words_complete_sets_done(controller):
    controller.stage = Stage.PRACTICE
    controller.index = 2  # last word is "bird"
    response = await controller.handle("bird")
    assert controller.stage == Stage.DONE
    assert response["emotion"] == "excited"
