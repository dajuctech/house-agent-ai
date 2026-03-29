import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")


def send_whatsapp_reply(to: str, body: str):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_=whatsapp_number,
        to=to,
        body=body
    )
    print(f"WhatsApp reply sent to {to} | SID: {message.sid}")
    return message.sid
