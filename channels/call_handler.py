import os
import httpx
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Record, Say
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
phone_number = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(account_sid, auth_token)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def handle_incoming_call():
    response = VoiceResponse()
    response.say(
        "Thank you for calling House Agent AI. "
        "Please leave your message after the tone "
        "and we will text you back within minutes.",
        voice="alice"
    )
    response.record(
        action="/webhook/call/recording",
        max_length=120,
        play_beep=True,
        trim="trim-silence"
    )
    response.say("Thank you. Goodbye.", voice="alice")
    return str(response)


def transcribe_recording(recording_url: str) -> str:
    audio_response = httpx.get(
        recording_url,
        auth=(account_sid, auth_token)
    )
    audio_content = audio_response.content
    transcript = openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=("recording.mp3", audio_content, "audio/mpeg")
    )
    return transcript.text


def send_sms_reply(to: str, body: str):
    message = twilio_client.messages.create(
        from_=phone_number,
        to=to,
        body=body[:160]
    )
    print(f"SMS sent to {to} | SID: {message.sid}")
    return message.sid
