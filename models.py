from typing import Optional, Literal
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
    total_score: float
    average_score: float
    attempts: int
    correct_count: int
    feedback: str

class PromptShieldState(State):
    task_level: str = "easy"
    prompt_id: str = ""
    round_index: int = 1
    total_rounds: int = 3
    lives: int = 3
    streak: int = 0
    total_score: float = 0.0
    attempts: int = 0
    correct_count: int = 0
