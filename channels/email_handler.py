import os
import base64
import json
import email.mime.text
import email.mime.multipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_FILE = "gmail_token.json"
CREDENTIALS_FILE = "gmail_credentials.json"


def get_gmail_service():
    creds = None

    # Try loading token from env var first (Railway), then from file (local)
    token_json = os.getenv("GMAIL_TOKEN")
    if token_json:
        creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
    elif os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token back to file if running locally
            if not os.getenv("GMAIL_TOKEN") and os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
        else:
            # OAuth flow only works locally — on Railway, GMAIL_TOKEN must be set
            creds_json = os.getenv("GMAIL_CREDENTIALS")
            if creds_json:
                raise RuntimeError(
                    "GMAIL_TOKEN env var is missing or expired. "
                    "Run the app locally to generate a fresh gmail_token.json, "
                    "then set its contents as GMAIL_TOKEN in Railway."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_unread_emails():
    service = get_gmail_service()
    results = service.users().messages().list(
        userId="me", labelIds=["INBOX"], q="is:unread"
    ).execute()
    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()
        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")
        body = ""
        payload = msg_data["payload"]
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break
        elif "body" in payload and "data" in payload["body"]:
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        service.users().messages().modify(
            userId="me", id=msg["id"],
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        emails.append({
            "id": msg["id"],
            "sender": sender,
            "subject": subject,
            "body": body
        })
    return emails


def send_email_reply(to: str, subject: str, body: str):
    service = get_gmail_service()
    message = email.mime.multipart.MIMEMultipart()
    message["to"] = to
    message["subject"] = f"Re: {subject}"
    message.attach(email.mime.text.MIMEText(body, "plain"))
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()
    print(f"Reply sent to {to}")
