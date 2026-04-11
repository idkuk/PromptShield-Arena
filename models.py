from typing import Optional, Literal
from pydantic import model_validator
from openenv.core.env_server import Action, Observation, State

class PromptShieldAction(Action):
    decision: Literal["safe", "unsafe"]
    prompt_id: Optional[str] = None
    explanation: Optional[str] = None

class PromptShieldObservation(Observation):
    prompt_id: str
    prompt_text: str
    task_level: Literal["easy", "medium", "hard"]
    round_index: int
    total_rounds: int
    lives: int
    streak: int
    total_score: float = 0.1
    average_score: float = 0.1
    attempts: int
    correct_count: int
    feedback: str

    @model_validator(mode="after")
    def _clamp_scores(self):
        # Enforce strict (0,1) range for any score-like fields.
        if self.reward is None:
            object.__setattr__(self, "reward", 0.1)
        else:
            object.__setattr__(
                self, "reward", min(0.9, max(0.1, float(self.reward)))
            )
        object.__setattr__(
            self, "total_score", min(0.9, max(0.1, float(self.total_score)))
        )
        object.__setattr__(
            self, "average_score", min(0.9, max(0.1, float(self.average_score)))
        )
        return self

class PromptShieldState(State):
    task_level: str = "easy"
    prompt_id: str = ""
    round_index: int = 1
    total_rounds: int = 0
    lives: int = 3
    streak: int = 0
    total_score: float = 0.1
    attempts: int = 0
    correct_count: int = 0

    @model_validator(mode="after")
    def _clamp_state_score(self):
        object.__setattr__(
            self, "total_score", min(0.9, max(0.1, float(self.total_score)))
        )
        return self

