import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_message(message: str) -> dict:
    prompt = f"""
You are a property management assistant. Classify the following tenant message.

Message: {message}

Respond in this exact JSON format:
{{
  "intent": "one of: maintenance, payment, complaint, noise, general, emergency, lease, deposit, parking, pets",
  "priority": "one of: urgent, normal, low",
  "summary": "one sentence description of the issue"
}}

Priority rules:
- urgent: gas leak, flooding, no heating in winter, electrical faults, break-ins
- normal: standard repairs, payment queries, complaints
- low: general enquiries, parking, noise during day
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    import json
    return json.loads(result)
