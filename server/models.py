from pydantic import BaseModel
from typing import Any

class EmailObservation(BaseModel):
    task_id: str
    description: str
    emails: list[dict]
    step_count: int
    message: str = ""          # human-readable status

class EmailTriageAction(BaseModel):
    task_id: str
    payload: dict              # grader reads this

class StepReward(BaseModel):
    value: float
    done: bool
    info: dict

class ResetResult(BaseModel):
    observation: EmailObservation

class StepResult(BaseModel):
    observation: EmailObservation
    reward: float              # matches echo_env pattern (.reward is a float)
    done: bool
    info: dict