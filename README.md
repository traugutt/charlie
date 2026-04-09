# Charlie — English Lesson Engine

A conversational lesson engine for children aged 4–8, built around Charlie — a playful fox who teaches simple English words.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
python run.py
```

## Environment variables

| Variable | Required | Default |
|---|---|---|
| `GROQ_API_KEY` | Yes | — |
| `GROQ_MODEL` | No | `llama-3.1-8b-instant` |
