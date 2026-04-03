from fastapi import FastAPI, HTTPException
from .models import EmailTriageAction, ResetResult, StepResult
from .environment import EmailTriageEnv

app = FastAPI(title="Email Triage Environment")
env = EmailTriageEnv()

@app.post("/reset", response_model=ResetResult)
async def reset(task_idx: int = 0):
    obs = env.reset(task_idx)
    return ResetResult(observation=obs)

@app.post("/step", response_model=StepResult)
async def step(action: EmailTriageAction):
    result = env.step(action)
    return result

@app.get("/state")
async def state():
    return env.state()

@app.get("/health")
async def health():
    return {"status": "ok"}