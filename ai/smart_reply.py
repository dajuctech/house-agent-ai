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


def generate_reply(message: str, intent: str, priority: str) -> str:
    policy = find_policy(intent)

    prompt = f"""
You are a professional and friendly property management assistant.

Tenant message: {message}
Intent: {intent}
Priority: {priority}
Policy: {policy if policy else "Use general best practices for property management."}

Write a helpful, empathetic reply to the tenant. 
- Keep it under 150 words
- Be professional and friendly
- Reference the policy where relevant
- Give clear next steps
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
