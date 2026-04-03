from datetime import datetime, timedelta

now = datetime.now()

EMAILS = [
    {
        "id": "e1",
        "from": "ceo@acme.com",
        "subject": "Board deck needed ASAP",
        "body": "Need the Q3 deck by 5pm today. Please send it to the board members.",
        "received_at": str(now - timedelta(hours=1)),
    },
    {
        "id": "e2",
        "from": "billing@vendor.com",
        "subject": "Invoice #4421 overdue",
        "body": "Your invoice is 30 days past due. Please arrange payment immediately.",
        "received_at": str(now - timedelta(hours=3)),
    },
    {
        "id": "e3",
        "from": "newsletter@medium.com",
        "subject": "Top stories this week",
        "body": "Here are this week's top stories from Medium.",
        "received_at": str(now - timedelta(hours=5)),
    },
    {
        "id": "e4",
        "from": "customer@bigclient.com",
        "subject": "Production is DOWN",
        "body": "Our integration broke 2 hours ago. SLA breach in 1 hour. Need immediate help.",
        "received_at": str(now - timedelta(hours=2)),
        "sla_note": "SLA deadline approaching within 1 hour",
    },
    {
        "id": "e5",
        "from": "hr@acme.com",
        "subject": "Team lunch Friday",
        "body": "Just a reminder that team lunch is at noon on Friday.",
        "received_at": str(now - timedelta(minutes=30)),
    },
]
