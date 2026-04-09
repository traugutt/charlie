# Charlie — English Lesson Engine

Charlie is a playful animated fox who teaches English words to children aged 4–8.  
This is a Python prototype of the lesson engine — text only, no voice required.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
python run.py
```

## How it works

### 1. Lesson flow — who manages it

All lesson state lives in one place: `LessonController` in `lesson.py`.  
It moves through three stages in order:

```
GREETING → PRACTICE (one word at a time) → DONE
```

The controller is the only thing that decides when to advance to the next word,
when to repeat, and when the lesson is over. `run.py` just loops and prints —
it has no knowledge of the lesson logic.

Each child turn follows the same three steps:

1. classify the input → `Intent`
2. decide what happens next (advance / repeat / redirect)
3. return a response (hardcoded for transitions, LLM for practice)

---

### 2. LLM interaction — prompts and character control

Charlie's personality is defined once in the **system prompt** (`llm.py`):

```
You are Charlie, a playful 8-year-old fox from London teaching English to children aged 4–8.
Max 8 words. Always respond with valid JSON: {"text": "...", "emotion": "..."}
```

The **user turn** only supplies factual context — which word is being taught,
what the child said, and the detected intent:

```
Target word: "cat"
Child said: "ga"
Intent: PARTIAL
```

Keeping character and context separate means the personality stays consistent
no matter what the child does. The LLM never needs to figure out whether
something is a correct answer — `analyze_intent()` does that first, and the
LLM just receives a labelled situation to respond to.

Responses are streamed with a 3-retry fallback. The system prompt requires JSON
output; any response that fails to parse falls back to plain text.

---

### 3. Real child interactions — not edge cases

Children will be silent, say random things, or answer halfway. These are
the normal case, not exceptions. Every input is classified before the LLM sees it:

| What the child does | Intent | Charlie does |
|---|---|---|
| Says the word correctly | `CORRECT` | Praise + introduce next word |
| Says part of the word (2+ chars match) | `PARTIAL` | Encourage, repeat the word |
| Says something short and wrong | `WRONG` | Ask to try again |
| Says 5+ unrelated words | `OFF_TOPIC` | Redirect back to the word |
| Says nothing | `SILENT` | Encourage gently |

Classification happens in `intent.py` using simple string rules — no LLM call
needed. This makes responses fast, predictable, and easy to test.

One specific case worth noting: when the child answers correctly, the
word transition is **hardcoded**, not LLM-generated. The LLM proved unreliable
when asked to praise *and* introduce the next word in a single response —
it would drop one of the two parts. The solution was to own that step in code
and only use the LLM where its flexibility actually helps.

---

## Project structure

```
run.py       entry point and print loop
lesson.py    lesson state + flow controller
llm.py       Groq client, system prompt, streaming
intent.py    input classification (CORRECT / PARTIAL / WRONG / OFF_TOPIC / SILENT)
tests/
  test_intent.py   unit tests for input classification
  test_lesson.py   flow tests (LLM mocked)
```

## Environment variables

| Variable | Required | Default |
|---|---|---|
| `GROQ_API_KEY` | Yes | — |
| `GROQ_MODEL` | No | `llama-3.1-8b-instant` |
