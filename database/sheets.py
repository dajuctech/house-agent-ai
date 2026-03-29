import gspread
from google.oauth2.service_account import Credentials
import os
import json
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")


def get_sheet_client():
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def get_worksheet(tab_name: str):
    client = get_sheet_client()
    spreadsheet = client.open_by_key(SHEETS_ID)
    return spreadsheet.worksheet(tab_name)


def get_tickets_sheet():
    return get_worksheet("Tickets")


def get_messages_sheet():
    return get_worksheet("Messages")


def get_calls_sheet():
    return get_worksheet("Calls")


def get_knowledge_base_sheet():
    return get_worksheet("Knowledge_Base")


def add_knowledge_base_entry(topic: str, content: str, keywords: str):
    sheet = get_knowledge_base_sheet()
    all_rows = sheet.get_all_values()
    next_id = len(all_rows)
    sheet.append_row([next_id, topic, content, keywords, "TRUE"])


def update_knowledge_base_entry(row_index: int, topic: str, content: str, keywords: str):
    sheet = get_knowledge_base_sheet()
    sheet.update(f"B{row_index}:D{row_index}", [[topic, content, keywords]])


def delete_knowledge_base_entry(row_index: int):
    sheet = get_knowledge_base_sheet()
    sheet.delete_rows(row_index)


def toggle_knowledge_base_entry(row_index: int):
    sheet = get_knowledge_base_sheet()
    current = sheet.cell(row_index, 5).value
    new_value = "FALSE" if current == "TRUE" else "TRUE"
    sheet.update_cell(row_index, 5, new_value)
    return new_value


def update_ticket_status(ticket_id: str, status: str):
    sheet = get_tickets_sheet()
    records = sheet.get_all_records()
    for i, row in enumerate(records):
        if row.get("ticket_id") == ticket_id:
            row_index = i + 2  # +1 for header, +1 for 1-based index
            # Find the status column
            headers = sheet.row_values(1)
            status_col = headers.index("status") + 1
            sheet.update_cell(row_index, status_col, status)
            return True
    return False
