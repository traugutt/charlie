# Charlie — English Lesson Engine

A conversational lesson engine for children aged 4–8, built around Charlie — a playful fox who teaches simple English words. Text only, no voice.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
python run.py
```

## How it works

### Lesson flow

`LessonController` in `lesson.py` owns the lesson state and drives everything forward:

```
GREETING → PRACTICE (one word at a time) → DONE
```

`run.py` just handles input/output. On each turn the controller classifies what the child said, decides what to do next, and returns a response. That's it.

### Working with the LLM

Charlie's character lives in the system prompt — personality, tone, output format. The user turn only carries the facts: which word, what the child said, what the intent was.

```
Target word: "cat"
Child said: "ga"
Intent: PARTIAL
```

This way the character stays consistent regardless of what the child does. The LLM doesn't decide whether an answer is correct — `analyze_intent()` handles that first, so the LLM just gets a labelled situation to respond to.

Word transitions (praise + next word) are hardcoded rather than LLM-generated — the model was dropping one of the two parts when asked to do both at once.

### Handling real child input

Silence, off-topic replies, and partial answers are the normal case here, not edge cases. Every input gets classified before it reaches the LLM:

| What the child does | Intent | Charlie does |
|---|---|---|
| Says the word | `CORRECT` | Praises, introduces next word |
| Says part of the word | `PARTIAL` | Encourages, repeats the word |
| Short wrong answer | `WRONG` | Asks to try again |
| Goes off topic | `OFF_TOPIC` | Redirects back to the word |
| Says nothing | `SILENT` | Encourages gently |

Classification is simple string matching in `intent.py` — fast, predictable, and easy to test without mocking anything.

## Structure

```
run.py        entry point
lesson.py     lesson state and flow
llm.py        Groq client and prompts
intent.py     input classification
tests/
  test_intent.py
  test_lesson.py
```

## Environment variables

| Variable | Required | Default |
|---|---|---|
| `GROQ_API_KEY` | Yes | — |
| `GROQ_MODEL` | No | `llama-3.1-8b-instant` |
