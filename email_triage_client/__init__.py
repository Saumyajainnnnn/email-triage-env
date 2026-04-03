import httpx
from pydantic import BaseModel
from typing import Any

class EmailTriageAction(BaseModel):
    task_id: str
    payload: dict

class EmailObservation(BaseModel):
    task_id: str
    description: str
    emails: list[dict]
    step_count: int
    message: str = ""

class ResetResult(BaseModel):
    observation: EmailObservation

class StepResult(BaseModel):
    observation: EmailObservation
    reward: float
    done: bool
    info: dict

class _SyncWrapper:
    def __init__(self, env: "EmailTriageEnv"):
        self._env = env
        self._client = httpx.Client(base_url=env._base_url, timeout=30)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    def reset(self, task_idx: int = 0) -> ResetResult:
        r = self._client.post("/reset", params={"task_idx": task_idx})
        r.raise_for_status()
        return ResetResult(**r.json())

    def step(self, action: EmailTriageAction) -> StepResult:
        r = self._client.post("/step", json=action.model_dump())
        r.raise_for_status()
        return StepResult(**r.json())

    def state(self) -> dict:
        r = self._client.get("/state")
        r.raise_for_status()
        return r.json()


class EmailTriageEnv:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def reset(self, task_idx: int = 0) -> ResetResult:
        r = await self._client.post("/reset", params={"task_idx": task_idx})
        r.raise_for_status()
        return ResetResult(**r.json())

    async def step(self, action: EmailTriageAction) -> StepResult:
        r = await self._client.post("/step", json=action.model_dump())
        r.raise_for_status()
        return StepResult(**r.json())

    async def state(self) -> dict:
        r = await self._client.get("/state")
        r.raise_for_status()
        return r.json()

    def sync(self) -> _SyncWrapper:
        return _SyncWrapper(self)