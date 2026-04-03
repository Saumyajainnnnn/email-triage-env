---
title: Email Triage Environment
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Email Triage Environment

An OpenEnv-compatible environment that simulates a real corporate email inbox.
An AI agent must triage, route, and respond to emails under time pressure and SLA constraints.

## Environment Description

The agent receives a set of emails and must complete one of three tasks:
- **Easy**: Sort emails by urgency
- **Medium**: Route emails to departments + draft replies
- **Hard**: Detect SLA breaches and escalate with remediation steps

## Action Space
```json
{
  "task_id": "task_sort",
  "payload": {}
}
```

## Observation Space
```json
{
  "task_id": "task_sort",
  "description": "...",
  "emails": [],
  "step_count": 0,
  "message": ""
}
```

## Setup
```bash
pip install -r requirements.txt
pip install -e email_triage_client/
```

## Usage
```python
import asyncio
from email_triage_client import EmailTriageEnv, EmailTriageAction

async def main():
    async with EmailTriageEnv(
        base_url="https://saumyajain786-email-triage-env.hf.space"
    ) as env:
        result = await env.reset(task_idx=0)
        print(result.observation.message)

asyncio.run(main())
```

## Baseline
```bash
export OPENAI_API_KEY=your_key
python baseline.py
```

## Tasks

| Task | Difficulty | Description |
|------|-----------|-------------|
| task_sort | Easy | Sort 5 emails by urgency |
| task_route_reply | Medium | Route to departments + draft replies |
| task_sla_escalate | Hard | Detect SLA breach + escalate |