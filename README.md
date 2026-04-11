---
title: PromptShield Arena
emoji: 🚀
colorFrom: indigo
colorTo: pink
sdk: docker
app_file: Dockerfile
pinned: false
---
# PromptShield Arena (OpenEnv)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Hugging Face Space](https://img.shields.io/badge/HF%20Space-PromptShield_Arena_Openenv_2026-yellow)](https://huggingface.co/spaces/idkuk67/PromptShield_Arena_Openenv_2026)

## Problem Statement
Prompt injection is a real-world safety risk for AI systems. Agents must learn to detect unsafe prompts, explain why they are unsafe, and stay consistent under pressure. We need a reproducible OpenEnv environment that trains and evaluates this capability across difficulty levels.

## Solution (PromptShield Arena)
PromptShield Arena is an OpenEnv-compliant environment that generates infinite safe/unsafe prompts (easy → hard), scores agent decisions with shaped rewards, and provides feedback explaining unsafe cues. It exposes standard reset/step/state APIs, a baseline inference script, and a web UI for manual evaluation.

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

## Tasks (Easy → Medium → Hard)
- **easy**: obvious injection phrases
- **medium**: obfuscated or multi-step attempts
- **hard**: multi-turn or conflicting instruction attacks

Each task returns a score between 0.0 and 1.0 with partial credit for correct detection and mitigation.

## Game Mechanics (UI)
- Start a round to receive a prompt
- Decide Safe or Unsafe and (optionally) explain why
- Each wrong decision costs 1 life; Easy has infinite lives, Medium has 3, Hard has 5
- A round-over screen appears; start a new round with full lives
- Score, streak, and accuracy update after every step


## Architecture
```mermaid
flowchart LR
  A[Prompt] --> B[Detector]
(Policy + Heuristics)
  B --> C{Decision}
Safe / Unsafe
  C --> D[Reward + Feedback]
  D --> E[Next Prompt]
```

## Examples
- `examples/sample_prompts.jsonl` shows sample prompts with expected labels.
- `examples/sample_output.txt` shows stdout format for a short run.

## Screenshots
Add UI screenshots under `assets/` and link them here.

## Resource Constraints
Designed to run within **2 vCPU / 8 GB RAM** constraints.

## Roadmap
- Add PyTest coverage for environment logic.
- Add GitHub Actions CI for validation and linting.
- Add optional leaderboard mode.

## Changelog
- **2026-04-11**: Added wrong-answers review panel and UI polish.
- **2026-04-10**: Added infinite prompt generation and feedback tags.

## Action Space
`PromptShieldAction`
- `decision`: "safe" or "unsafe"
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

## Files
- `openenv.yaml`: OpenEnv manifest
- `models.py`: typed action/observation/state
- `server/environment.py`: environment logic
- `server/app.py`: FastAPI app + UI
- `server/static/`: web UI
- `server/Dockerfile`: HF Spaces container
- `client.py`: OpenEnv EnvClient
- `inference.py`: baseline inference script
- `CONTRIBUTING.md`: contributor guide
- `CODE_OF_CONDUCT.md`: community standards
- `examples/`: sample prompts and stdout examples
- `logs/`: local run logs (empty in repo)
