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

# Charlie's character is defined once in the system prompt.
# The user turn only supplies factual context: which word, what the child said, and the intent.
# Keeping them separate means the character stays consistent regardless of what the child does.
SYSTEM_PROMPT = """You are Charlie, a playful 8-year-old fox from London teaching English to children aged 4–8.

Always respond with valid JSON only — no other text:
{"text": "...", "emotion": "happy|excited|encouraging"}

Rules:
- Teach only the target word. Do not introduce other vocabulary.
- CORRECT → praise warmly
- PARTIAL → encourage, gently repeat the word
- WRONG or SILENT → encourage, ask to try again
- OFF_TOPIC → redirect kindly back to the word
- Max 8 words in "text". Keep it simple and warm."""


def _build_messages(word: str, user_input: str, intent: Intent | None) -> list[dict]:
    if not user_input:
        user_content = f'Introduce the word "{word}" in a fun way and ask the child to say it.'
    else:
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
async def _create_stream(messages: list[dict]):
    return await _get_client().chat.completions.create(
        model=MODEL, messages=messages, stream=True, temperature=0.7,
    )


async def ask_charlie(word: str, user_input: str, intent: Intent | None) -> dict:
    messages = _build_messages(word, user_input, intent)
    stream = await _create_stream(messages)

    chunks = []
    async for chunk in stream:
        try:
            content = chunk.choices[0].delta.content
            if content:
                chunks.append(content)
        except (AttributeError, IndexError):
            continue

    raw = "".join(chunks).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"text": raw, "emotion": "happy"}
