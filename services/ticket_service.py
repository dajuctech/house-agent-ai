from database.tickets import get_or_create_ticket
from database.messages import log_message
from database.sheets import get_tickets_sheet
from ai.classifier import classify_message
from ai.smart_reply import generate_reply
from channels.email_handler import send_email_reply
from channels.whatsapp_handler import send_whatsapp_reply
from services.scheduler import offer_repair_slots, book_selected_slot


def process_incoming_message(sender: str, subject: str, body: str, channel: str = "email"):
    # Step 1 — Get or create ticket
    ticket_id, is_new = get_or_create_ticket(sender, subject, channel)
    print(f"Ticket: {ticket_id} | New: {is_new}")

    # Step 2 — Check if tenant is selecting a repair slot
    if body.strip() in ["1", "2", "3"]:
        slot_number = int(body.strip())
        confirmation = book_selected_slot(ticket_id, sender, slot_number, subject)
        print(f"Slot {slot_number} booked for {sender}")
        if channel == "email":
            send_email_reply(sender, subject, confirmation)
        elif channel == "whatsapp":
            send_whatsapp_reply(sender, confirmation)
        log_message(ticket_id, "outbound", channel, confirmation, "system")
        return {"ticket_id": ticket_id, "intent": "maintenance", "priority": "normal", "summary": subject, "reply": confirmation}

    # Step 3 — Log inbound message
    log_message(ticket_id, "inbound", channel, body, sender)
    print("Inbound message logged")

    # Step 4 — Classify with AI
    classification = classify_message(body)
    intent = classification.get("intent", "general")
    priority = classification.get("priority", "normal")
    summary = classification.get("summary", "")
    print(f"Intent: {intent} | Priority: {priority}")

    # Step 5 — Update ticket with classification
    sheet = get_tickets_sheet()
    records = sheet.get_all_records()
    for i, record in enumerate(records):
        if record.get("ticket_id") == ticket_id:
            sheet.update_cell(i + 2, 5, intent)
            sheet.update_cell(i + 2, 6, priority)
            sheet.update_cell(i + 2, 7, summary)
            break

    # Step 6 — Generate reply or offer slots
    if intent == "maintenance":
        reply = offer_repair_slots(ticket_id, sender, summary)
    else:
        reply = generate_reply(body, intent, priority, channel)
    print(f"Reply generated: {reply[:80]}...")

    # Step 7 — Send reply via correct channel
    if channel == "email":
        send_email_reply(sender, subject, reply)
    elif channel == "whatsapp":
        send_whatsapp_reply(sender, reply)

    # Step 8 — Log outbound reply
    log_message(ticket_id, "outbound", channel, reply, "system")
    print("Outbound reply logged")

    return {
        "ticket_id": ticket_id,
        "intent": intent,
        "priority": priority,
        "summary": summary,
        "reply": reply
    }
