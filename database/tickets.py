import uuid
from datetime import datetime
from database.sheets import get_tickets_sheet


def find_existing_ticket(sender_email: str):
    sheet = get_tickets_sheet()
    records = sheet.get_all_records()
    for record in records:
        if record.get("customer_id") == sender_email and record.get("status") != "closed":
            return record
    return None


def create_ticket(sender_email: str, subject: str, channel: str = "email"):
    sheet = get_tickets_sheet()
    ticket_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        ticket_id,
        sender_email,
        channel,
        "open",
        "",
        "",
        "",
        subject,
        now,
        now
    ]
    sheet.append_row(row)
    return ticket_id


def get_or_create_ticket(sender_email: str, subject: str, channel: str = "email"):
    existing = find_existing_ticket(sender_email)
    if existing:
        return existing["ticket_id"], False
    ticket_id = create_ticket(sender_email, subject, channel)
    return ticket_id, True
