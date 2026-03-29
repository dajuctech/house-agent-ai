import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from database.sheets import get_knowledge_base_sheet

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def find_policy(intent: str) -> str:
    sheet = get_knowledge_base_sheet()
    records = sheet.get_all_records()
    for record in records:
        if record.get("topic") == intent and record.get("active") == "TRUE":
            return record.get("content", "")
    return ""


CHANNEL_INSTRUCTIONS = {
    "email": (
        "Write a formal email reply. Use a greeting (e.g. 'Dear Tenant,'), "
        "full sentences, and a sign-off (e.g. 'Kind regards, House Agent AI'). "
        "Keep it under 150 words."
    ),
    "whatsapp": (
        "Write a short, friendly WhatsApp message. "
        "No formal greeting or sign-off needed. Use natural, conversational language. "
        "Keep it under 80 words."
    ),
    "sms": (
        "Write a very short SMS reply. Plain text only, no formatting. "
        "Maximum 160 characters. Be direct and clear."
    ),
    "call": (
        "Write a short SMS reply to someone who just left a voicemail. "
        "Acknowledge their call and give clear next steps. "
        "Plain text only. Maximum 160 characters."
    ),
}


def generate_reply(message: str, intent: str, priority: str, channel: str = "email") -> str:
    policy = find_policy(intent)
    channel_instruction = CHANNEL_INSTRUCTIONS.get(channel, CHANNEL_INSTRUCTIONS["email"])

    prompt = f"""
You are a professional and friendly property management assistant.

Tenant message: {message}
Intent: {intent}
Priority: {priority}
Channel: {channel}
Policy: {policy if policy else "Use general best practices for property management."}

{channel_instruction}
- Be professional and empathetic
- Reference the policy where relevant
- Give clear next steps
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
