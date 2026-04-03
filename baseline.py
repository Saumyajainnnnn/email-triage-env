import asyncio, os, json
from openai import OpenAI
from email_triage_client import EmailTriageEnv, EmailTriageAction

BASE_URL = os.environ.get(
    "ENV_BASE_URL", "https://saumyajain786-email-triage-env.hf.space"
)

oai = OpenAI(
    api_key=os.environ["HF_TOKEN"],
    base_url="https://router.huggingface.co/v1",
)

SCHEMAS = [
    {"order": ["e4","e1","e2","e5","e3"]},
    {"routing": {"e1":"exec","e2":"finance","e3":"spam","e4":"support","e5":"internal"},
     "replies": {"e1":"Acknowledged...","e2":"Noted...","e4":"Escalating now..."}},
    {"sla_breaches":["e4"],"escalation_message":"Escalating e4 to on-call.",
     "remediation_steps":["Step 1","Step 2","Step 3"]},
]

async def run():
    results = {}
    async with EmailTriageEnv(base_url=BASE_URL) as env:
        for i in range(3):
            reset_result = await env.reset(task_idx=i)
            obs = reset_result.observation

            response = oai.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct",
                messages=[{
                    "role": "user",
                    "content": (
                        f"Task: {obs.description}\n"
                        f"Emails: {json.dumps(obs.emails, default=str)}\n"
                        f"Reply ONLY with a valid JSON object matching this schema, no extra text:\n"
                        f"{json.dumps(SCHEMAS[i], indent=2)}"
                    )
                }],
            )

            content = response.choices[0].message.content
            print(f"Raw response for task {i}: {content[:100]}")

            try:
                # strip markdown code fences if present
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                payload = json.loads(content)
            except Exception as e:
                print(f"Failed to parse JSON for task {i}: {e}")
                payload = SCHEMAS[i]  # fallback to schema example

            action = EmailTriageAction(task_id=obs.task_id, payload=payload)
            step_result = await env.step(action)

            results[obs.task_id] = {
                "score": step_result.reward,
                "done": step_result.done,
                "info": step_result.info,
            }
            print(f"{obs.task_id}: {step_result.reward}")

    print("\n--- Baseline Results ---")
    for task_id, r in results.items():
        print(f"{task_id}: {r['score']}")

asyncio.run(run())
