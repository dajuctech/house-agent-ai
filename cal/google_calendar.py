import os
import json
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = "danjudchicloud@gmail.com"


def get_calendar_service():
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    service = build("calendar", "v3", credentials=creds)
    return service


def get_available_slots(days_ahead: int = 3):
    service = get_calendar_service()
    now = datetime.utcnow()
    slots = []

    for day in range(1, days_ahead + 1):
        date = now + timedelta(days=day)
        for hour in [9, 13, 16]:
            slot_start = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_end = slot_start + timedelta(hours=2)

            events_result = service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=slot_start.isoformat() + "Z",
                timeMax=slot_end.isoformat() + "Z",
                singleEvents=True
            ).execute()

            if not events_result.get("items"):
                slots.append({
                    "start": slot_start.strftime("%Y-%m-%d %H:%M"),
                    "end": slot_end.strftime("%Y-%m-%d %H:%M"),
                    "label": slot_start.strftime("%A %d %B at %I:%M %p")
                })

            if len(slots) == 3:
                return slots

    return slots


def book_appointment(slot_start: str, slot_end: str, tenant_email: str, summary: str, description: str):
    service = get_calendar_service()
    event = {
        "summary": f"Repair: {summary}",
        "description": description + f"\nTenant Email: {tenant_email}",
        "start": {"dateTime": slot_start.replace(" ", "T") + ":00Z", "timeZone": "UTC"},
        "end": {"dateTime": slot_end.replace(" ", "T") + ":00Z", "timeZone": "UTC"},
    }
    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")
    return event.get("id")


def get_upcoming_events(days_ahead: int = 30):
    service = get_calendar_service()
    now = datetime.utcnow()
    time_max = now + timedelta(days=days_ahead)

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now.isoformat() + "Z",
        timeMax=time_max.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    result = []
    for e in events:
        start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date", "")
        end = e.get("end", {}).get("dateTime") or e.get("end", {}).get("date", "")
        result.append({
            "id": e.get("id"),
            "summary": e.get("summary", "No title"),
            "description": e.get("description", ""),
            "start": start,
            "end": end,
            "type": "blocked" if e.get("summary", "").startswith("BLOCKED") else "repair"
        })
    return result


def block_date(date_str: str, reason: str = "Unavailable"):
    service = get_calendar_service()
    event = {
        "summary": f"BLOCKED: {reason}",
        "start": {"date": date_str},
        "end": {"date": date_str},
    }
    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return event.get("id")


def delete_event(event_id: str):
    service = get_calendar_service()
    service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
