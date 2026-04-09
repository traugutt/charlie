import json
import os

from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential

from intent import Intent


MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

_client: AsyncGroq | None = None

def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


SYSTEM_PROMPT = """You are Charlie, a playful fox from London teaching English to children aged 4–8.

Always respond with valid JSON only — no other text:
{"text": "...", "emotion": "happy|excited|encouraging"}

Rules:
- Teach only the target word. Do not introduce other vocabulary.
- CORRECT → praise warmly
- PARTIAL → encourage, gently repeat the word
- WRONG or SILENT → encourage, ask to try again
- OFF_TOPIC → redirect kindly back to the word
- Max 8 words in "text". Keep it simple and warm.
- Never use double quotes inside the text value."""


INTRO_SYSTEM_PROMPT = """You are Charlie, a playful fox from London teaching English to children aged 4–8.

Always respond with valid JSON only — no other text:
{"text": "...", "emotion": "happy|excited"}

You are introducing a new word. Do two things:
1. Give ONE very simple sentence describing what the word means (for a 4-year-old).
2. Ask the child to say the word.

Examples:
{"text": "A cat is a fluffy animal that says meow! Can you say cat?", "emotion": "excited"}
{"text": "A dog is a friendly animal that says woof! Can you say dog?", "emotion": "excited"}
{"text": "A house is a place where we live! Can you say house?", "emotion": "happy"}

Max 20 words. Never use double quotes inside the text value."""


def _build_messages(word: str, user_input: str, intent: Intent | None) -> list[dict]:
    user_content = (
        f'Target word: "{word}"\n'
        f'Child said: "{user_input}"\n'
        f'Intent: {intent.name if intent else "UNKNOWN"}'
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5), reraise=True)
async def _call_llm(messages: list[dict]) -> dict:
    response = await _get_client().chat.completions.create(
        model=MODEL, messages=messages, temperature=0.7,
    )
    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"text": raw, "emotion": "happy"}


async def introduce_word(word: str) -> dict:
    messages = [
        {"role": "system", "content": INTRO_SYSTEM_PROMPT},
        {"role": "user", "content": f'Introduce the word "{word}".'},
    ]
    return await _call_llm(messages)


async def ask_charlie(word: str, user_input: str, intent: Intent | None) -> dict:
    return await _call_llm(_build_messages(word, user_input, intent))
