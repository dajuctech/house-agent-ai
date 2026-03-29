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
  "summary": "one sentence description of the issue",
  "needs_more_info": true or false,
  "resolvable_remotely": true or false
}}

Priority rules:
- urgent: gas leak, flooding, no heating in winter, electrical faults, break-ins
- normal: standard repairs, payment queries, complaints
- low: general enquiries, parking, noise during day

needs_more_info rules:
- true: message is vague, missing location, missing details needed to act (e.g. "something is broken", "there's a problem")
- false: message has enough detail to act on

resolvable_remotely rules:
- true: can be resolved by providing information, policy, advice or payment link (payment queries, lease questions, general enquiries, noise advice)
- false: requires a physical visit or landlord involvement (maintenance, flooding, break-ins, electrical faults)
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    import json
    return json.loads(result)
