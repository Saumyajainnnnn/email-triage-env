from .models import EmailObservation, EmailTriageAction, StepResult
from .data import EMAILS
from .graders import grade_sort, grade_route_reply, grade_sla_escalate

TASKS = [
    {
        "id": "task_sort",
        "difficulty": "easy",
        "description": (
            "Sort the 5 emails from most to least urgent. "
            "Return JSON: {\"order\": [\"e4\", \"e1\", \"e2\", \"e5\", \"e3\"]} "
            "using only the email IDs provided."
        ),
        "email_ids": ["e1", "e2", "e3", "e4", "e5"],
        "grader": grade_sort,
    },
    {
        "id": "task_route_reply",
        "difficulty": "medium",
        "description": (
            "For each email assign a department "
            "(exec/finance/support/internal/spam) AND draft a one-sentence "
            "acknowledgement for emails that need a reply. "
            "Return JSON: {\"routing\": {\"e1\": \"exec\", ...}, "
            "\"replies\": {\"e1\": \"...\", ...}}"
        ),
        "email_ids": ["e1", "e2", "e3", "e4", "e5"],
        "grader": grade_route_reply,
    },
    {
        "id": "task_sla_escalate",
        "difficulty": "hard",
        "description": (
            "Identify emails breaching SLA within 2 hours, draft an escalation "
            "message to the on-call engineer, and list 3 remediation steps. "
            "Return JSON: {\"sla_breaches\": [\"e4\"], "
            "\"escalation_message\": \"...\", \"remediation_steps\": [\"...\", \"...\", \"...\"]}"
        ),
        "email_ids": ["e4"],
        "grader": grade_sla_escalate,
    },
]


class EmailTriageEnv:
    def __init__(self):
        self._task_idx = 0
        self._step_count = 0
        self._max_steps = 5

    def reset(self, task_idx: int = 0) -> EmailObservation:
        self._task_idx = max(0, min(task_idx, len(TASKS) - 1))
        self._step_count = 0
        return self._make_obs("Email triage environment ready!")

    def step(self, action: EmailTriageAction) -> StepResult:
        self._step_count += 1
        task = TASKS[self._task_idx]

        if action.task_id != task["id"]:
            raise ValueError(
                f"Action task_id '{action.task_id}' does not match "
                f"current task '{task['id']}'"
            )

        raw_score = task["grader"](action.payload)
        step_penalty = 0.05 * max(0, self._step_count - 1)
        final_score = round(max(0.0, raw_score - step_penalty), 2)
        done = (raw_score >= 0.9) or (self._step_count >= self._max_steps)

        obs = self._make_obs(
            f"Step {self._step_count} complete. "
            f"Score: {final_score}. Done: {done}."
        )
        return StepResult(
            observation=obs,
            reward=final_score,
            done=done,
            info={
                "raw_score": raw_score,
                "step_penalty": step_penalty,
                "steps_used": self._step_count,
            },
        )

    def state(self) -> dict:
        return {
            "task_idx": self._task_idx,
            "current_task": TASKS[self._task_idx]["id"],
            "step_count": self._step_count,
            "max_steps": self._max_steps,
        }

    def _make_obs(self, message: str) -> EmailObservation:
        task = TASKS[self._task_idx]
        emails = [
            {k: v for k, v in e.items()}
            for e in EMAILS
            if e["id"] in task["email_ids"]
        ]
        return EmailObservation(
            task_id=task["id"],
            description=task["description"],
            emails=emails,
            step_count=self._step_count,
            message=message,
        )