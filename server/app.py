from pathlib import Path

import uvicorn
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from openenv.core.env_server import create_fastapi_app

from models import PromptShieldAction, PromptShieldObservation
from server.environment import PromptShieldEnvironment

app = create_fastapi_app(
    PromptShieldEnvironment,
    PromptShieldAction,
    PromptShieldObservation,
)


def _sanitize_score_examples(obj, path: str = "") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_path = f"{path}.{key}" if path else key
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                haystack = f"{key} {next_path}".lower()
                if "score" in haystack or "reward" in haystack:
                    if value <= 0:
                        obj[key] = 0.1
                    elif value >= 1:
                        obj[key] = 0.9
            _sanitize_score_examples(value, next_path)
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            _sanitize_score_examples(value, f"{path}[{idx}]")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    _sanitize_score_examples(openapi_schema)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

LEVEL_LIVES = {
    "easy": 999999,  # treat as infinite in UI
    "medium": 3,
    "hard": 5,
}

# Local UI game sessions (one per level)
_game_envs = {
    "easy": PromptShieldEnvironment(),
    "medium": PromptShieldEnvironment(),
    "hard": PromptShieldEnvironment(),
}

def _get_env(level: str) -> PromptShieldEnvironment:
    return _game_envs.get(level, _game_envs["easy"])

@app.post("/game/reset")
def game_reset(payload: dict):
    level = (payload.get("task_level") or "easy").lower()
    env = _get_env(level)
    lives = payload.get("lives")
    if lives is None:
        lives = LEVEL_LIVES.get(level, 3)
    payload["lives"] = lives
    payload["task_level"] = level
    return env.reset(**payload)

@app.post("/game/step")
def game_step(payload: dict):
    try:
        level = (payload.get("task_level") or "easy").lower()
        payload = dict(payload)
        payload.pop("task_level", None)
        env = _get_env(level)
        action = PromptShieldAction(**payload)
        return env.step(action)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/game/state")
def game_state(payload: dict):
    level = (payload.get("task_level") or "easy").lower()
    env = _get_env(level)
    obs = env.snapshot()
    if not obs.prompt_text:
        lives = LEVEL_LIVES.get(level, 3)
        return env.reset(task_level=level, total_rounds=payload.get("total_rounds", 0), lives=lives)
    return obs

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    return FileResponse(static_dir / "index.html")

@app.get("/favicon.ico")
def favicon():
    return FileResponse(static_dir / "favicon.ico")


def main() -> None:
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
