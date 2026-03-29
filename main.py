from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
from channels.email_handler import get_unread_emails
from services.ticket_service import process_incoming_message
from services.escalation import check_and_escalate
from webhooks.routes import router
from database.sheets import (
    get_tickets_sheet, get_messages_sheet, get_knowledge_base_sheet,
    add_knowledge_base_entry, update_knowledge_base_entry,
    delete_knowledge_base_entry, toggle_knowledge_base_entry,
    update_ticket_status
)
from cal.google_calendar import (
    get_upcoming_events, block_date, delete_event
)

app = FastAPI()
app.include_router(router)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
scheduler = BackgroundScheduler()


class KBEntry(BaseModel):
    topic: str
    content: str
    keywords: str


class BlockDate(BaseModel):
    date: str
    reason: str = "Unavailable"


class TicketStatusUpdate(BaseModel):
    status: str


def poll_emails():
    print("Polling Gmail for new emails...")
    emails = get_unread_emails()
    print(f"Found {len(emails)} unread emails")
    for email in emails:
        process_incoming_message(
            sender=email["sender"],
            subject=email["subject"],
            body=email["body"],
            channel="email"
        )


@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(poll_emails, "interval", seconds=60)
    scheduler.add_job(check_and_escalate, "interval", minutes=30)
    scheduler.start()
    print("Email poller started")
    print("Escalation checker started")


@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/dashboard")
def dashboard():
    return FileResponse("frontend/index.html")


@app.get("/tickets")
def tickets_page():
    return FileResponse("frontend/tickets.html")


@app.get("/knowledge-base")
def knowledge_base_page():
    return FileResponse("frontend/knowledge_base.html")


@app.get("/calendar")
def calendar_page():
    return FileResponse("frontend/calendar.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def api_stats():
    tickets = get_tickets_sheet().get_all_records()
    total = len(tickets)
    open_count = sum(1 for t in tickets if t.get("status") == "open")
    urgent_count = sum(1 for t in tickets if t.get("priority") == "urgent")
    escalated_count = sum(1 for t in tickets if t.get("status") == "escalated")
    closed_count = sum(1 for t in tickets if t.get("status") == "closed")
    return {
        "total": total,
        "open": open_count,
        "urgent": urgent_count,
        "escalated": escalated_count,
        "closed": closed_count
    }


@app.get("/api/tickets")
def api_tickets():
    tickets = get_tickets_sheet().get_all_records()
    return {"tickets": tickets}


@app.patch("/api/tickets/{ticket_id}")
def api_update_ticket_status(ticket_id: str, body: TicketStatusUpdate):
    success = update_ticket_status(ticket_id, body.status)
    if success:
        return {"status": "updated"}
    return {"status": "not_found"}


@app.get("/api/tickets/{ticket_id}/messages")
def api_ticket_messages(ticket_id: str):
    messages = get_messages_sheet().get_all_records()
    ticket_messages = [m for m in messages if m.get("ticket_id") == ticket_id]
    return {"messages": ticket_messages}


@app.get("/api/knowledge-base")
def api_knowledge_base():
    records = get_knowledge_base_sheet().get_all_records()
    return {"knowledge_base": records}


@app.post("/api/knowledge-base")
def api_add_knowledge_base(entry: KBEntry):
    add_knowledge_base_entry(entry.topic, entry.content, entry.keywords)
    return {"status": "added"}


@app.put("/api/knowledge-base/{row_id}")
def api_update_knowledge_base(row_id: int, entry: KBEntry):
    update_knowledge_base_entry(row_id, entry.topic, entry.content, entry.keywords)
    return {"status": "updated"}


@app.delete("/api/knowledge-base/{row_id}")
def api_delete_knowledge_base(row_id: int):
    delete_knowledge_base_entry(row_id)
    return {"status": "deleted"}


@app.patch("/api/knowledge-base/{row_id}/toggle")
def api_toggle_knowledge_base(row_id: int):
    new_value = toggle_knowledge_base_entry(row_id)
    return {"status": "toggled", "active": new_value}


@app.get("/api/calendar/events")
def api_calendar_events():
    events = get_upcoming_events(days_ahead=30)
    return {"events": events}


@app.post("/api/calendar/block")
def api_block_date(body: BlockDate):
    event_id = block_date(body.date, body.reason)
    return {"status": "blocked", "event_id": event_id}


@app.delete("/api/calendar/block/{event_id}")
def api_delete_block(event_id: str):
    delete_event(event_id)
    return {"status": "deleted"}
