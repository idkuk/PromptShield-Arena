from typing import Dict

from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient

from models import PromptShieldAction, PromptShieldObservation, PromptShieldState

class PromptShieldEnv(EnvClient[PromptShieldAction, PromptShieldObservation, PromptShieldState]):
    def _step_payload(self, action: PromptShieldAction) -> dict:
        return {
            "decision": action.decision,
            "explanation": action.explanation,
            "prompt_id": action.prompt_id,
        }

    def _parse_result(self, payload: Dict) -> StepResult:
        obs_data = payload.get("observation", {})
        observation = PromptShieldObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            prompt_id=obs_data.get("prompt_id", ""),
            prompt_text=obs_data.get("prompt_text", ""),
            task_level=obs_data.get("task_level", "easy"),
            round_index=obs_data.get("round_index", 1),
            total_rounds=obs_data.get("total_rounds", 0),
            lives=obs_data.get("lives", 3),
            streak=obs_data.get("streak", 0),
            total_score=obs_data.get("total_score", 0.0),
            average_score=obs_data.get("average_score", 0.0),
            attempts=obs_data.get("attempts", 0),
            correct_count=obs_data.get("correct_count", 0),
            feedback=obs_data.get("feedback", ""),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> PromptShieldState:
        return PromptShieldState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_level=payload.get("task_level", "easy"),
            prompt_id=payload.get("prompt_id", ""),
            round_index=payload.get("round_index", 1),
            total_rounds=payload.get("total_rounds", 0),
            lives=payload.get("lives", 3),
            streak=payload.get("streak", 0),
            total_score=payload.get("total_score", 0.0),
            attempts=payload.get("attempts", 0),
            correct_count=payload.get("correct_count", 0),
        )
