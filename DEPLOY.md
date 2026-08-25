# 🚀 Deployment Guide

## Deploy to Streamlit Community Cloud (Free & Recommended)

### Prerequisites
- GitHub account with this repository pushed ✅
- Free Groq API key from https://console.groq.com

---

## Step-by-Step Deployment

### 1. Go to Streamlit Cloud
Visit 👉 **https://share.streamlit.io**  
Sign in with your **GitHub account**.

---

### 2. Create a New App
Click **"New app"** → **"From existing repo"**

Fill in:
| Field | Value |
|-------|-------|
| **Repository** | `malipeddisekhar/Education-Examination-Evaluation-Process-Explainer-Bot` |
| **Branch** | `main` |
| **Main file path** | `app.py` |
| **App URL** | Choose a custom slug (e.g. `exam-explainer`) |

---

### 3. Add Secrets (API Key)
Before clicking Deploy, click **"Advanced settings"** → **"Secrets"**

Paste this exactly:
```toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
HF_HUB_DISABLE_SYMLINKS_WARNING = "1"
```

---

### 4. Deploy
Click **"Deploy!"**

The first deploy takes **5–10 minutes** (downloads ML models).  
After that, the app auto-redeploys on every GitHub push.

---

### 5. Your Live URL
Your app will be live at:
```
https://[your-slug].streamlit.app
```

---

## After Deployment — First Use

1. Open the live URL
2. Upload your exam regulation PDF(s) in the sidebar
3. Click **"🔨 Build KB"** to process them
4. Start asking questions!

> **Note:** The knowledge base is built per-session. After the server restarts, you'll need to re-upload and rebuild. This is normal for free-tier hosting.

---

## File Structure (Deployment-Ready)
```
├── app.py                    ← Main application
├── htmlTemplates.py          ← CSS & UI templates
├── requirements.txt          ← Python dependencies
├── packages.txt              ← Linux system packages (ffmpeg)
├── .streamlit/
│   ├── config.toml           ← Production Streamlit config
│   └── secrets.toml.example  ← Secret template (DON'T commit actual secrets)
├── .env.example              ← Local dev template
├── .gitignore                ← Proper ignores (.env, .venv, faiss_knowledge_base)
└── docs/
    ├── ARCHITECTURE.md
    └── SETUP.md
```

---

## Local Development

```bash
# 1. Clone
git clone https://github.com/malipeddisekhar/Education-Examination-Evaluation-Process-Explainer-Bot.git
cd Education-Examination-Evaluation-Process-Explainer-Bot

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run
streamlit run app.py
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 413 Token limit error | Reduce "Max Tokens" in sidebar to 256 |
| Embedding model slow on first load | Wait ~60s — it downloads once and caches |
| Knowledge base lost after refresh | Re-upload PDF and click "Build KB" |
| API key not working | Generate a new key at https://console.groq.com/keys |
