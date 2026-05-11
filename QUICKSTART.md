# 🚀 QUICK START GUIDE

## Deploy in 5 Minutes

### Step 1: Get Your API Key (2 minutes)
1. Go to https://console.groq.com
2. Sign up (free)
3. Click "API Keys" → "Create API Key"
4. Copy your key (starts with `gsk_...`)

### Step 2: Deploy to Render (3 minutes)
1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Fill in:
   - **Name**: `education-explainer-bot`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
5. Click **"Advanced"** → **"Add Environment Variable"**
   - **Key**: `GROQ_API_KEY`
   - **Value**: [Paste your API key]
6. Click **"Create Web Service"**
7. Wait 5-10 minutes
8. Done! 🎉

### Step 3: Test Your App
1. Open your Render URL (e.g., `https://education-explainer-bot.onrender.com`)
2. Upload a PDF in the sidebar
3. Click "🔨 Build KB"
4. Ask a question
5. Get an answer!

---

## Alternative: Deploy to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

### Step 2: Deploy
1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Select your repository
4. Click **"Advanced settings"** → **"Secrets"**
5. Add:
   ```toml
   GROQ_API_KEY = "your_key_here"
   ```
6. Click **"Deploy!"**
7. Wait 3-5 minutes
8. Done! 🎉

---

## Test Locally First

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Education-Examination-Evaluation-Process-Explainer-Bot

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API key
# Create .env file with:
# GROQ_API_KEY=your_key_here

# 5. Run app
streamlit run app.py

# 6. Open browser
# http://localhost:8501
```

---

## Troubleshooting

### "GROQ_API_KEY not configured"
- Make sure you added the environment variable
- Check the key is correct (starts with `gsk_`)
- Redeploy the service

### Build fails
- Check deployment logs
- Verify `requirements.txt` has correct versions
- Make sure `runtime.txt` specifies Python 3.11

### App is slow
- First launch takes 2-3 minutes (downloading models)
- Subsequent launches are faster
- Use "Llama 3.1 8B (Fast)" model for speed

---

## Need Help?

- 📖 Full deployment guide: See `DEPLOYMENT_FIXED.md`
- 🐛 Issues: Create a GitHub issue
- 💬 Questions: Check Streamlit forum

---

**Ready to deploy? Let's go! 🚀**
