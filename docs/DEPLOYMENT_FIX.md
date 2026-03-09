# Quick Deployment Fix Guide

## Issue
The Blueprint deployment may fail due to environment variable configuration complexity.

## Solution: Manual Deployment (Recommended)

### Step 1: Deploy Backend First
1. Go to Render Dashboard → **New +** → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `task-review-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   - `ALLOWED_ORIGINS` = `["*"]`
5. Click **Create Web Service**
6. **IMPORTANT**: Copy the backend URL (e.g., `https://task-review-backend-xxxx.onrender.com`)

### Step 2: Deploy Frontend
1. Go to **New +** → **Static Site**
2. Connect the same GitHub repo
3. Configure:
   - **Name**: `task-review-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`
4. Environment Variables:
   - `REACT_APP_BACKEND_URL` = `<YOUR_BACKEND_URL>/api/v1/task`
   - Example: `https://task-review-backend-xxxx.onrender.com/api/v1/task`
5. Click **Create Static Site**

### Step 3: Wait for Build
- Backend: ~2-3 minutes
- Frontend: ~3-5 minutes

## Common Errors & Fixes

### "npm: command not found"
- Render should auto-detect Node.js from `package.json`
- If not, add to frontend environment: `NODE_VERSION` = `18`

### "Module not found" errors
- Ensure `package.json` is in the `frontend/` directory
- Check build logs for specific missing packages

### Backend shows "Offline"
- Wait for backend to fully deploy first
- Verify `REACT_APP_BACKEND_URL` includes `/api/v1/task`
- Check CORS settings on backend

### Build timeout
- Free tier has limited resources
- Try deploying during off-peak hours
- Consider upgrading to paid tier if needed

## Verify Deployment

### Backend Health Check
Visit: `https://your-backend-url.onrender.com/health`

Should return:
```json
{
  "status": "healthy",
  "version": "1.1.0"
}
```

### Frontend
Visit: `https://your-frontend-url.onrender.com`

Should show the React UI with "Backend Online" in the status badge.

## Need the Error Logs?

Please share:
1. Which service failed (Backend or Frontend)?
2. The specific error message from the logs
3. Screenshot if possible

I can provide a more specific fix based on the actual error!
