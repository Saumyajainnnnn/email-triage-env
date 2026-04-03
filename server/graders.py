CORRECT_ORDER = ["e4", "e1", "e2", "e5", "e3"]

CORRECT_DEPT = {
    "e1": "exec",
    "e2": "finance",
    "e3": "spam",
    "e4": "support",
    "e5": "internal",
}

REPLIES_NEEDED = ["e1", "e2", "e4"]


def grade_sort(payload: dict) -> float:
    pred = payload.get("order", [])
    if not pred:
        return 0.0
    score = 0.0
    for i, eid in enumerate(CORRECT_ORDER):
        if i < len(pred) and pred[i] == eid:
            score += 1.0
    return round(score / len(CORRECT_ORDER), 2)


def grade_route_reply(payload: dict) -> float:
    routing = payload.get("routing", {})
    replies = payload.get("replies", {})

    routing_score = sum(
        1 for eid, dept in CORRECT_DEPT.items()
        if routing.get(eid) == dept
    ) / len(CORRECT_DEPT)

    reply_score = sum(
        1 for eid in REPLIES_NEEDED
        if len(replies.get(eid, "")) > 20
    ) / len(REPLIES_NEEDED)

    return round(0.6 * routing_score + 0.4 * reply_score, 2)


def grade_sla_escalate(payload: dict) -> float:
    score = 0.0

    if "e4" in payload.get("sla_breaches", []):
        score += 0.4

    if len(payload.get("escalation_message", "")) > 50:
        score += 0.3

    steps = payload.get("remediation_steps", [])
    score += min(len(steps), 3) / 3 * 0.3

    return round(score, 2)
