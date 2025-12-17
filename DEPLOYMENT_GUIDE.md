# Deployment Guide

## Frontend Deployment (Vercel)

### Steps:
1. Push your frontend folder to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project" → Import GitHub repo → select your repo
4. Framework: `Vite`
5. Root Directory: `frontend`
6. Build Command: `npm run build`
7. Output Directory: `.vite/dist` or `dist`
8. Environment Variables:
   ```
   VITE_API_URL=https://your-backend-url.com
   ```
9. Deploy!

**Your frontend will be live at:** `https://your-project.vercel.app`

---

## Backend Deployment (Railway)

### Prerequisites:
- GitHub account with your project repository
- Railway account (create free at [railway.app](https://railway.app))

### Steps:

#### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 2. Create Railway Account
- Go to [railway.app](https://railway.app)
- Sign up with GitHub
- Authorize Railway to access your repos

#### 3. Deploy on Railway
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Select the root directory (where requirements.txt is)
5. Railway will auto-detect it's Python + FastAPI

#### 4. Configure Environment Variables
In Railway dashboard, go to "Variables" and add:
```
PYTHONUNBUFFERED=1
PORT=8000
```

#### 5. Set Build & Start Commands (if needed)
- Build: `pip install -r requirements.txt`
- Start: `uvicorn api.app:app --host 0.0.0.0 --port $PORT`

#### 6. Get Your Backend URL
- Railway will give you a URL like: `https://your-app-xxx.railway.app`
- Copy this URL

---

## Connect Frontend to Backend

### Update Frontend Environment Variables:

In your Vercel project settings:
1. Go to Settings → Environment Variables
2. Add:
   ```
   VITE_API_URL=https://your-app-xxx.railway.app
   ```
3. Redeploy

---

## Update Backend CORS for Vercel Frontend

Edit `api/app.py` to allow your Vercel frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-project.vercel.app",  # Your Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Update Frontend API Calls

Update `frontend/src/lib/api.ts` to use environment variable:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = {
  async sendChat(sessionId: string, message: string) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    return response.json();
  },
  // ... rest of your API methods
};
```

---

## Testing

1. Go to your Vercel frontend URL
2. Try the chat/voice features
3. Check Network tab in browser DevTools to verify API calls go to Railway backend
4. Check Railway logs if something fails: Dashboard → Logs

---

## Monitoring

### Railway:
- Dashboard shows real-time logs
- Click project → "Logs" tab to see errors
- Memory/CPU usage visible

### Vercel:
- Analytics available in dashboard
- Function logs in Settings → Functions

---

## Troubleshooting

**Backend showing 502 error?**
- Check Railway logs for errors
- Verify requirements.txt is up to date
- Ensure Procfile points to correct app: `uvicorn api.app:app`

**Frontend can't reach backend?**
- Check CORS settings in api/app.py
- Verify VITE_API_URL is set correctly
- Check Network tab in browser DevTools

**Voice/TTS not working?**
- Ensure backend is using correct imports
- Check if Deepgram keys are set (if using real Deepgram)
- Web Speech API only works in Chrome/Edge

---

## Cost

- **Vercel**: Free tier covers most projects
- **Railway**: Free $5/month credits (usually enough for testing)
- Both have paid tiers if you need more capacity

**Estimated monthly cost for both: $0-10** (if staying within free tiers)

---

## Next Steps

1. Push code to GitHub
2. Deploy frontend to Vercel
3. Deploy backend to Railway
4. Update CORS and API URLs
5. Test everything end-to-end
6. Monitor logs for any issues
