from fastapi import APIRouter, Request, Form
from services.ticket_service import process_incoming_message
from channels.call_handler import handle_incoming_call, transcribe_recording, send_sms_reply
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    print(f"WhatsApp message from {From}: {Body}")
    result = process_incoming_message(
        sender=From,
        subject="WhatsApp Message",
        body=Body,
        channel="whatsapp"
    )
    return {"status": "ok", "ticket_id": result["ticket_id"]}


@router.post("/webhook/call", response_class=HTMLResponse)
async def call_webhook():
    print("Incoming call received")
    twiml = handle_incoming_call()
    return HTMLResponse(content=twiml, media_type="application/xml")


@router.post("/webhook/call/recording", response_class=HTMLResponse)
async def call_recording_webhook(
    RecordingUrl: str = Form(...),
    From: str = Form(...),
    CallDuration: str = Form(default="0")
):
    print(f"Recording received from {From} | Duration: {CallDuration}s")
    transcript = transcribe_recording(RecordingUrl)
    print(f"Transcript: {transcript}")
    result = process_incoming_message(
        sender=From,
        subject="Phone Call",
        body=transcript,
        channel="phone"
    )
    sms_reply = result["reply"][:160]
    send_sms_reply(From, sms_reply)
    return HTMLResponse(content="<Response/>", media_type="application/xml")
