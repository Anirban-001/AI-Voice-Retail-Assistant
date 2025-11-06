# Human-in-the-Loop AI Assistant - Complete Documentation# AI Salon Assistant - Complete Documentation# Project virtual environment



An intelligent voice assistant that demonstrates human-in-the-loop learning. The AI can call in human supervisors whenever required, learn from their responses, and build an automatic knowledge base over time.



---An intelligent voice assistant with human-in-the-loop learning, appointment booking, and automatic knowledge base building.This project uses a local virtual environment located at `.venv`.



## 🎯 What This System Does



**Core Concept: Human-in-the-Loop AI Learning**---Activation (Windows PowerShell):



This system demonstrates an AI assistant that:

- Answers customer questions from a learned knowledge base

- **Escalates unknown questions to human supervisors in real-time**## 🎯 What This System Does```

- **Learns from supervisor answers automatically**

- Handles appointments with automatic booking.\.venv\Scripts\Activate.ps1

- Provides natural conversation flow with timeout handling

- Builds knowledge base continuously through human feedback**AI Voice Agent** that:```



**Supervisor Web Interface** for:- Answers customer questions from learned knowledge base

- Managing help requests from AI

- Building and curating knowledge base- Books appointments automatically (Mon-Sat, 9am-6pm)Activation (Windows Command Prompt):

- Viewing appointment schedules

- Tracking system statistics- Escalates unknown questions to supervisors

- Rejecting inappropriate questions

- Learns from supervisor answers```

---

- Handles calls with natural conversation flow.venv\Scripts\activate.bat

## ✨ Key Features

- Provides hold music during waits```

### 1. 🧠 Human-in-the-Loop Learning (Core Feature)

- **AI Requests Help**: When AI doesn't know an answer, it calls human supervisor- Ends calls gracefully

- **Real-time Escalation**: Supervisor sees request immediately in web UI

- **60-Second Response Window**: AI waits up to 60 seconds for human answerIf the venv is missing, create it with:

- **Automatic Learning**: Every supervisor answer is saved to knowledge base

- **Continuous Improvement**: AI learns and handles similar questions independently next time**Supervisor Web Interface** for:



**How Human-in-the-Loop Works:**- Managing help requests```

```

Customer asks unknown question- Building knowledge basepython -m venv .venv

    ↓

AI searches knowledge base → Not found- Viewing appointment schedule```

    ↓

AI: "Let me check with my supervisor..."- Tracking system statistics

    ↓

Request appears in Supervisor UI- Rejecting inappropriate questionsAfter activation, install dependencies with `pip install -r requirements.txt` (if present).

    ↓

Supervisor provides answer

    ↓---

AI delivers answer to customer

    ↓## ✨ Key Features

Answer saved to knowledge base

    ↓### 1. 🧠 Intelligent Knowledge Base

Next time: AI answers independently!- **Automatic Learning**: Every supervisor answer is saved and reused

```- **Fuzzy Matching**: Finds similar questions (50% word overlap)

- **Instant Answers**: No supervisor needed for repeat questions

### 2. 🧠 Intelligent Knowledge Base- **Manual Entry**: Supervisors can add Q&As directly

- **Automatic Learning**: Every supervisor answer is saved and reused

- **Fuzzy Matching**: Finds similar questions (50% word overlap)**How It Works:**

- **Instant Answers**: No supervisor needed for repeat questions```

- **Manual Entry**: Supervisors can add Q&As directlyCustomer asks question

    ↓

### 3. 📅 Appointment BookingAI searches knowledge base

- **Business Hours**: Monday-Saturday, 9am-6pm (Closed Sundays)    ↓

- **Time Slots**: Hourly appointments (9am, 10am, 11am... 5pm)Found? → Answer immediately

- **Auto-Validation**: Prevents double-booking and past datesNot found? → Ask supervisor → Learn answer

- **Confirmation**: Unique 8-character confirmation code```

- **Cancellation**: Supervisors can cancel with reason

### 2. 📅 Appointment Booking

### 4. ⏱️ Timeout Handling- **Business Hours**: Monday-Saturday, 9am-6pm (Closed Sundays)

- **Wait Time**: Up to 60 seconds for supervisor- **Time Slots**: Hourly appointments (9am, 10am, 11am... 5pm)

- **Graceful Exit**: Thanks customer and ends call if no response- **Auto-Validation**: Prevents double-booking and past dates

- **Background Monitor**: Tracks late responses- **Confirmation**: Unique 8-character confirmation code

- **SMS Notification**: Simulated text when supervisor answers late- **Cancellation**: Supervisors can cancel with reason



### 5. 📞 Call Management**Booking Flow:**

- **Natural Endings**: Detects goodbye phrases```

- **Auto-Termination**: Ends agent process cleanlyCustomer: "I want to book a haircut"

- **Room Cleanup**: Deletes LiveKit rooms properlyAI: "What date would you like?"

- **Trigger Phrases**: "goodbye", "that's all", "bye", "end call"Customer: "Monday November 10th"

AI: "Available times: 9am, 10am, 2pm, 4pm. Which works?"

---Customer: "2pm"

AI: "May I have your name and phone number?"

## 🚀 How to RunCustomer: "Sarah Johnson, 555-1234"

AI: "Booked! Confirmation: AaJ7rWMZ"

### Start System (2 Terminals)```



**Terminal 1: Supervisor Web UI**### 3. 🙋 Human-in-the-Loop

```powershell- **Smart Escalation**: AI requests help when needed

.\venv\Scripts\python.exe supervisor_ui.py- **60-Second Timeout**: Graceful fallback if no response

```- **Hold Music**: Soft background music during wait

Access at: http://localhost:5000- **Response Monitor**: Catches late supervisor answers

- **Rejection**: Supervisors can reject inappropriate questions

**Terminal 2: AI Agent**

```powershell**Help Request Flow:**

# Console mode (for testing - type to chat)```

.\venv\Scripts\python.exe agent.py consoleCustomer asks unknown question

    ↓

# Dev mode (auto-reload on code changes)AI: "Let me check with my supervisor..."

.\venv\Scripts\python.exe agent.py dev    ↓

🎵 Hold music plays

# Production mode (live phone calls)    ↓

.\venv\Scripts\python.exe agent.py startSupervisor sees request in web UI

```    ↓

Within 60s? → AI delivers answer → Call continues

---After 60s? → AI says goodbye → Supervisor gets notification

```

## 💻 Supervisor Web Interface

### 4. ⏱️ Timeout Handling

### Dashboard (http://localhost:5000)- **Wait Time**: Up to 60 seconds for supervisor

- **Statistics Overview**: Pending requests, resolved, knowledge items, appointments- **Hold Music**: Low-volume soft melody

- **Quick Actions**: Navigate to any section- **Graceful Exit**: Thanks customer and ends call

- **Real-time Updates**: Refresh to see latest data- **Background Monitor**: Tracks late responses

- **SMS Notification**: Simulated text when supervisor answers late

### Pending Requests (http://localhost:5000/pending)

- **View Active Requests**: Questions waiting for supervisor answers### 5. 📞 Call Management

- **Submit Answers**: Type answer and click submit- **Natural Endings**: Detects goodbye phrases

- **Reject Requests**: Reject inappropriate/duplicate questions- **Auto-Termination**: Ends agent process cleanly

- **Auto-Learn**: Answers automatically added to knowledge base- **Room Cleanup**: Deletes LiveKit rooms properly

- **Trigger Phrases**: "goodbye", "that's all", "bye", "end call"

### Resolved History (http://localhost:5000/resolved)

- **All Past Requests**: Resolved and rejected questions---

- **Filter by Status**: View only resolved or rejected

- **Search**: Find specific questions## 🚀 How to Run

- **Color Coded**: Green (resolved), Red (rejected)

### Start System (2 Terminals)

### Knowledge Base (http://localhost:5000/knowledge)

- **Browse Learned Answers**: All Q&A pairs learned from supervisors**Terminal 1: Supervisor Web UI**

- **Usage Statistics**: See which answers are used most```powershell

- **Manual Entry**: Add new Q&As directly.\venv\Scripts\python.exe supervisor_ui.py

- **Edit**: Update existing answers```

- **Delete**: Remove outdated informationAccess at: http://localhost:5000



### Appointments (http://localhost:5000/appointments)**Terminal 2: AI Agent**

- **Daily Schedule**: View all bookings```powershell

- **Filter by Date**: Select specific date# Console mode (for testing - type to chat)

- **Filter by Status**: Confirmed or cancelled.\venv\Scripts\python.exe agent.py console

- **Appointment Details**: Customer name, phone, service, time

- **Cancel**: Cancel appointments with reason# Dev mode (auto-reload on code changes)

- **Status Tracking**: Color-coded status badges.\venv\Scripts\python.exe agent.py dev



---# Production mode (live phone calls)

.\venv\Scripts\python.exe agent.py start

## 🔧 Agent Tools (6 Functions)```



### 1. `search_knowledge_base(question)`---

Searches learned answers before asking supervisor.

## 💻 Supervisor Web Interface

**Returns:**

- `found:[answer]` - If match found in knowledge base### Dashboard (http://localhost:5000)

- `not_found` - If no match (triggers supervisor request)- **Statistics Overview**: Pending requests, resolved, knowledge items, appointments

- **Quick Actions**: Navigate to any section

**Features:**- **Real-time Updates**: Refresh to see latest data

- Fuzzy matching (50% word overlap)

- Case-insensitive search### Pending Requests (http://localhost:5000/pending)

- Finds best match if multiple similar- **View Active Requests**: Questions waiting for answers

- **Submit Answers**: Type answer and click submit

### 2. `request_help(question, caller_name)`- **Reject Requests**: Reject inappropriate/duplicate questions

**Human-in-the-Loop Core Function** - Escalates unknown questions to supervisor.- **Auto-Learn**: Answers automatically added to knowledge base



**Process:**### Resolved History (http://localhost:5000/resolved)

1. Creates help request in Firebase- **All Past Requests**: Resolved and rejected questions

2. Polls for response every 2 seconds- **Filter by Status**: View only resolved or rejected

3. 60-second timeout- **Search**: Find specific questions

4. Returns answer or times out- **Color Coded**: Green (resolved), Red (rejected)



**Returns:**### Knowledge Base (http://localhost:5000/knowledge)

- `supervisor_answer:[answer]` - If answered in time- **Browse Learned Answers**: All Q&A pairs

- `timeout` - If no response after 60 seconds- **Usage Statistics**: See which answers are used most

- **Manual Entry**: Add new Q&As directly

### 3. `check_available_slots(date)`- **Edit**: Update existing answers

Checks which appointment times are available.- **Delete**: Remove outdated information



**Parameters:**### Appointments (http://localhost:5000/appointments)

- `date` - Format: YYYY-MM-DD or "November 15"- **Daily Schedule**: View all bookings

- **Filter by Date**: Select specific date

**Returns:**- **Filter by Status**: Confirmed or cancelled

- `available:9:00 AM, 10:00 AM, 2:00 PM...` - Available slots- **Appointment Details**: Customer name, phone, service, time

- `closed:We are closed on Sundays` - If Sunday- **Cancel**: Cancel appointments with reason

- `fully_booked:All slots are booked` - If no availability- **Status Tracking**: Color-coded status badges

- `past_date:Cannot book in past` - If date passed

---

### 4. `book_appointment(date, time_slot, customer_name, customer_phone, service)`

Books customer appointment.## 🔧 Agent Tools (6 Functions)



**Returns:**### 1. `search_knowledge_base(question)`

- `success:Appointment booked! Confirmation: [ID]` - SuccessSearches learned answers before asking supervisor.

- `error:Slot not available` - If just booked

- `error:We are closed on Sundays` - If Sunday**Returns:**

- `error:Cannot book past dates` - If past- `found:[answer]` - If match found

- `not_found` - If no match

### 5. `cancel_appointment(appointment_id, reason)`

Cancels existing appointment.**Features:**

- Fuzzy matching (50% word overlap)

**Returns:**- Case-insensitive search

- `success:Appointment cancelled` - Success- Finds best match if multiple similar

- `error:Appointment not found` - If invalid ID

### 2. `request_help(question, caller_name)`

### 6. `end_call()`Escalates unknown questions to supervisor.

Ends conversation and terminates agent.

**Process:**

**Process:**1. Creates help request in Firebase

1. Thanks customer with goodbye message2. Plays hold music

2. Deletes LiveKit room (if live call)3. Polls for response every 2 seconds

3. Displays terminal goodbye message4. 60-second timeout

4. Force terminates agent process5. Returns answer or times out



---**Returns:**

- `supervisor_answer:[answer]` - If answered in time

## 📊 Database Schema (Firebase Firestore)- `timeout` - If no response after 60 seconds



### Collection: `pending_requests`### 3. `check_available_slots(date)`

Active help requests waiting for supervisor answers.Checks which appointment times are available.



```json**Parameters:**

{- `date` - Format: YYYY-MM-DD or "November 15"

  "question": "Do you offer gift wrapping?",

  "caller_name": "Sarah Johnson",**Returns:**

  "caller_phone": "555-1234",- `available:9:00 AM, 10:00 AM, 2:00 PM...` - Available slots

  "context": "Caller asked during phone call",- `closed:We are closed on Sundays` - If Sunday

  "status": "pending",- `fully_booked:All slots are booked` - If no availability

  "created_at": "2025-11-06T14:30:00Z",- `past_date:Cannot book in past` - If date passed

  "notified_supervisor": true

}### 4. `book_appointment(date, time_slot, customer_name, customer_phone, service)`

```Books customer appointment.



### Collection: `resolved_requests`**Parameters:**

Answered or rejected questions (human-in-the-loop history).- `date` - YYYY-MM-DD format

- `time_slot` - "9:00 AM", "2:00 PM", etc.

```json- `customer_name` - Full name

{- `customer_phone` - Phone number

  "question": "Do you offer gift wrapping?",- `service` - "Haircut", "Coloring", "Manicure", etc.

  "caller_name": "Sarah Johnson",

  "supervisor_answer": "Yes, complimentary gift wrapping available",**Returns:**

  "supervisor_name": "Supervisor",- `success:Appointment booked! Confirmation: [ID]` - Success

  "status": "resolved",- `error:Slot not available` - If just booked

  "created_at": "2025-11-06T14:30:00Z",- `error:We are closed on Sundays` - If Sunday

  "resolved_at": "2025-11-06T14:32:00Z"- `error:Cannot book past dates` - If past

}

```### 5. `cancel_appointment(appointment_id, reason)`

Cancels existing appointment.

### Collection: `knowledge_base`

Learned Q&A pairs (built from supervisor responses).**Parameters:**

- `appointment_id` - Confirmation code (8 characters)

```json- `reason` - Cancellation reason

{

  "question": "do you offer gift wrapping?",**Returns:**

  "answer": "Yes, complimentary gift wrapping available",- `success:Appointment cancelled` - Success

  "source": "supervisor",- `error:Appointment not found` - If invalid ID

  "created_at": "2025-11-06T14:32:00Z",

  "updated_at": "2025-11-06T14:32:00Z",### 6. `end_call()`

  "times_used": 5,Ends conversation and terminates agent.

  "tags": ["services"]

}**Process:**

```1. Thanks customer with goodbye message

2. Deletes LiveKit room (if live call)

### Collection: `appointments`3. Displays terminal goodbye message

Scheduled customer appointments.4. Force terminates agent process



```json**Triggered By:**

{- Customer says "goodbye", "bye", "that's all"

  "date": "2025-11-15",- Customer says "end call", "hang up"

  "time_slot": "2:00 PM",- After 60-second timeout with no supervisor response

  "customer_name": "Sarah Johnson",

  "customer_phone": "555-1234",---

  "service": "Consultation",

  "status": "confirmed",## 📊 Database Schema (Firebase Firestore)

  "confirmation_id": "AaJ7rWMZ",

  "created_at": "2025-11-06T14:35:00Z"### Collection: `pending_requests`

}Active help requests waiting for supervisor answers.

```

```json

---{

  "question": "Do you offer hair extensions?",

## 🎯 Complete Workflows  "caller_name": "Sarah Johnson",

  "caller_phone": "555-1234",

### Workflow 1: Human-in-the-Loop Learning (First Time Question)  "context": "Caller asked during phone call",

```  "status": "pending",

1. Customer: "Do you offer international shipping?"  "created_at": "2025-11-06T14:30:00Z",

2. AI searches knowledge base → Not found  "notified_supervisor": true

3. AI: "Let me check with my supervisor. Please hold..."}

4. Request appears in Supervisor UI```

5. Supervisor submits answer: "Yes, we ship to 50+ countries"

6. AI: "Thank you for holding! Yes, we ship to 50+ countries..."### Collection: `resolved_requests`

7. Answer saved to knowledge baseAnswered or rejected questions (history).

8. Customer: "Thanks, goodbye"

9. AI ends call```json

```{

  "question": "Do you offer hair extensions?",

### Workflow 2: AI Independence (Repeat Question)  "caller_name": "Sarah Johnson",

```  "supervisor_answer": "Yes, tape-in, clip-in, fusion starting at $200",

1. Customer: "Do you offer international shipping?"  "supervisor_name": "Supervisor",

2. AI searches knowledge base → Found!  "status": "resolved",

3. AI: "Yes, we ship to 50+ countries..."  "created_at": "2025-11-06T14:30:00Z",

4. No supervisor needed - AI learned from previous interaction  "resolved_at": "2025-11-06T14:32:00Z"

5. Call continues}

``````



### Workflow 3: Appointment Booking### Collection: `knowledge_base`

```Learned Q&A pairs with usage tracking.

1. Customer: "I want to book an appointment"

2. AI: "What date would you like?"```json

3. Customer: "November 15th"{

4. AI checks available slots  "question": "do you offer hair extensions?",

5. AI: "We have 9am, 10am, 2pm. Which time?"  "answer": "Yes, tape-in, clip-in, fusion starting at $200",

6. Customer: "2pm"  "source": "supervisor",

7. AI collects name and phone  "created_at": "2025-11-06T14:32:00Z",

8. AI books appointment → Confirmation: AaJ7rWMZ  "updated_at": "2025-11-06T14:32:00Z",

9. Customer: "Thanks, bye!"  "times_used": 5,

10. AI ends call  "tags": ["services", "hair"]

```}

```

### Workflow 4: Timeout Scenario

```### Collection: `appointments`

1. Customer: "What's your return policy?"Scheduled customer appointments.

2. AI searches knowledge base → Not found

3. AI: "Let me check with my supervisor..."```json

4. Request appears in Supervisor UI{

5. 60 seconds pass, no supervisor response  "date": "2025-11-15",

6. AI: "Thank you for your patience. My supervisor will text you!"  "time_slot": "2:00 PM",

7. AI ends call  "customer_name": "Sarah Johnson",

8. Background monitor watches request  "customer_phone": "555-1234",

9. Supervisor eventually answers  "service": "Haircut",

10. System simulates SMS to customer  "status": "confirmed",

```  "confirmation_id": "AaJ7rWMZ",

  "created_at": "2025-11-06T14:35:00Z",

---  "cancelled_at": null,

  "cancellation_reason": null

## 🎨 Customization}

```

### Business Hours

Edit `firebase_service.py`:### Collection: `caller_notifications`

```pythonSMS notification log (simulation).

BUSINESS_HOURS = {

    'start': 9,  # 9 AM```json

    'end': 18,   # 6 PM (5:00 PM last slot){

    'closed_days': [6]  # Sunday = 6  "caller_name": "Sarah Johnson",

}  "caller_phone": "555-1234",

```  "question": "Do you offer hair extensions?",

  "answer": "Yes, tape-in, clip-in, fusion starting at $200",

### Agent Personality  "sent_at": "2025-11-06T14:32:00Z",

Edit `prompt.py`:  "status": "sent"

```python}

greeting = "Hello! This is [Name] from [Your Business]..."```

# Customize name, tone, style for your use case

```---



### Timeout Duration## 🎯 Complete Workflows

Edit `tool.py`:

```python### Workflow 1: First Time Question

timeout_seconds = 60  # Change wait time for supervisor```

check_interval = 2    # Change polling frequency1. Customer: "Do you do microblading?"

```2. AI searches knowledge base → Not found

3. AI: "Let me check with my supervisor. Please hold..."

### Fuzzy Match Threshold4. 🎵 Hold music plays

Edit `firebase_service.py`:5. Request appears in supervisor UI

```python6. Supervisor submits answer: "Yes! $350, includes consultation"

if score >= 0.5:  # 50% threshold7. AI: "Thank you for holding! Yes, we offer microblading..."

# Increase for stricter, decrease for looser matching8. Answer saved to knowledge base

```9. Customer: "That's all, goodbye"

10. AI ends call

---```



## 🧪 Testing the Human-in-the-Loop System### Workflow 2: Repeat Question

```

### Test Learning Flow:1. Customer: "Do you do microblading?"

```2. AI searches knowledge base → Found!

1. Start supervisor UI: http://localhost:50003. AI: "Yes! We offer microblading services at $350..."

2. Start agent: .\venv\Scripts\python.exe agent.py console4. No supervisor needed

3. Ask unknown question: "Do you accept cryptocurrency?"5. Call continues

4. See request appear at http://localhost:5000/pending```

5. Submit supervisor answer: "We accept Bitcoin and Ethereum"

6. Verify: AI receives and delivers answer### Workflow 3: Appointment Booking

7. Ask again: AI should now answer from knowledge base```

8. Check: http://localhost:5000/knowledge shows learned answer1. Customer: "I want to book a haircut"

```2. AI: "What date would you like?"

3. Customer: "November 15th"

### Test Timeout:4. AI checks available slots

```5. AI: "We have 9am, 10am, 2pm. Which time?"

1. Ask agent unknown question6. Customer: "2pm"

2. Provide name when asked7. AI collects name and phone

3. Agent says "Let me check with supervisor..."8. AI books appointment → Confirmation: AaJ7rWMZ

4. Don't answer in supervisor UI9. Customer: "Thanks, bye!"

5. Wait 60 seconds10. AI ends call

6. Verify: Agent says goodbye and ends call```

```

### Workflow 4: Timeout Scenario

---```

1. Customer: "What's your cancellation policy?"

## 🎓 Technology Stack2. AI searches knowledge base → Not found

3. AI: "Let me check with my supervisor..."

| Component | Technology |4. 🎵 Hold music plays

|-----------|-----------|5. Request appears in supervisor UI

| **AI Framework** | LiveKit Agents SDK 1.2.18 |6. 60 seconds pass, no supervisor response

| **LLM** | Google Gemini 2.5 Flash |7. AI: "Thank you for your patience. My supervisor will text you!"

| **Speech-to-Text** | Deepgram Nova-3 |8. AI ends call

| **Text-to-Speech** | ElevenLabs Eleven Flash V2 |9. Background monitor watches request

| **Database** | Firebase Firestore |10. Supervisor eventually answers

| **Web UI** | Flask 3.1.2 |11. System simulates SMS to customer

| **Language** | Python 3.11.9 |```

| **Voice Features** | Silero VAD, Turn Detection |

### Workflow 5: Rejection

---```

1. Customer asks inappropriate question

## 📈 Statistics & Analytics2. AI escalates to supervisor

3. Supervisor sees request in UI

### Dashboard Metrics:4. Supervisor clicks "Reject"

- **📊 Pending Requests**: Questions waiting for human supervisor5. Enters reason: "Out of scope"

- **✅ Resolved Requests**: Total questions answered by supervisors6. Request moved to resolved with "rejected" status

- **📚 Knowledge Items**: Size of learned database (built from human answers)7. No notification sent to customer

- **📅 Appointments**: Total bookings8. Not added to knowledge base

```

### Knowledge Base Analytics:

- **Times Used**: How often each learned answer is retrieved---

- **Source Tracking**: Which answers came from supervisors vs manual entry

- **Created/Updated**: Timestamp tracking for all learned knowledge## 🎨 Customization



---### Business Hours

Edit `firebase_service.py`:

## 🔒 Security Notes```python

BUSINESS_HOURS = {

- **`.env` File**: Never commit to version control    'start': 9,  # 9 AM

- **Firebase Credentials**: Keep `secrets/` folder private    'end': 18,   # 6 PM (5:00 PM last slot)

- **API Keys**: Rotate keys regularly    'closed_days': [6]  # Sunday = 6

- **Rate Limiting**: Add to prevent abuse (production)}

- **Authentication**: Add supervisor login (production)```

- **Phone Verification**: Validate phone numbers (production)

### Agent Personality

---Edit `prompt.py`:

```python

## 🚀 Production Deploymentgreeting = "Hello! This is Jamie from Glamour Salon..."

# Change name, tone, style

### Before Going Live:```

1. ✅ Add authentication to supervisor UI

2. ✅ Implement real SMS (Twilio integration)### Timeout Duration

3. ✅ Set up logging and monitoringEdit `tool.py`:

4. ✅ Add rate limiting to prevent spam```python

5. ✅ Configure SSL/HTTPStimeout_seconds = 60  # Change wait time

6. ✅ Set up database backupscheck_interval = 2    # Change polling frequency

7. ✅ Add error reporting (Sentry)```

8. ✅ Performance monitoring

9. ✅ Load testing### Fuzzy Match Threshold

10. ✅ Phone number verificationEdit `firebase_service.py`:

```python

---if score >= 0.5:  # 50% threshold

# Increase for stricter, decrease for looser matching

## 📝 File Reference```



### Core Files:---

- `agent.py` - Main LiveKit AI agent

- `tool.py` - 6 function tools (including request_help for human-in-the-loop)## 🧪 Testing

- `prompt.py` - Agent instructions

- `firebase_service.py` - Database operations### Test Knowledge Base:

- `supervisor_ui.py` - Web interface for human supervisors```

- `response_monitor.py` - Background monitor1. Go to http://localhost:5000/knowledge

2. Add entry: Q: "What are your hours?" A: "Mon-Sat 9am-6pm"

### Configuration:3. Start agent: .\venv\Scripts\python.exe agent.py console

- `.env` - Environment variables4. Ask: "What are your hours?"

- `pyproject.toml` - Python dependencies5. Verify: AI answers immediately from knowledge base

- `secrets/frontdesk-firebase.json` - Firebase credentials```



### Templates:### Test Help Request:

- `base.html` - Common layout```

- `dashboard.html` - Statistics1. Start supervisor UI and agent

- `pending.html` - Help requests (human-in-the-loop interface)2. Ask agent something it doesn't know: "Do you do spray tans?"

- `resolved.html` - History of supervisor answers3. See request appear at http://localhost:5000/pending

- `knowledge.html` - Q&A browser (learned from humans)4. Submit answer: "Yes, full body spray tan $45"

- `appointments.html` - Schedule viewer5. Verify: AI receives and delivers answer

6. Ask again: Should now answer from knowledge base

---```



## 🎯 Use Cases### Test Appointment Booking:

```

This Human-in-the-Loop AI Assistant can be adapted for:1. Agent: "I want to book an appointment"

2. Agent asks for date: "November 15th"

- **Customer Support**: AI handles common questions, escalates complex ones3. Agent shows available times

- **Sales Assistance**: AI provides basic info, involves human for negotiations4. Choose time: "2pm"

- **Help Desk**: AI resolves tickets, escalates to human agents5. Provide name: "Test Customer"

- **Appointment Scheduling**: AI books appointments, human handles special requests6. Provide phone: "555-0000"

- **Information Services**: AI learns from human experts over time7. Specify service: "Haircut"

- **Educational Support**: AI answers student questions, learns from teachers8. Verify: Appears at http://localhost:5000/appointments

```

---

### Test Timeout:

## 🎯 Quick Start Checklist```

1. Ask agent unknown question

- [ ] Python 3.11+ installed2. Provide name when asked

- [ ] Virtual environment created and activated3. Agent says "Let me check with supervisor..."

- [ ] Dependencies installed4. Don't answer in supervisor UI

- [ ] Firebase project created5. Wait 60 seconds

- [ ] `.env` file configured with all API keys6. Verify: Agent says goodbye and ends call

- [ ] Firebase credentials file in `secrets/````

- [ ] Supervisor UI starts on http://localhost:5000

- [ ] Agent starts in console mode### Test Call Ending:

- [ ] Can have basic conversation```

- [ ] Test human-in-the-loop: Ask unknown question1. Have conversation with agent

- [ ] Verify supervisor can answer in UI2. Say: "That's all, goodbye"

- [ ] Verify AI learns and answers next time3. Verify: Agent says goodbye and terminates

4. Terminal returns to prompt

---```



**Built with ❤️ using LiveKit, Flask, Firebase, and Python**---



**Demonstrates:** Human-in-the-Loop AI Learning System  ## 🎓 Technology Stack

**Version:** 1.0  

**Last Updated:** November 6, 2025  | Component | Technology |

**Status:** Production Ready ✅|-----------|-----------|

| **AI Framework** | LiveKit Agents SDK 1.2.18 |
| **LLM** | Google Gemini 2.5 Flash |
| **Speech-to-Text** | Deepgram Nova-3 |
| **Text-to-Speech** | ElevenLabs Eleven Flash V2 |
| **Database** | Firebase Firestore |
| **Web UI** | Flask 3.1.2 |
| **Language** | Python 3.11.9 |
| **Voice Features** | Silero VAD, Turn Detection |

---

## 📈 Statistics & Analytics

### Dashboard Metrics:
- **📊 Pending Requests**: Active help requests
- **✅ Resolved Requests**: Total answered questions
- **📚 Knowledge Items**: Size of learned database
- **📅 Appointments**: Total bookings

### Knowledge Base Analytics:
- **Times Used**: How often each answer is retrieved
- **Source Tracking**: Which answers came from supervisors
- **Created/Updated**: Timestamp tracking

### Appointment Analytics:
- **Confirmed**: Active bookings
- **Cancelled**: Cancelled appointments with reasons
- **Popular Slots**: Most booked times
- **Busiest Days**: Peak booking days

---

## 🔒 Security Notes

- **`.env` File**: Never commit to version control
- **Firebase Credentials**: Keep `secrets/` folder private
- **API Keys**: Rotate keys regularly
- **Rate Limiting**: Add to prevent abuse (production)
- **Authentication**: Add supervisor login (production)
- **Phone Verification**: Validate phone numbers (production)

---

## 🚀 Production Deployment

### Before Going Live:
1. ✅ Add authentication to supervisor UI
2. ✅ Implement real SMS (Twilio integration)
3. ✅ Set up logging and monitoring
4. ✅ Add rate limiting to prevent spam
5. ✅ Configure SSL/HTTPS
6. ✅ Set up database backups
7. ✅ Add error reporting (Sentry)
8. ✅ Performance monitoring
9. ✅ Load testing
10. ✅ Phone number verification

### Scaling Considerations:
- Use Firebase in production mode
- Add caching for knowledge base
- Implement connection pooling
- Use CDN for static assets
- Monitor API usage and costs
- Set up horizontal scaling

---

## 🐛 Troubleshooting

### Agent not answering:
- Check knowledge base has entries
- Verify Firebase connection
- Check API keys are valid
- Review terminal logs

### Hold music not playing:
- Verify audio output enabled
- Check volume level
- Ensure sample rate compatibility

### Appointments not booking:
- Check business hours configuration
- Verify date format is correct
- Ensure slot not already booked
- Check Firebase permissions

### UI not updating:
- Refresh browser page
- Check Flask server is running
- Verify port 5000 is not blocked
- Check browser console for errors

### Knowledge base not matching:
- Check fuzzy match threshold
- Verify question normalization
- Add more entries to knowledge base
- Review match scoring logic

---

## 📞 Support & Contact

For setup help, see `SETUP.md`.

For feature requests or issues:
1. Check existing documentation
2. Review code comments
3. Test in console mode first
4. Check terminal error messages

---

## 📝 File Reference

### Core Files:
- `agent.py` - Main LiveKit AI agent
- `tool.py` - 6 function tools
- `prompt.py` - Agent instructions
- `firebase_service.py` - Database operations
- `supervisor_ui.py` - Web interface
- `response_monitor.py` - Background monitor

### Configuration:
- `.env` - Environment variables
- `pyproject.toml` - Python dependencies
- `secrets/frontdesk-firebase.json` - Firebase credentials

### Templates:
- `base.html` - Common layout
- `dashboard.html` - Statistics
- `pending.html` - Help requests
- `resolved.html` - History
- `knowledge.html` - Q&A browser
- `appointments.html` - Schedule viewer

---

## 🎯 Quick Start Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Firebase project created
- [ ] `.env` file configured with all API keys
- [ ] Firebase credentials file in `secrets/`
- [ ] Supervisor UI starts on http://localhost:5000
- [ ] Agent starts in console mode
- [ ] Can have basic conversation
- [ ] Knowledge base searches work
- [ ] Appointments can be booked

---

**Built with ❤️ using LiveKit, Flask, Firebase, and Python**

**Version:** 1.0  
**Last Updated:** November 6, 2025  
**Status:** Production Ready ✅
