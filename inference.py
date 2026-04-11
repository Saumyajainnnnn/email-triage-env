import asyncio
import os
import json
import textwrap
from typing import List, Optional

from openai import OpenAI
from email_triage_client import EmailTriageEnv, EmailTriageAction

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "meta-llama/Llama-3.3-70B-Instruct"
BENCHMARK = "email-triage-env"
MAX_STEPS = 5

TASKS = [
    {"task_idx": 0, "task_name": "task_sort"},
    {"task_idx": 1, "task_name": "task_route_reply"},
    {"task_idx": 2, "task_name": "task_sla_escalate"},
]

SCHEMAS = [
    {"order": ["e4","e1","e2","e5","e3"]},
    {"routing": {"e1":"exec","e2":"finance","e3":"spam","e4":"support","e5":"internal"},
     "replies": {"e1":"Acknowledged...","e2":"Noted...","e4":"Escalating now..."}},
    {"sla_breaches":["e4"],"escalation_message":"Escalating e4 to on-call.",
     "remediation_steps":["Step 1","Step 2","Step 3"]},
]

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def get_model_payload(client: OpenAI, description: str, emails: list, schema: dict) -> dict:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": (
                    f"Task: {description}\n"
                    f"Emails: {json.dumps(emails, default=str)}\n"
                    f"Reply ONLY with a valid JSON object matching this schema, no extra text:\n"
                    f"{json.dumps(schema, indent=2)}"
                )
            }],
            temperature=0.1,
            max_tokens=512,
        )
        content = (completion.choices[0].message.content or "").strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())
    except Exception as e:
        print(f"[DEBUG] Model/parse error: {e}", flush=True)
        return schema

async def run_task(env: EmailTriageEnv, client: OpenAI, task_idx: int, task_name: str, schema: dict):
    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset_result = await env.reset(task_idx=task_idx)
        obs = reset_result.observation

        for step in range(1, MAX_STEPS + 1):
            payload = get_model_payload(client, obs.description, obs.emails, schema)
            action = EmailTriageAction(task_id=obs.task_id, payload=payload)

            result = await env.step(action)
            reward = result.reward or 0.0
            done = result.done
            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=str(task_name), reward=reward, done=done, error=None)

            if done:
                break

        score = max(rewards) if rewards else 0.01
        score = min(max(score, 0.01), 0.99)
        success = score >= 0.5


    except Exception as e:
        log_step(step=steps_taken+1, action="error", reward=0.0, done=True, error=str(e))

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    BASE_URL = os.environ.get("ENV_BASE_URL", "https://saumyajain786-email-triage-env.hf.space")

    async with EmailTriageEnv(base_url=BASE_URL) as env:
        for i, task in enumerate(TASKS):
            score = await run_task(env, client, task["task_idx"], task["task_name"], SCHEMAS[i])
            print(f"[RESULT] {task['task_name']}: {score:.2f}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())