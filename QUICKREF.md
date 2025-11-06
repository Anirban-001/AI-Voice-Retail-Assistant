# Quick Reference Card - Human-in-the-Loop AI Assistant

## 📂 Project Overview

**System Purpose:** Demonstrates Human-in-the-Loop AI learning where the AI can call in human supervisors whenever needed, learn from their responses, and build a knowledge base automatically.

## 📂 Project Files (Clean Structure)

### 🐍 Core Python Files (6)
1. **agent.py** (1.6 KB) - AI agent entry point
2. **tool.py** (9.6 KB) - 6 function tools
3. **prompt.py** (9.2 KB) - Agent instructions
4. **firebase_service.py** (21.8 KB) - Database operations
5. **supervisor_ui.py** (4.4 KB) - Web interface
6. **response_monitor.py** (3.3 KB) - Background monitor

### 📚 Documentation (2)
1. **SETUP.md** (9 KB) - Installation & configuration guide
2. **README.md** (18 KB) - Complete feature documentation

### ⚙️ Configuration (3)
1. `.env` - API keys and environment variables
2. `pyproject.toml` - Python dependencies
3. `.gitignore` - Git ignore rules

### 🎨 Templates (6 HTML files in templates/)
1. `base.html` - Common layout
2. `dashboard.html` - Statistics overview
3. `pending.html` - Active help requests
4. `resolved.html` - Request history
5. `knowledge.html` - Q&A browser
6. `appointments.html` - Schedule viewer

### 🔐 Secrets
- `secrets/frontdesk-firebase.json` - Firebase credentials

---

## 🚀 Quick Commands

### Start System
```powershell
# Terminal 1: Supervisor UI
.\venv\Scripts\python.exe supervisor_ui.py

# Terminal 2: AI Agent (console mode)
.\venv\Scripts\python.exe agent.py console
```

### Access Web UI
- Dashboard: http://localhost:5000
- Pending: http://localhost:5000/pending
- Resolved: http://localhost:5000/resolved
- Knowledge: http://localhost:5000/knowledge
- Appointments: http://localhost:5000/appointments

---

## 🎯 Features at a Glance

### AI Agent Tools (6)
1. ✅ `search_knowledge_base` - Check learned answers
2. ✅ `request_help` - **Human-in-the-Loop**: Call supervisor (60s timeout)
3. ✅ `check_available_slots` - Check appointment availability
4. ✅ `book_appointment` - Book customer appointments
5. ✅ `cancel_appointment` - Cancel bookings
6. ✅ `end_call` - End conversation & terminate

### Key Features
- ✅ **Human-in-the-Loop Learning** - AI calls supervisors for unknown questions
- ✅ **Automatic Knowledge Building** - Learns from supervisor responses
- ✅ Intelligent knowledge base with fuzzy matching
- ✅ Appointment booking (Mon-Sat 9am-6pm)
- ✅ 60-second timeout with graceful fallback
- ✅ Supervisor rejection of requests
- ✅ Auto call termination
- ✅ Background response monitoring

### Database (5 Collections)
1. `pending_requests` - Questions waiting for human supervisor
2. `resolved_requests` - Supervisor answers (learning history)
3. `knowledge_base` - Learned Q&A pairs from supervisors
4. `appointments` - Scheduled bookings
5. `caller_notifications` - SMS notification log

---

## 📊 Total File Count

| Category          | Count  |
|-------------------|--------|
| Core Python Files | 6      |
| HTML Templates    | 6      |
| Documentation     | 2      |
| Configuration     | 3      |
| **Total**         | **17** |

Plus: `venv/` (virtual environment), `secrets/` (credentials), `__pycache__/` (auto-generated)

---

## 📖 Documentation Guide

**First Time Setup?**  
→ Read `SETUP.md` first

**Need Feature Details & Human-in-the-Loop Info?**  
→ Read `README.md` next

**Quick Reference?**  
→ This file!

---

## ✅ System Status

- ✅ Human-in-the-Loop AI learning system
- ✅ AI calls supervisors for unknown questions
- ✅ Automatic knowledge base building
- ✅ All test files removed
- ✅ Documentation consolidated (7 → 3 files)
- ✅ Clean project structure
- ✅ Production ready
- ✅ Easy to maintain

---

**System Type:** Human-in-the-Loop AI Learning  
**Version:** 1.0  
**Status:** Production Ready ✅  
**Last Updated:** November 6, 2025
