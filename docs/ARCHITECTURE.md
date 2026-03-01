# Architecture — Exam Evaluation Explainer Bot

## System Overview

```
User (Browser)
    │
    ▼
┌──────────────────────────────────────────────────────┐
│                  Streamlit Frontend                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Sidebar     │  │  Chat Area   │  │  Input Bar  │  │
│  │  PDF Upload  │  │  History     │  │  Text/Voice │  │
│  │  KB Builder  │  │  Messages    │  │  + / Mic    │  │
│  └─────────────┘  └──────────────┘  └─────────────┘  │
└──────────────────────────────────────────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                ┌──────────────────────┐
│  Knowledge Base │                │    Voice Pipeline     │
│  Builder        │                │                      │
│                 │                │  Browser Mic (WebM)  │
│  PyPDF2 / OCR   │                │       ↓              │
│  Text Chunks    │                │  Groq Whisper API    │
│  HuggingFace    │                │  (whisper-large-v3)  │
│  Embeddings     │                │       ↓              │
│  FAISS Index    │                │  Transcribed Text    │
└────────┬────────┘                └──────────┬───────────┘
         │                                    │
         ▼                                    ▼
┌──────────────────────────────────────────────────────┐
│                   RAG Pipeline                        │
│                                                      │
│  1. FAISS Similarity Search (top-K chunks)           │
│  2. Context Assembly (chunks + history + question)   │
│  3. Groq LLM Inference (llama-3.3-70b-versatile)     │
│  4. Streaming Response → Chat UI                     │
└──────────────────────────────────────────────────────┘
```

## RAG Flow (Step by Step)

1. **PDF Ingestion** — User uploads exam regulation PDFs via sidebar
2. **Text Extraction** — PyPDF2 extracts text; pytesseract handles scanned PDFs via OCR
3. **Chunking** — CharacterTextSplitter splits into 500-char chunks with 50-char overlap
4. **Embedding** — `sentence-transformers/all-MiniLM-L6-v2` generates 384-dim vectors
5. **Indexing** — FAISS stores vectors; persisted to `faiss_knowledge_base/` for reuse
6. **Query** — User question → embed → FAISS top-2 similarity search → retrieve chunks
7. **Augment** — System prompt + retrieved chunks + conversation history + question = final prompt
8. **Generate** — Groq API streams response token-by-token to the chat UI

## Voice Pipeline

```
st.audio_input (hidden)  →  WebM/Opus bytes
        ↓
Groq Whisper API  →  transcribed text  (< 0.5s)
        ↓
pending_voice session_state  →  survives Streamlit rerun
        ↓
RAG Pipeline (same as typed input)
```

## Models Used

| Task | Model | Provider |
|------|-------|----------|
| Chat / QA | llama-3.3-70b-versatile | Groq |
| Fast Chat | llama-3.1-8b-instant | Groq |
| Voice STT | whisper-large-v3-turbo | Groq |
| Embeddings | all-MiniLM-L6-v2 | HuggingFace |
