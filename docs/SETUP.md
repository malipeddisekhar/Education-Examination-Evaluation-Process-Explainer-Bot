# Setup Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | 3.14 tested |
| pip | latest | `python -m pip install --upgrade pip` |
| Groq API Key | — | Free at [console.groq.com](https://console.groq.com) |
| Poppler | any | Required for OCR on scanned PDFs only |
| Tesseract | any | Required for OCR on scanned PDFs only |

---

## Step 1 — Clone the Repository

```bash
git clone <your-repo-url>
cd "ERROR SQUAD"
```

---

## Step 2 — Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and paste your Groq API key
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxx
```

Get your free key at: https://console.groq.com

---

## Step 5 — Run the App

```bash
streamlit run app.py
```

Open: http://localhost:8501

---

## Step 6 — Upload Documents & Build Knowledge Base

1. Open the **sidebar** (left panel)
2. Click **"Browse files"** → select your exam regulation PDFs
3. Click **"Build Knowledge Base"**
4. Wait for the ✅ confirmation
5. Start asking questions!

---

## Optional: OCR for Scanned PDFs

If your PDFs are scanned images (not text-selectable), install:

**Poppler (Windows):**
```
Download from: https://github.com/oschwartz10612/poppler-windows/releases
Add bin/ folder to your system PATH
```

**Tesseract (Windows):**
```
Download from: https://github.com/UB-Mannheim/tesseract/wiki
Add install folder to your system PATH
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside `.venv` |
| `GROQ_API_KEY not found` | Check `.env` file exists with correct key |
| Voice not transcribing | Check browser has mic permission; ffmpeg not required |
| FAISS load error | Delete `faiss_knowledge_base/` folder and rebuild |
| Slow embeddings first run | Model downloads once (~90MB); subsequent runs are instant |
