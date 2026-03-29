import uuid
from datetime import datetime
from database.sheets import get_messages_sheet


def log_message(ticket_id: str, direction: str, channel: str, content: str, sender: str):
    sheet = get_messages_sheet()
    message_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        message_id,
        ticket_id,
        direction,
        channel,
        content,
        sender,
        now
    ]
    sheet.append_row(row)
    return message_id
