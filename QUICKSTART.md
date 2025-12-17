# Quick Start Guide - Voice-Enabled Retail AI

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Modern browser (Chrome/Edge recommended for voice)

### 1. Backend Setup

```powershell
# Navigate to project directory
cd d:/Project/EY

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Seed the database with sample data
python seed_data.py

# Start the API server
python api/app.py
```

The backend should now be running at `http://localhost:8000`

### 2. Frontend Setup

```powershell
# Navigate to frontend directory
cd d:/Project/EY/frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

The frontend should now be running at `http://localhost:5173`

## 🎤 Using Voice Features

### Step 1: Open the Application
Navigate to `http://localhost:5173` in Chrome or Edge

### Step 2: Start Voice Session
1. Look for the "Voice Director" panel
2. Click the **"Go Live"** button
3. Allow microphone access when prompted

### Step 3: Start Talking
- Speak naturally: "Show me available laptops"
- Wait for transcription to appear
- AI will respond both in text and voice
- Continue the conversation naturally

### Step 4: Stop When Done
- Click the **"Stop"** button to end voice session

## 💬 Using Chat Features

### Text Chat
1. Type your message in the "Conversation Studio" panel
2. Press Enter or click Send
3. AI agent responds with recommendations, inventory info, or answers

### Example Queries
- "What products do you have?"
- "I'm looking for a laptop under $1000"
- "Add this to my cart"
- "What's in stock?"
- "I need help choosing a phone"

## 📊 Features Overview

### Real-Time Voice
- ✅ Continuous speech recognition
- ✅ Live transcription
- ✅ AI voice responses
- ✅ Natural conversation flow

### Smart Recommendations
- ✅ Mood detection
- ✅ Context-aware suggestions
- ✅ Product recommendations
- ✅ Inventory checking

### Shopping Cart
- ✅ Add products to cart
- ✅ View cart status
- ✅ Real-time updates

### Insights Dashboard
- ✅ Active sessions
- ✅ Product count
- ✅ Sales metrics
- ✅ Customer mood tracking

## 🔧 Troubleshooting

### Voice Not Working
**Problem**: Voice button doesn't activate
**Solution**: 
1. Use Chrome or Edge browser
2. Ensure you're on localhost or HTTPS
3. Grant microphone permission
4. Check if backend is running

### Backend Connection Error
**Problem**: "Unable to reach orchestrator"
**Solution**:
1. Verify backend is running: `http://localhost:8000`
2. Check console for CORS errors
3. Restart backend server

### No Products Showing
**Problem**: Product shelf is empty
**Solution**:
1. Run seed script: `python seed_data.py`
2. Check database connection in backend logs
3. Verify API endpoint: `http://localhost:8000/api/products`

### Microphone Permission Denied
**Problem**: Can't access microphone
**Solution**:
1. Check browser permissions (address bar icon)
2. Reset site permissions
3. Try different browser

## 📝 Test Scenarios

### Scenario 1: Product Discovery
```
You: "What laptops do you have?"
AI: "We have several laptops available. Here are some recommendations..."
[Products appear in product shelf]
```

### Scenario 2: Add to Cart
```
You: "Add the first laptop to my cart"
AI: "I've added it to your cart. Anything else?"
[Cart count updates]
```

### Scenario 3: Inventory Check
```
You: "Is the MacBook Pro in stock?"
AI: "Let me check... Yes, we have 5 units available."
```

### Scenario 4: Price Inquiry
```
You: "What's your cheapest laptop?"
AI: "Our most affordable laptop is the HP Stream at $299."
```

## 🎯 Key Components

### Voice Director Panel
- **Go Live** button - Start/stop voice
- **Transcript** - Real-time speech display
- **Waveform** - Visual audio indicator
- **Status** - Connection and error states

### Conversation Studio
- **Chat history** - All messages
- **Input box** - Type messages
- **Status** - Processing indicators

### Mood Card
- **Current mood** - Detected from conversation
- **Confidence** - Detection accuracy
- **Suggested tone** - Response style

### Product Shelf
- **Recommendations** - AI-suggested products
- **Add to Cart** - Quick add buttons
- **Product info** - Name, price, stock

### Insight Grid
- **Sessions** - Active users
- **Products** - Total inventory
- **Stats** - System metrics

## 🔐 Security Notes

- Microphone access required for voice
- Session-based tracking
- No personal data stored without consent
- Secure WebSocket connections in production

## 📱 Browser Support

| Feature | Chrome | Edge | Firefox | Safari |
|---------|--------|------|---------|--------|
| Voice Recognition | ✅ | ✅ | ⚠️ | ⚠️ |
| Voice Synthesis | ✅ | ✅ | ✅ | ✅ |
| Chat | ✅ | ✅ | ✅ | ✅ |
| WebSocket | ✅ | ✅ | ✅ | ✅ |

## 🆘 Need Help?

1. Check backend logs in terminal
2. Check browser console (F12)
3. Verify all services are running
4. Review VOICE_INTEGRATION.md for details

## 🎉 You're Ready!

Open `http://localhost:5173` and start chatting with your AI retail assistant!

---

**Quick Commands:**
```powershell
# Start Backend
cd d:/Project/EY && python api/app.py

# Start Frontend
cd d:/Project/EY/frontend && npm run dev

# Seed Database
cd d:/Project/EY && python seed_data.py
```
