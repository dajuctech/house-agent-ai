from cal.google_calendar import get_available_slots, book_appointment
from database.messages import log_message


def offer_repair_slots(ticket_id: str, tenant_email: str, issue_summary: str) -> str:
    slots = get_available_slots()
    if not slots:
        return "No available slots found. We will contact you shortly to arrange a repair."

    message = f"We have received your maintenance request regarding: {issue_summary}\n\n"
    message += "Please reply with the number of your preferred slot:\n\n"
    for i, slot in enumerate(slots, 1):
        message += f"{i}. {slot['label']}\n"

    log_message(ticket_id, "outbound", "system", message, "system")
    return message


def book_selected_slot(ticket_id: str, tenant_email: str, slot_number: int, issue_summary: str) -> str:
    slots = get_available_slots()
    if slot_number < 1 or slot_number > len(slots):
        return "Invalid slot number. Please reply with 1, 2, or 3."

    selected = slots[slot_number - 1]
    description = f"Repair for ticket {ticket_id}\nTenant: {tenant_email}\nIssue: {issue_summary}"

    book_appointment(
        slot_start=selected["start"],
        slot_end=selected["end"],
        tenant_email=tenant_email,
        summary=issue_summary,
        description=description
    )

    confirmation = (
        f"Your repair has been booked for {selected['label']}. "
        f"A technician will visit your property. "
        f"You will receive a reminder 24 hours before."
    )
    log_message(ticket_id, "outbound", "system", confirmation, "system")
    return confirmation
