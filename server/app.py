from pathlib import Path

import uvicorn
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openenv.core.env_server import create_fastapi_app

from models import PromptShieldAction, PromptShieldObservation
from server.environment import PromptShieldEnvironment

app = create_fastapi_app(
    PromptShieldEnvironment,
    PromptShieldAction,
    PromptShieldObservation,
)

# Local UI game session (keeps state for the website)
_game_env = PromptShieldEnvironment()

@app.post("/game/reset")
def game_reset(payload: dict):
    return _game_env.reset(**payload)

@app.post("/game/step")
def game_step(payload: dict):
    action = PromptShieldAction(**payload)
    result = _game_env.step(action)
    if result.done and result.lives == 0:
        reset_obs = _game_env.reset(task_level=result.task_level, total_rounds=result.total_rounds, lives=3)
        feedback = result.feedback or ""
        if feedback:
            feedback = feedback.rstrip() + " "
        feedback += "Game over. New round started."
        return PromptShieldObservation(**reset_obs.model_dump(), feedback=feedback)
    return result

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
