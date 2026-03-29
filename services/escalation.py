import os
from datetime import datetime, timedelta
from database.sheets import get_tickets_sheet
from channels.email_handler import send_email_reply
from channels.whatsapp_handler import send_whatsapp_reply
from dotenv import load_dotenv

load_dotenv()

LANDLORD_EMAIL = os.getenv("LANDLORD_EMAIL")
LANDLORD_WHATSAPP = os.getenv("LANDLORD_WHATSAPP")

ESCALATION_HOURS = {
    "urgent": 4,
    "normal": 24,
    "low": 72
}


def check_and_escalate():
    print("Running escalation check...")
    sheet = get_tickets_sheet()
    records = sheet.get_all_records()
    now = datetime.utcnow()
    escalated_count = 0

    for i, record in enumerate(records):
        status = record.get("status", "")
        priority = record.get("priority", "normal").lower()
        created_at = record.get("created_at", "")

        if status in ["closed", "escalated", ""]:
            continue

        if not created_at:
            continue

        try:
            created_time = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        hours_open = (now - created_time).total_seconds() / 3600
        threshold = ESCALATION_HOURS.get(priority, 24)

        if hours_open >= threshold:
            ticket_id = record.get("ticket_id", "")
            customer_id = record.get("customer_id", "")
            summary = record.get("summary", "No summary available")

            message = (
                f"ESCALATION ALERT\n"
                f"Ticket: {ticket_id}\n"
                f"Tenant: {customer_id}\n"
                f"Priority: {priority}\n"
                f"Open for: {hours_open:.1f} hours\n"
                f"Issue: {summary}"
            )

            print(f"Escalating ticket {ticket_id}")

            # Send email alert
            send_email_reply(LANDLORD_EMAIL, f"ESCALATION: Ticket {ticket_id}", message)

            # Send WhatsApp alert
            send_whatsapp_reply(LANDLORD_WHATSAPP, message[:1000])

            # Update ticket status
            sheet.update_cell(i + 2, 4, "escalated")
            escalated_count += 1

    print(f"Escalation check complete. {escalated_count} tickets escalated.")
