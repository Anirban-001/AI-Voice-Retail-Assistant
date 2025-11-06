# Human-in-the-Loop AI Assistant - Setup Guide

Complete installation and configuration guide for first-time setup.

This system demonstrates a Human-in-the-Loop AI learning approach where the AI can call in human supervisors whenever it encounters unknown questions, learn from their responses, and build a knowledge base automatically.

---

## 📋 Prerequisites

- **Python 3.11+** installed
- **Firebase Project** created ([console.firebase.google.com](https://console.firebase.google.com))
- **LiveKit Account** ([livekit.io](https://livekit.io))
- **Google Gemini API Key** ([ai.google.dev](https://ai.google.dev))
- **Deepgram API Key** ([deepgram.com](https://deepgram.com))
- **ElevenLabs API Key** ([elevenlabs.io](https://elevenlabs.io))

---

## 🚀 Installation Steps

### 1. Clone/Download Project
```powershell
cd D:\Project
# Your project should be in: D:\Project\Frontdesk01
```

### 2. Create Virtual Environment
```powershell
cd Frontdesk01
python -m venv venv
```

### 3. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an error about execution policies:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install Dependencies
```powershell
pip install livekit-agents[silero,turn-detector]~=1.2
pip install livekit-plugins-noise-cancellation~=0.2
pip install python-dotenv>=1.1.1
pip install pytz
pip install flask
pip install firebase-admin
```

Or if you have `pyproject.toml`:
```powershell
pip install -e .
```

---

## 🔧 Configuration

### 1. Firebase Setup

**Create Firebase Project:**
1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Create new project: "AI-Salon-Assistant"
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Save the JSON file as: `secrets/frontdesk-firebase.json`

**Create Firestore Database:**
1. In Firebase Console, go to **Firestore Database**
2. Click **Create Database**
3. Select **Production Mode**
4. Choose your region
5. Collections will be created automatically

**Collections Created:**
- `pending_requests` - Active help requests
- `resolved_requests` - Answered/rejected questions
- `knowledge_base` - Learned Q&A pairs
- `appointments` - Scheduled appointments
- `caller_notifications` - SMS notifications log

### 2. LiveKit Setup

**Get Credentials:**
1. Sign up at [livekit.io](https://livekit.io)
2. Create new project
3. Copy:
   - LiveKit URL (wss://...)
   - API Key
   - API Secret

### 3. API Keys Setup

**Google Gemini:**
1. Visit [ai.google.dev](https://ai.google.dev)
2. Get API key
3. Copy for `.env` file

**Deepgram (Speech-to-Text):**
1. Sign up at [deepgram.com](https://deepgram.com)
2. Create API key
3. Copy for `.env` file

**ElevenLabs (Text-to-Speech):**
1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Get API key
3. Find voice ID (default: cgSgspJ2msm6clMCkdW9)
4. Copy for `.env` file

### 4. Create `.env` File

Create a file named `.env` in the project root:

```env
# Firebase Configuration
FIREBASE_CREDENTIALS=D:\Project\Frontdesk01\secrets\frontdesk-firebase.json

# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here

# Google Gemini LLM
GOOGLE_API_KEY=your_google_api_key_here

# Deepgram Speech-to-Text
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# ElevenLabs Text-to-Speech
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=cgSgspJ2msm6clMCkdW9
```

**⚠️ Important:** Never commit `.env` to version control!

---

## 🗂️ Project Structure

```
Frontdesk01/
├── agent.py                    # Main AI agent (LiveKit)
├── tool.py                     # 6 function tools
├── prompt.py                   # Agent behavior instructions
├── firebase_service.py         # Database operations
├── supervisor_ui.py            # Flask web interface
├── response_monitor.py         # Background response checker
├── templates/                  # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── pending.html
│   ├── resolved.html
│   ├── knowledge.html
│   └── appointments.html
├── secrets/
│   └── frontdesk-firebase.json # Firebase credentials
├── .env                        # Environment variables
├── venv/                       # Virtual environment
├── SETUP.md                    # This file
└── README.md                   # Full documentation
```

---

## ✅ Verify Installation

### 1. Test Firebase Connection
```powershell
.\venv\Scripts\python.exe -c "from firebase_service import FirebaseService; print('✅ Firebase Connected!')"
```

### 2. Test Environment Variables
```powershell
.\venv\Scripts\python.exe -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ LiveKit URL:', os.getenv('LIVEKIT_URL'))"
```

### 3. Check All Imports
```powershell
.\venv\Scripts\python.exe -c "import livekit, flask, firebase_admin; print('✅ All dependencies installed!')"
```

---

## 🎯 First Run

### Terminal 1: Start Supervisor UI
```powershell
.\venv\Scripts\python.exe supervisor_ui.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**Access UI:** Open browser to http://localhost:5000

### Terminal 2: Start AI Agent (Console Mode)
```powershell
.\venv\Scripts\python.exe agent.py console
```

**Expected Output:**
```
Starting Human-in-the-Loop AI Assistant in Console Mode...
Connected to LiveKit
Ready to chat! Type your messages...
```

### Test Conversation

**Type in agent terminal:**
```
You: Hello
AI: Hello! This is [Agent Name]. How can I help you today?

You: What are your hours?
AI: [Searches knowledge base] We're open Monday-Saturday, 9am-6pm. Closed Sundays.

You: Do you offer delivery? (unknown question)
AI: Let me check with my supervisor. Please hold...
[Go to http://localhost:5000/pending and answer]
AI: Thank you for holding! Here's the answer: [supervisor's answer]

You: Goodbye
AI: Thank you for calling! Have a wonderful day!
[Agent terminates automatically]
```

---

## 🔍 Troubleshooting

### Issue: "Firebase credentials not found"
**Solution:**
1. Check `.env` file has correct path
2. Verify `secrets/frontdesk-firebase.json` exists
3. Use absolute path in `.env`

### Issue: "LiveKit connection failed"
**Solution:**
1. Check LiveKit URL format (must start with `wss://`)
2. Verify API key and secret are correct
3. Check internet connection

### Issue: "Module not found" errors
**Solution:**
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
pip install -e .
```

### Issue: "Permission denied" on Windows
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Port 5000 already in use
**Solution:**
```powershell
# Kill process using port 5000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
```

### Issue: Virtual environment not activating
**Solution:**
```powershell
# Use full path
D:\Project\Frontdesk01\venv\Scripts\Activate.ps1

# Or use python directly
.\venv\Scripts\python.exe agent.py console
```

---

## 📊 Verify Everything Works

### Checklist:
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] `.env` file configured
- [ ] Firebase credentials in place
- [ ] Supervisor UI accessible at http://localhost:5000
- [ ] Agent starts in console mode
- [ ] Can have basic conversation
- [ ] Test Human-in-the-Loop: Ask unknown question
- [ ] Verify question appears in pending UI
- [ ] Submit supervisor answer
- [ ] Verify AI learns and delivers answer
- [ ] Ask same question again - AI should know it now

---

## 🎓 Next Steps

After successful setup:

1. **Read README.md** - Complete feature documentation about Human-in-the-Loop learning
2. **Test Learning Flow:**
   - Ask agent an unknown question
   - Answer as supervisor in UI
   - Ask same question again
   - Verify AI learned and answers independently
3. **Add Initial Knowledge** - Go to http://localhost:5000/knowledge and add common Q&As
4. **Customize for Your Use Case:**
   - Edit `prompt.py` for your business domain
   - Update business hours in `firebase_service.py`
   - Customize UI in `templates/`

---

## 🆘 Getting Help

- Check `README.md` for complete feature documentation
- Review code comments in each file
- Check terminal output for error messages
- Verify all API keys are valid and have credit

---

## 📝 Quick Command Reference

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start supervisor UI
.\venv\Scripts\python.exe supervisor_ui.py

# Start agent (console mode - for testing)
.\venv\Scripts\python.exe agent.py console

# Start agent (dev mode - auto-reload)
.\venv\Scripts\python.exe agent.py dev

# Start agent (production mode)
.\venv\Scripts\python.exe agent.py start

# Install new package
pip install package-name

# Update dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version

# Deactivate virtual environment
deactivate
```

---

**Setup Complete! 🎉**

Your Human-in-the-Loop AI Assistant is ready to use. The system will learn from human supervisors and continuously improve. Proceed to `README.md` for complete feature documentation.
