# 🏠 House Agent AI — Product Requirements Document (PRD)

---

## 1. Product Overview

**Product Name:** House Agent AI
**Version:** 1.0.0
**Owner:** Daniel Jude
**Date:** March 2026
**Status:** ✅ Built + Deployed on Railway
**Live URL:** https://web-production-9d9db.up.railway.app
**GitHub:** https://github.com/dajuctech/house-agent-ai

### Vision
An intelligent, fully automated landlord support system that handles tenant communications across multiple channels using AI — eliminating manual email responses, missed maintenance requests, and delayed repairs — with a professional web dashboard for the landlord.

### Problem Statement
Landlords managing multiple properties face:
- High volume of repetitive tenant emails
- Missed urgent maintenance requests
- Slow response times causing tenant dissatisfaction
- No centralised system to track all tenant issues
- Manual scheduling of repair appointments
- No visual dashboard to monitor all activity

### Solution
An AI-powered system that automatically receives, classifies, responds to, and tracks all tenant communications across email, WhatsApp, and phone — with intelligent repair scheduling, SMS text reply for calls, and a professional HTML/CSS/JavaScript dashboard built in.

---

## 2. Goals & Success Metrics

| Goal | Metric | Target |
|------|--------|--------|
| Reduce response time | Time to first reply | Under 2 minutes |
| Automate routine replies | % replies automated | 80% |
| Reduce missed urgent issues | Urgent escalation rate | 100% escalated within 4 hours |
| Centralise tenant data | % messages logged | 100% |
| Reduce repair booking time | Time to book repair | Under 10 minutes |
| Call response via SMS | Time to SMS after call | Under 3 minutes |
| Dashboard visibility | All tickets visible in real time | 100% |

---

## 3. Users

### Primary User — Landlord
- Receives escalation alerts
- Views all tickets in dashboard
- Manages Knowledge Base policies via dashboard
- Books repairers in Google Calendar
- Monitors all tenant communications in one place

### Secondary User — Tenant
- Sends messages via email, WhatsApp, or phone call
- Receives AI-generated smart replies via email, WhatsApp, or SMS
- Books repair appointments by replying with slot number
- Receives reminders before appointments

### Tertiary User — Repairer
- Receives job details via email or WhatsApp
- Gets Google Calendar invite for repair appointments
- Receives reminders before jobs

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   INCOMING CHANNELS                      │
│   📧 Gmail     💬 WhatsApp     📞 Phone Call             │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  FASTAPI SERVER                          │
│   Webhook receiver + Email poller + Background jobs      │
│   + Static file server (Frontend)                        │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                 CORE PIPELINE                            │
│  1. Extract message data                                 │
│  2. Lookup or create ticket                              │
│  3. AI classify (intent + priority + summary)            │
│  4. Search Knowledge Base                                │
│  5. Generate smart reply                                 │
│  6. Route reply to correct channel                       │
│     - Email → Gmail reply                                │
│     - WhatsApp → Twilio WhatsApp reply                   │
│     - Phone Call → Twilio SMS text reply                 │
│  7. Log everything to Google Sheets                      │
│  8. Check if repair scheduling needed                    │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  DATA + SERVICES                         │
│  Google Sheets    Google Calendar    OpenAI    Twilio    │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│              FRONTEND DASHBOARD                          │
│  HTML + Tailwind CSS + JavaScript                        │
│  Dashboard / Tickets / Calendar (+ KB at /knowledge-base)│
└─────────────────────────────────────────────────────────┘
```

---

## 5. Development Environment Setup

### 5.1 — Package Manager: uv

This project uses **uv** as the package manager instead of pip. uv is 10-100x faster than pip and automatically manages virtual environments and lock files.

**How uv works:**
- `pyproject.toml` — the shopping list (what packages are needed)
- `uv.lock` — the receipt (exact versions of every package)
- `.venv/` — the actual packages downloaded locally (never pushed to GitHub)

### 5.2 — Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart terminal then verify:
```bash
uv --version
```

### 5.3 — Create Project with uv

```bash
uv init house_agent_ai
cd house_agent_ai
rm hello.py
```

This automatically creates:
```
house_agent_ai/
├── pyproject.toml      ← dependency manager (replaces requirements.txt)
├── uv.lock             ← locked dependency versions
├── .python-version     ← Python version lock
└── .venv/              ← virtual environment (auto-managed)
```

### 5.4 — Create Project Structure

```bash
mkdir channels ai database services cal webhooks frontend
mkdir frontend/css frontend/js

touch main.py config.py .env .env.example README.md

touch channels/__init__.py channels/email_handler.py \
      channels/whatsapp_handler.py channels/call_handler.py

touch ai/__init__.py ai/classifier.py \
      ai/smart_reply.py ai/transcriber.py

touch database/__init__.py database/sheets.py database/tickets.py \
      database/messages.py database/knowledge_base.py

touch services/__init__.py services/ticket_service.py \
      services/reply_service.py services/escalation.py \
      services/scheduler.py

touch cal/__init__.py cal/google_calendar.py \
      cal/availability.py cal/reminders.py

touch webhooks/__init__.py webhooks/routes.py

touch frontend/index.html frontend/tickets.html \
      frontend/ticket_detail.html \
      frontend/knowledge_base.html frontend/calendar.html

touch frontend/css/style.css
touch frontend/js/api.js frontend/js/dashboard.js \
      frontend/js/tickets.js
```

> ⚠️ NOTE: The folder was named `cal/` NOT `calendar/` to avoid conflict with Python's built-in `calendar` module.

### 5.5 — Install All Dependencies with uv

```bash
uv add fastapi uvicorn openai gspread \
    google-auth google-auth-oauthlib google-api-python-client \
    twilio apscheduler python-dotenv \
    httpx python-multipart pydantic
```

### 5.6 — pyproject.toml (actual version used)

```toml
[project]
name = "house-agent-ai"
version = "0.1.0"
description = "Add your description here"
requires-python = ">=3.13"
dependencies = [
    "apscheduler>=3.11.2",
    "fastapi>=0.125.0",
    "google-api-python-client>=2.192.0",
    "google-auth>=2.47.0",
    "google-auth-oauthlib>=1.3.0",
    "gspread>=6.2.1",
    "openai>=2.14.0",
    "pydantic>=2.12.5",
    "python-dotenv>=1.2.1",
    "python-multipart>=0.0.21",
    "twilio>=9.10.3",
    "uvicorn>=0.38.0",
]
```

### 5.7 — Common uv Commands

| Command | Description |
|---------|-------------|
| `uv add package-name` | Add a new package |
| `uv remove package-name` | Remove a package |
| `uv sync` | Install all dependencies from lock file |
| `uv run uvicorn main:app --reload` | Run the server |
| `uv run python script.py` | Run any Python script |
| `uv lock` | Update the lock file |
| `uv pip list` | List installed packages |

### 5.8 — uv vs pip Comparison

| Feature | pip | uv |
|---------|-----|----|
| Speed | Slow | ✅ 10-100x faster |
| Lock file | Manual | ✅ Automatic (uv.lock) |
| Virtual env | Manual setup | ✅ Auto-managed |
| Dependency resolver | Basic | ✅ Advanced |
| Python version mgmt | ❌ | ✅ Built in |
| Reproducible builds | Limited | ✅ Full |

### 5.9 — Run the Server Locally

```bash
cd house_agent_ai
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Open browser:
- Dashboard → `http://localhost:8000/dashboard`
- Tickets → `http://localhost:8000/tickets`
- Knowledge Base → `http://localhost:8000/knowledge-base`
- Calendar → `http://localhost:8000/calendar`

### 5.10 — Expose with ngrok (for webhooks locally)

```bash
ngrok http 8000
```

Your public webhook URL:
```
https://your-ngrok-url.ngrok-free.app
```

Set in Twilio:
- WhatsApp webhook: `https://your-ngrok-url.ngrok-free.app/webhook/whatsapp`
- Voice webhook: `https://your-ngrok-url.ngrok-free.app/webhook/call`

### 5.11 — Known uv Issue (workspace root conflict)

When running `uv lock`, uv may save `uv.lock` to `~/uv.lock` (home folder) instead of the project folder. This happens because uv detects a `pyproject.toml` at `/Users/daniel/` and treats it as the workspace root.

**Fix:**
```bash
cp ~/uv.lock "/path/to/house_agent_ai/uv.lock"
git add -f uv.lock
git commit -m "Add uv.lock"
git push
```

---

## 6. Features

### Phase 1 — Database Setup ✅ COMPLETED
**Description:** Set up Google Sheets as the central database.

**Google Sheet:** "House Agent AI" with 4 tabs:

| Tab | Columns |
|-----|---------|
| Tickets | ticket_id, customer_id, channel, status, intent, priority, summary, subject, created_at, updated_at |
| Messages | message_id, ticket_id, direction, channel, content, sender, timestamp |
| Calls | call_id, ticket_id, phone_number, duration, transcript, summary, sms_sent, sms_status, timestamp |
| Knowledge_Base | doc_id, topic, content, keywords, active |

**Google Cloud Setup:**
1. Go to console.cloud.google.com
2. Create new project "House Agent AI"
3. Enable APIs: Google Sheets API, Google Drive API, Google Calendar API, Gmail API
4. Create Service Account → download `credentials.json`
5. Share Google Sheet with service account email
6. Share Google Calendar with service account email

**Acceptance Criteria:**
- Sheet created with correct tabs and columns ✅
- System can read and write to all tabs ✅
- All data persists correctly ✅

---

### Phase 2 — Email Automation ✅ COMPLETED
**Description:** Automatically receive and respond to tenant emails.

**Gmail OAuth Setup:**
1. Go to Google Cloud Console → APIs → Gmail API → Enable
2. Create OAuth 2.0 credentials → download `gmail_credentials.json`
3. Run the app locally once → browser opens for Gmail permission
4. `gmail_token.json` is created automatically and saved locally

**Flow:**
```
Gmail polls every 60 seconds
→ New email found
→ Extract sender, subject, body
→ Create or update ticket
→ Log message to Messages tab
→ Send acknowledgement reply
```

**Acceptance Criteria:**
- System detects new emails within 60 seconds ✅
- New tenants get a new ticket created ✅
- Returning tenants get existing ticket updated ✅
- All emails logged to Messages tab ✅
- Acknowledgement reply sent within 2 minutes ✅

---

### Phase 3 — AI Intent Detection ✅ COMPLETED
**Description:** Use OpenAI to classify every message.

**AI Output:**

| Field | Values |
|-------|--------|
| intent | maintenance, payment, complaint, noise, general, emergency, lease, deposit, parking, pets |
| priority | urgent, normal, low |
| summary | One sentence description |

**Priority Rules:**
- **Urgent:** gas leak, flooding, no heating in winter, electrical faults, break-ins
- **Normal:** standard repairs, payment queries, complaints
- **Low:** general enquiries, parking, noise during day

**Model used:** GPT-4o-mini (fast + cheap + accurate)

**Acceptance Criteria:**
- Every message classified within 10 seconds ✅
- intent, priority, summary saved to Tickets tab ✅
- Accuracy above 90% for common issues ✅

---

### Phase 4 — Knowledge Base + Smart Reply ✅ COMPLETED
**Description:** Search policies and generate personalised replies.

**Flow:**
```
Intent detected
→ Search Knowledge Base for matching policy
→ Pass message + policy to OpenAI
→ Generate smart, personalised reply
→ Send reply to tenant via correct channel
→ Log outbound reply to Messages tab
```

**Knowledge Base Structure (Google Sheet — Knowledge_Base tab):**

| Column | Description |
|--------|-------------|
| doc_id | Unique ID |
| topic | e.g. maintenance, emergency, rent_payment |
| content | The full policy text the AI uses |
| keywords | Comma-separated keywords for matching |
| active | TRUE / FALSE — toggle without deleting |

**Sample entries:**
- maintenance — 24-48 hour response policy
- emergency — gas leak, flooding instructions
- rent_payment — due date, late fee policy
- noise — quiet hours 11pm-7am

**Acceptance Criteria:**
- Reply references correct policy ✅
- Reply is under 150 words ✅
- Reply sent within 30 seconds of classification ✅
- All replies logged to Messages tab ✅

---

### Phase 5 — WhatsApp Integration ✅ COMPLETED
**Description:** Handle tenant messages via WhatsApp using Twilio.

**Twilio Setup:**
1. Go to twilio.com/console
2. Activate WhatsApp Sandbox
3. Set "When a message comes in" to: `https://your-url/webhook/whatsapp`
4. Tenants join sandbox by sending: `join <sandbox-code>` to `+14155238886`

**Fix applied:** Twilio WhatsApp number must be `whatsapp:+14155238886` (not `+whatsapp:...`)

**Flow:**
```
Tenant sends WhatsApp message to Twilio sandbox
→ Twilio sends webhook to FastAPI /webhook/whatsapp
→ System processes same as email
→ Reply sent back via WhatsApp
```

**Acceptance Criteria:**
- WhatsApp messages received within 5 seconds ✅
- Same AI classification as email ✅
- Reply sent back via WhatsApp (not email) ✅
- Channel recorded as "whatsapp" in Tickets ✅

---

### Phase 6 — Call Handling with SMS Reply ✅ COMPLETED
**Description:** Handle incoming phone calls with recording, transcription, and automatic SMS text message reply.

**Twilio Voice Setup:**
1. Buy a Twilio phone number
2. Set Voice webhook to: `https://your-url/webhook/call`

**Flow:**
```
Tenant calls Twilio phone number
        ↓
Automated voice greeting plays:
"Thank you for calling House Agent AI.
Please leave your message after the tone
and we will text you back within minutes."
        ↓
Call recorded (max 2 minutes)
        ↓
Twilio sends recording URL to /webhook/call/recording
        ↓
Audio downloaded and sent to OpenAI Whisper
        ↓
Call transcribed to text
        ↓
AI classifies intent + priority + summary
        ↓
Knowledge Base searched for relevant policy
        ↓
AI generates smart reply (SMS format — max 160 chars)
        ↓
SMS text message sent to tenant's phone number
        ↓
Call logged to Calls tab in Google Sheets
        ↓
Ticket created or updated in Tickets tab
        ↓
If priority = urgent → Landlord notified immediately
```

**Acceptance Criteria:**
- All calls recorded automatically ✅
- Transcription accuracy above 85% ✅
- SMS reply sent within 3 minutes of call ending ✅
- Channel recorded as "phone" in Tickets tab ✅

---

### Phase 7 — Escalation Logic ✅ COMPLETED
**Description:** Automatically escalate unresolved tickets.

**Escalation Rules:**

| Priority | Escalate After |
|----------|---------------|
| Urgent | 4 hours |
| Normal | 24 hours |
| Low | 72 hours |

**Escalation Actions:**
- Send email + WhatsApp to landlord
- Update ticket status to "escalated"
- Include tenant details + issue summary

**Background job:** Runs every 30 minutes via APScheduler

**Acceptance Criteria:**
- Escalation check runs every 30 minutes ✅
- Landlord notified via email AND WhatsApp ✅
- Ticket status updated to "escalated" ✅
- No duplicate escalation notifications ✅

---

### Phase 8 — Calendar Scheduling ✅ COMPLETED
**Description:** Automatically suggest and book repair appointments.

**Google Calendar Setup:**
1. Share calendar with service account email
2. Give "Make changes to events" permission
3. Use calendar ID: your Gmail address
4. Service account books events directly (no attendees — avoids permission errors)
5. Tenant email added to event description instead

**Flow:**
```
Maintenance issue detected
→ Check Google Calendar for conflicts
→ Generate 3 available time slots (9am, 1pm, 4pm)
→ Send slots to tenant via email or WhatsApp
→ Tenant replies with slot number (1, 2, or 3)
→ System books Google Calendar event
→ Send confirmation to tenant
→ Update ticket status to "repair_scheduled"
```

**Acceptance Criteria:**
- Available slots offered within 1 hour of maintenance report ✅
- Booking confirmed within 5 minutes of tenant reply ✅
- Ticket updated to "repair_scheduled" ✅

---

### Phase 9 — Frontend Dashboard ✅ COMPLETED
**Description:** A professional web dashboard built with HTML, Tailwind CSS, and JavaScript.

**Pages built:**

| Page | URL | Status |
|------|-----|--------|
| Dashboard | /dashboard | ✅ Complete |
| Tickets | /tickets | ✅ Complete |
| Knowledge Base | /knowledge-base | ✅ Complete (hidden from nav — landlord only) |
| Calendar | /calendar | ✅ Complete |

**Dashboard Features:**
- Total, Open, Urgent, Escalated, Closed ticket counts
- Each stat card is clickable → navigates to /tickets?filter=open (or urgent/escalated/closed/all)
- Tickets page heading updates to match filter (e.g. "Open Tickets") with a "Clear filter ×" link
- Recent tickets table with status/priority badges
- Click ticket → navigates to /tickets?id=... and auto-opens that ticket's modal directly
- Auto-refreshes data from Google Sheets via API
- Mobile card view (stacked) + Desktop table view

**Tickets Features:**
- Full tickets list with status/priority/channel badges
- Mobile card view + Desktop table view
- Click any ticket → opens modal with full details
- Modal shows: Tenant, Channel, Status, Priority, Summary, Created date
- Update Status from modal (Open / Closed / Escalated / Resolved)
- Message history showing all inbound and outbound messages with timestamps
- Save button works on both desktop and mobile (touchend event)

**Knowledge Base Features:**
- Split-panel layout (topic list + detail view)
- Topic icons auto-assigned by keyword
- Active/Inactive toggle
- Add, Edit, Delete entries from dashboard
- Changes saved directly to Google Sheet
- **Hidden from navigation** — landlord manages directly via /knowledge-base URL

**Calendar Features:**
- Monthly calendar view with navigation
- Blue dots = repair appointments
- Red dots = blocked dates
- Click any day → see events for that day
- Block a date (mark as unavailable)
- Remove blocked dates
- Upcoming events list (next 30 days)

**Navbar:**
- House Agent AI logo clickable → goes to dashboard
- Active page highlighted with underline
- Links: Dashboard | Tickets | Calendar
- Knowledge Base removed from nav (client-facing simplification)
- Mobile hamburger menu on all pages (toggles with style.display — NOT Tailwind hidden class)

**Mobile Responsive Design:**
- All 4 pages fully responsive
- Hamburger menu replaces desktop nav on mobile
- Stats cards: 2 columns on mobile, 5 columns on desktop
- Ticket/dashboard tables replaced with card layout on mobile
- Calendar cells scale down on small screens
- Modals scroll correctly on mobile (outer overlay scrollable, not inner modal)
- Save button uses touchend event listener for reliable mobile tap

**Technology:**
- HTML5 for structure
- Tailwind CSS (CDN) for professional styling
- Vanilla JavaScript for interactivity
- fetch() API calls to FastAPI backend
- No React or complex frameworks needed

---

### Phase 10 — Deployment ✅ COMPLETED
**Description:** Deploy the application to Railway for 24/7 availability.

**Deployment Platform:** Railway (railway.app)
**Live URL:** https://web-production-9d9db.up.railway.app

**Files needed for deployment:**

| File | Purpose |
|------|---------|
| `Procfile` | Tells Railway how to start the app |
| `pyproject.toml` | List of packages to install |
| `uv.lock` | Exact package versions |
| `railway.json` | Railway-specific config |

**Procfile:**
```
web: uv run uvicorn main:app --host 0.0.0.0 --port $PORT
```

**railway.json:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uv run uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Environment Variables on Railway:**

| Variable | Description |
|----------|-------------|
| GOOGLE_SHEETS_ID | Google Sheets document ID |
| OPENAI_API_KEY | OpenAI API key |
| TWILIO_ACCOUNT_SID | Twilio account SID |
| TWILIO_AUTH_TOKEN | Twilio auth token |
| TWILIO_WHATSAPP_NUMBER | `whatsapp:+14155238886` |
| TWILIO_PHONE_NUMBER | Twilio voice phone number |
| LANDLORD_EMAIL | Landlord's email address |
| LANDLORD_WHATSAPP | `whatsapp:+447881153882` |
| URGENT_ESCALATION_HOURS | `4` |

**Deployment Steps:**
1. Create `Procfile` and `railway.json`
2. Run `uv lock` to generate `uv.lock`
3. `git init` → `git add .` → `git commit -m "Initial commit"`
4. Create repo on GitHub: github.com/dajuctech/house-agent-ai
5. `git remote add origin https://github.com/dajuctech/house-agent-ai`
6. `git push -u origin main`
7. Go to railway.app → New Project → Deploy from GitHub
8. Select repo → Railway builds automatically
9. Add environment variables in Variables tab
10. Click Deploy

**Issues encountered and fixed:**

| Issue | Fix |
|-------|-----|
| `uvicorn: command not found` | Changed Procfile to use `uv run uvicorn` |
| `uv.lock` not created in project folder | uv was saving to `~/uv.lock` due to workspace root conflict — manually copied to project |
| Branch named `master` not `main` | Ran `git branch -M main` |
| GitHub rejected push | Ran `git pull origin main --rebase` first |
| `FileNotFoundError: credentials.json` on Railway | `credentials.json` does not exist on Railway server — updated `database/sheets.py` and `cal/google_calendar.py` to read from `GOOGLE_CREDENTIALS` env var using `json.loads()` instead of file |
| `FileNotFoundError: gmail_credentials.json` on Railway | Gmail OAuth file not present on Railway — added `GMAIL_TOKEN` env var to Railway for gmail token handling |
| `json.decoder.JSONDecodeError` on Railway | `GOOGLE_CREDENTIALS` env var was empty or had wrong format — fixed by running `cat credentials.json \| python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)))" \| pbcopy` and pasting the single-line JSON into Railway Raw Editor |

**How to correctly set GOOGLE_CREDENTIALS on Railway:**
```bash
cat credentials.json | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)))" | pbcopy
```
Then paste the clipboard value into Railway → Variables → Raw Editor. The value must be a single-line JSON string with no extra quotes.

**Twilio Webhooks on Railway (updated):**
- WhatsApp webhook: `https://web-production-9d9db.up.railway.app/webhook/whatsapp`
- Voice webhook: `https://web-production-9d9db.up.railway.app/webhook/call`
- Recording webhook: `https://web-production-9d9db.up.railway.app/webhook/call/recording`

**UK Phone Number:**
- Target number: +44 7588 332029 (Mobile, Voice + SMS, £0.83/month)
- "UK Local Individual" bundle was approved by John but wrong type for mobile numbers
- "UK Mobile Individual" bundle submitted 2026-03-29 — under review (7 days avg)
- Next: Email John to fast-track approval, then buy +44 7588 332029

---

## 7. Technical Requirements

### Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13 |
| Package Manager | uv |
| Web Framework | FastAPI |
| AI | OpenAI GPT-4o-mini |
| Transcription | OpenAI Whisper |
| Database | Google Sheets API |
| Email | Gmail API (OAuth) |
| WhatsApp + Calls + SMS | Twilio |
| Calendar | Google Calendar API |
| Scheduler | APScheduler (background jobs) |
| Frontend | HTML + Tailwind CSS + Vanilla JavaScript |
| Environment | python-dotenv |
| Deployment | Railway |
| Version Control | Git + GitHub |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| / | GET | Serve dashboard |
| /dashboard | GET | Serve dashboard HTML |
| /tickets | GET | Serve tickets HTML |
| /knowledge-base | GET | Serve knowledge base HTML |
| /calendar | GET | Serve calendar HTML |
| /health | GET | System status |
| /api/stats | GET | Dashboard statistics |
| /api/tickets | GET | Get all tickets JSON |
| /api/tickets/{id} | PATCH | Update ticket status |
| /api/tickets/{id}/messages | GET | Get messages for ticket |
| /api/knowledge-base | GET | Get all KB entries |
| /api/knowledge-base | POST | Add new KB entry |
| /api/knowledge-base/{id} | PUT | Update KB entry |
| /api/knowledge-base/{id} | DELETE | Delete KB entry |
| /api/knowledge-base/{id}/toggle | PATCH | Toggle active/inactive |
| /api/calendar/events | GET | Get upcoming events |
| /api/calendar/block | POST | Block a date |
| /api/calendar/block/{id} | DELETE | Remove blocked date |
| /webhook/whatsapp | POST | Receive WhatsApp messages |
| /webhook/call | POST | Receive incoming call |
| /webhook/call/recording | POST | Receive call recording |

### Environment Variables

| Variable | Description |
|----------|-------------|
| OPENAI_API_KEY | OpenAI API key |
| GOOGLE_SHEETS_ID | Google Sheets document ID |
| TWILIO_ACCOUNT_SID | Twilio account SID |
| TWILIO_AUTH_TOKEN | Twilio auth token |
| TWILIO_WHATSAPP_NUMBER | Twilio WhatsApp number (format: whatsapp:+number) |
| TWILIO_PHONE_NUMBER | Twilio voice phone number |
| LANDLORD_EMAIL | Landlord's email address |
| LANDLORD_WHATSAPP | Landlord's WhatsApp (format: whatsapp:+number) |
| URGENT_ESCALATION_HOURS | Hours before urgent escalation (default: 4) |

---

## 8. Reply Channel Matrix

| Incoming Channel | Reply Channel | Technology |
|-----------------|--------------|-----------|
| Email | Email reply | Gmail API |
| WhatsApp | WhatsApp message | Twilio WhatsApp |
| Phone Call | SMS text message | Twilio SMS |

---

## 9. Data Flow Diagram

```
TENANT
  │
  ├── Email ──────────────────────────────────────────┐
  │                                                    │
  ├── WhatsApp ────────────────────────────────────────┤
  │                                                    ↓
  └── Phone Call ──── Record ──── Transcribe ─── FastAPI Server
                                                       │
                                              ┌────────┴────────┐
                                              │                 │
                                         New Tenant       Existing Tenant
                                              │                 │
                                         Create Ticket    Update Ticket
                                              └────────┬────────┘
                                                       │
                                              AI Classification
                                              (intent/priority/summary)
                                                       │
                                              Knowledge Base Search
                                                       │
                                              Smart Reply Generation
                                                       │
                                   ┌───────────────────┼───────────────────┐
                                   │                   │                   │
                              Email Reply       WhatsApp Reply        SMS Reply
                              (Gmail)           (Twilio WA)          (Twilio SMS)
                                   │                   │                   │
                                   └───────────────────┼───────────────────┘
                                                       │
                                              Log to Messages Tab
                                                       │
                                   ┌───────────────────┴───────────────────┐
                                   │                                       │
                             Maintenance?                           Other Intent
                                   │                                       │
                          Offer Repair Slots                      Normal flow ends
                                   │
                          Tenant picks slot
                                   │
                          Book Google Calendar
                                   │
                          Send Confirmation
                                   │
                          ─────────────────────
                          LANDLORD DASHBOARD
                          (HTML/CSS/JS Frontend)
                          Views all in real time
```

---

## 10. Project Folder Structure

```
house_agent_ai/
├── main.py                     ← FastAPI server + all API endpoints
├── config.py                   ← Config file
├── pyproject.toml              ← uv dependency file
├── uv.lock                     ← uv lock file (exact versions)
├── .python-version             ← Python version lock (3.13)
├── Procfile                    ← Railway start command
├── railway.json                ← Railway deployment config
├── .env                        ← Local environment variables (not on GitHub)
├── .env.example                ← Template for env variables
├── .gitignore                  ← Files excluded from GitHub
├── README.md                   ← Project readme
├── credentials.json            ← Google service account key (not on GitHub)
├── gmail_credentials.json      ← Gmail OAuth credentials (not on GitHub)
├── gmail_token.json            ← Gmail OAuth token (not on GitHub)
│
├── frontend/                   ← Web Dashboard
│   ├── index.html              ← Dashboard page
│   ├── tickets.html            ← Tickets list page
│   ├── ticket_detail.html      ← Single ticket page
│   ├── knowledge_base.html     ← KB management page (split panel)
│   ├── calendar.html           ← Calendar page
│   ├── css/
│   │   └── style.css           ← Custom styles
│   └── js/
│       ├── api.js              ← All fetch() API calls + badge helpers
│       ├── dashboard.js        ← Dashboard logic
│       └── tickets.js          ← Tickets + modal logic
│
├── channels/
│   ├── __init__.py
│   ├── email_handler.py        ← Gmail read/send
│   ├── whatsapp_handler.py     ← Twilio WhatsApp send
│   └── call_handler.py         ← Call handling + Whisper transcription + SMS
│
├── ai/
│   ├── __init__.py
│   ├── classifier.py           ← GPT-4o-mini intent/priority/summary
│   ├── smart_reply.py          ← GPT-4o-mini reply generation
│   └── transcriber.py          ← (placeholder)
│
├── database/
│   ├── __init__.py
│   ├── sheets.py               ← Google Sheets connection + KB CRUD
│   ├── tickets.py              ← Create/find tickets
│   ├── messages.py             ← Log messages
│   └── knowledge_base.py       ← (placeholder)
│
├── services/
│   ├── __init__.py
│   ├── ticket_service.py       ← Main pipeline (classify → reply → log)
│   ├── reply_service.py        ← (placeholder)
│   ├── escalation.py           ← Escalation checker (every 30 mins)
│   └── scheduler.py            ← Offer slots + book appointments
│
├── cal/                        ← Named cal/ to avoid Python calendar conflict
│   ├── __init__.py
│   ├── google_calendar.py      ← Get slots, book events, block dates
│   ├── availability.py         ← (placeholder)
│   └── reminders.py            ← (placeholder)
│
└── webhooks/
    ��── __init__.py
    └── routes.py               ← WhatsApp + call webhook routes
```

---

## 11. Setup Checklist

### Local Setup
- [x] Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [x] Create project: `uv init house_agent_ai`
- [x] Create all folders including frontend/css and frontend/js
- [x] Install dependencies with uv add
- [x] Create Google Sheet "House Agent AI" with 4 tabs
- [x] Set up Google Cloud project and enable APIs
- [x] Download credentials.json from Google Cloud
- [x] Share Google Sheet with service account email
- [x] Share Google Calendar with service account email
- [x] Set up Gmail OAuth and generate gmail_token.json
- [x] Set up Twilio WhatsApp sandbox
- [x] Set up Twilio phone number for calls
- [x] Copy .env.example to .env and fill in all values
- [x] Run server: `source .venv/bin/activate && uvicorn main:app --reload --port 8000`
- [x] Verify dashboard at http://localhost:8000/dashboard
- [x] Test WhatsApp webhook with ngrok
- [x] Test email polling

### Deployment
- [x] Create Procfile
- [x] Create railway.json
- [x] Generate uv.lock
- [x] Push to GitHub: github.com/dajuctech/house-agent-ai
- [x] Deploy on Railway
- [x] Add all environment variables on Railway
- [x] Verify app is live: https://web-production-9d9db.up.railway.app

### Credentials on Railway
- [x] Convert credentials.json to GOOGLE_CREDENTIALS environment variable on Railway
- [x] Set GMAIL_TOKEN environment variable on Railway
- [x] Dashboard loading correctly on Railway
- [x] Update Twilio webhook URLs to Railway URL (not ngrok)
- [x] Get UK Local Individual regulatory bundle approved (John at Twilio) — wrong type for mobile
- [x] Submitted UK Mobile Individual bundle (2026-03-29) — awaiting approval
- [ ] Email John at Twilio to fast-track UK Mobile Individual bundle approval
- [ ] Once approved: buy +44 7588 332029 and assign Mobile Individual bundle
- [ ] Set Voice webhook on UK number: https://web-production-9d9db.up.railway.app/webhook/call
- [ ] Update TWILIO_PHONE_NUMBER env var on Railway to UK mobile number
- [ ] Test full end-to-end flow (email, WhatsApp, calls + SMS)

---

## 12. Milestones & Timeline

| Milestone | Phases | Status |
|-----------|--------|--------|
| Foundation | Phase 1 + 2 | ✅ Complete |
| AI Core | Phase 3 + 4 | ✅ Complete |
| Multi-channel | Phase 5 + 6 | ✅ Complete |
| Intelligence | Phase 7 + 8 | ✅ Complete |
| Frontend Dashboard | Phase 9 | ✅ Complete |
| Deployment | Phase 10 | ✅ Complete |
| Production Ready | Credentials on Railway | ✅ Complete |
| Mobile Responsive | All pages + modals | ✅ Complete |
| Ticket Management | Status update + filtering from dashboard | ✅ Complete |
| UK Phone Number | +44 7588 332029 — Mobile bundle under review | ⏳ Awaiting Twilio approval |

---

## 13. Known Issues & Fixes Applied

| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| `calendar` module conflict | Python has built-in `calendar` module | Renamed folder to `cal/` |
| Google Sheets API error | API not enabled in Google Cloud | Enabled in Google Cloud Console |
| `uv sync` installing globally | Virtual env not activated | Ran `source .venv/bin/activate` first |
| WhatsApp webhook not receiving | URL set in wrong Twilio field | Moved to "When a message comes in" field |
| Twilio number format wrong | Had `+whatsapp:` instead of `whatsapp:` | Fixed in .env |
| Google Calendar access denied | Service account can't invite attendees | Removed attendees, added email to description |
| `uvicorn: command not found` on Railway | Railway not using uv environment | Changed Procfile to `uv run uvicorn` |
| `uv.lock` not in project folder | uv workspace root set to home folder | Manually copied `~/uv.lock` to project |
| Git push rejected | GitHub had README, local didn't | Ran `git pull origin main --rebase` |
| `FileNotFoundError: credentials.json` on Railway | File doesn't exist on server | Updated `sheets.py` + `google_calendar.py` to read `GOOGLE_CREDENTIALS` env var |
| `json.decoder.JSONDecodeError` on Railway | `GOOGLE_CREDENTIALS` was empty or incorrectly pasted | Used `pbcopy` to copy single-line JSON and pasted via Raw Editor |
| Hamburger menu not working on mobile | `hidden md:hidden` conflicted with Tailwind flex classes | Used `style.display = 'none'/'block'` instead of Tailwind classes |
| Message content empty in ticket modal | Google Sheet column is `content` but frontend was looking for `body` | Fixed with `m.content \|\| m.body \|\| '—'` |
| Mobile modal Save button not accessible | Modal was `max-h-[90vh] overflow-y-auto` inside flex container — got cut off | Made outer overlay `overflow-y-auto` and inner card `my-4` |
| Mobile Save button tap not registering | `onclick` unreliable on mobile, overlay intercepting taps | Added `touchend` event listener + `event.stopPropagation()` on modal card |
| GitHub showing Claude as contributor | `Co-Authored-By: Claude` in commit messages | Recreated repo with squash commit — never add Co-Authored-By to future commits |
| UK Local number has no SMS capability | Twilio UK local numbers don't support SMS | Switched to UK Mobile number strategy |
| UK Local bundle wrong type for mobile | Local Individual bundle ≠ Mobile Individual bundle | Submitted new UK Mobile Individual bundle (2026-03-29) — awaiting approval |
| Trial account limited to 1 phone number | Twilio trial only allows one number | Released US number — will buy UK mobile number once bundle approved |

---

## 14. Out of Scope (v1.0)

- Multi-landlord support
- Payment processing
- Legal document generation
- Mobile app
- Two-way SMS conversations (SMS reply only, not receive)
- Real-time WebSocket updates on dashboard

---

## 15. Future Roadmap (v2.0)

- Real-time WebSocket dashboard updates
- Tenant portal (self-service)
- Two-way SMS conversations
- Automated rent reminders
- Contractor management system
- Property inspection reports
- Analytics and reporting charts
- Mobile app version
- Settings page (landlord details + system config)
- Messages page (all messages across all tickets)

---

*Document prepared for House Agent AI v1.0 — Daniel Jude — March 2026*
