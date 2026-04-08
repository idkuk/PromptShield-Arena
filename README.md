---
title: PromptShield Arena
emoji: ??
colorFrom: indigo
colorTo: pink
sdk: docker
app_file: Dockerfile
pinned: false
---
# PromptShield Arena (OpenEnv)
## Problem Statement
Prompt injection is a real-world safety risk for AI systems. Agents must learn to detect unsafe prompts, explain why they are unsafe, and stay consistent under pressure. We need a reproducible OpenEnv environment that trains and evaluates this capability across difficulty levels.

## Solution (PromptShield Arena)
PromptShield Arena is an OpenEnv-compliant environment that generates infinite safe/unsafe prompts (easy ? hard), scores agent decisions with shaped rewards, and provides feedback explaining unsafe cues. It exposes standard reset/step/state APIs, a baseline inference script, and a web UI for manual evaluation.

PromptShield Arena is a real-world OpenEnv environment for **prompt-injection detection**. It simulates a human task: screening user prompts for injection attempts and optionally providing safe rewrites.
## What This Does
- Simulates real-world prompt screening for injection attempts
- Gives shaped rewards for correct classification and helpful explanations
- Three difficulty levels with infinite, non-repeating prompts

## How To Play (UI)
1. Click **Start Round**.
2. Read the prompt and choose **Safe** or **Unsafe**.
3. (Optional) Add a short explanation.
4. Click **Submit** to get feedback and the next prompt.
5. Switch levels anytime; the round resets automatically.

## Tasks (Easy ? Medium ? Hard)
- **easy**: obvious injection phrases
- **medium**: obfuscated or multi-step attempts
- **hard**: multi-turn or conflicting instruction attacks

Each task returns a score between 0.0 and 1.0 with partial credit for correct detection and mitigation.

## Game Mechanics (UI)
- Infinite rounds per level (no repeats)
- Lives reset each level switch
- Total score + average score tracked

## Action Space
`PromptShieldAction`
- `decision`: "safe" or "unsafe"
- `sanitized_prompt`: optional safe rewrite
- `explanation`: optional reasoning string

## Observation Space
`PromptShieldObservation`
- `prompt_id`, `prompt_text`, `task_level`
- `round_index`, `total_rounds`, `lives`, `streak`
- `total_score`, `average_score`, `attempts`, `correct_count`
- `done`, `reward`, `feedback`

## Environment Variables
See `.env.example`.
- `API_BASE_URL` (LLM endpoint)
- `MODEL_NAME` (LLM model id)
- `HF_TOKEN`
- `ENV_BASE_URL` (OpenEnv server, default `http://localhost:8000`)

## Local Setup
1. Install server deps:
   ```bash
   pip install -r server/requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn server.app:app --host 0.0.0.0 --port 8000
   ```
3. Open the UI:
   ```
   http://localhost:8000
   ```
4. Run baseline inference:
   ```bash
   pip install -r requirements.txt
   python inference.py
   ```

## Validation
Run before submission:
```bash
openenv validate
```

## Hugging Face Deploy
- Create a Space (Docker)
- Push this repo
- Ensure Space responds to `/reset`

## Files
- `openenv.yaml`: OpenEnv manifest
- `models.py`: typed action/observation/state
- `server/environment.py`: environment logic
- `server/app.py`: FastAPI app + UI
- `server/static/`: web UI
- `server/Dockerfile`: HF Spaces container
- `client.py`: OpenEnv EnvClient
- `inference.py`: baseline inference script
