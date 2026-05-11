# ============================================================
# Education Examination & Evaluation Process Explainer Bot
# ============================================================
# A student-friendly AI assistant that explains academic
# examination & evaluation processes using uploaded documents.
#
# Components:
#   1. Knowledge Base   - PDF upload, text extraction, chunking
#   2. LLM Selection    - Groq API (Llama 3.3 70B, Mixtral, Gemma2)
#   3. Prompt Config    - Academic system prompt, generation params
#   4. RAG + Vector DB  - FAISS vector store with HuggingFace embeddings
#   5. Voice I/O        - Speech-to-text input, text-to-speech output
#   6. Academic Safety  - Strict guardrails against misuse
# ============================================================

# ----- Imports -----
import os
import io
import time
import base64
import tempfile
from dotenv import load_dotenv
import streamlit as st
import streamlit.components.v1 as stcomp
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from groq import Groq
from htmlTemplates import css, bot_template, user_template
import speech_recognition as sr
from gtts import gTTS

# OCR support (optional — install poppler + pytesseract to enable)
# On Windows, ensure poppler is in PATH; on Linux/Render, install via system: apt-get install poppler-utils tesseract-ocr
try:
    from pdf2image import convert_from_bytes
    import pytesseract
    # Configure pytesseract for Windows only (path not needed on Linux if installed via apt)
    if os.name == 'nt':
        pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ============================================================
# 1. KNOWLEDGE BASE CONFIGURATION
# ============================================================
# Chunking parameters for building the knowledge base
CHUNK_SIZE = 500           # Number of characters per chunk (smaller = more precise retrieval)
CHUNK_OVERLAP = 50         # Overlap between consecutive chunks
CHUNK_SEPARATOR = "\n"     # Separator used to split text

# Embedding model for vectorizing text chunks
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"

# Number of relevant chunks to retrieve per query
RETRIEVAL_TOP_K = 2

# Local path to persist the FAISS vector store
VECTORSTORE_PERSIST_DIR = "faiss_knowledge_base"

# ============================================================
# 2. LLM SELECTION (Groq)
# ============================================================
# Available Groq models (all free)
AVAILABLE_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma2 9B": "gemma2-9b-it",
}
DEFAULT_MODEL = "Llama 3.3 70B"

# ============================================================
# 3. PROMPT CONFIGURATION & GENERATION PARAMETERS
# ============================================================
# System prompt — strict academic examination explainer
SYSTEM_PROMPT = (
    "You are an Education Examination & Evaluation Process Assistant.\n\n"
    "=== STRICT DOCUMENT-GROUNDING RULES (HIGHEST PRIORITY) ===\n"
    "1. You MUST answer ONLY using information that is EXPLICITLY and LITERALLY present "
    "in the RETRIEVED DOCUMENT CONTEXT provided to you.\n"
    "2. INACCURATE / OUT-OF-RANGE VALUES: If the document defines a valid range or set "
    "of permitted values for something (e.g., marks 0\u2013100, specific grade letters, "
    "defined attendance percentages) AND the user asks about a value that FALLS OUTSIDE "
    "or is INCONSISTENT with that defined range, you MUST respond EXACTLY with:\n"
    "   \"\u274c Inaccurate value: According to the uploaded document, [topic] must be "
    "in the range [valid range / permitted values from the document]. "
    "The value you mentioned ([user's value]) is outside this defined range and is therefore invalid.\"\n"
    "   Fill in [topic], [valid range], and [user's value] with the actual values from "
    "the document and the user's query.\n"
    "   EXAMPLE: Document defines grades for marks 0\u2013100. User asks about 101 marks.\n"
    "   Correct response: \"\u274c Inaccurate value: According to the uploaded document, "
    "marks must be in the range 0\u2013100. The value you mentioned (101) is outside this "
    "defined range and is therefore invalid.\"\n"
    "3. MISSING INFORMATION: If the user's question asks about a value, scenario, or case "
    "that is simply NOT mentioned or defined anywhere in the document context, "
    "you MUST respond EXACTLY with:\n"
    "   \"\u26a0\ufe0f This information is not available in the uploaded document(s). "
    "Please refer to your institution's official regulations for this specific query.\"\n"
    "4. You MUST NOT infer, extrapolate, calculate, or assume any information "
    "beyond what is explicitly written in the context.\n"
    "5. You MUST NOT use your general training knowledge to fill gaps. "
    "If it is not in the document, it does not exist for you.\n"
    "6. Partial answers are not allowed. If only part of the question is covered "
    "in the document, answer only that part and explicitly state what is NOT covered.\n\n"
    "=== SCOPE ===\n"
    "Your purpose is to explain (from the document only):\n"
    "- Examination patterns and schedules\n"
    "- Internal and external evaluation methods\n"
    "- Grading systems (CGPA, GPA, letter grades, percentage)\n"
    "- Revaluation and recounting processes\n"
    "- Supplementary and improvement examinations\n"
    "- Attendance rules and eligibility criteria\n"
    "- Hall ticket and registration procedures\n"
    "- Result publication and transcript processes\n\n"
    "=== RESPONSE STYLE ===\n"
    "- Use simple, student-friendly language\n"
    "- Use clear headings, bullet points, or numbered steps\n"
    "- Be encouraging and supportive in tone\n\n"
    "=== ABSOLUTE PROHIBITIONS ===\n"
    "- NEVER predict, estimate, or calculate grades or marks\n"
    "- NEVER answer questions about values/scenarios not present in the document\n"
    "- NEVER solve exam questions or provide model answers\n"
    "- NEVER assist with academic dishonesty\n"
    "- NEVER discuss topics outside examination & evaluation processes\n"
    "- NEVER use knowledge from outside the provided document context\n\n"
    "If a user asks anything outside examination process explanation, reply:\n"
    "'I can only help explain examination and evaluation processes as described "
    "in the uploaded documents. Please ask about exam patterns, grading, "
    "revaluation, or similar topics.'\n"
)

# Default generation parameters (configurable via sidebar)
DEFAULT_TEMPERATURE = 0.0   # 0.0 = fully deterministic, prevents hallucination
DEFAULT_TOP_P = 0.95        # Nucleus sampling threshold
DEFAULT_MAX_TOKENS = 2048   # Maximum output tokens

# ============================================================
# KNOWLEDGE BASE FUNCTIONS
# ============================================================

def get_pdf_text(docs):
    """Extract text from all uploaded PDF files. Falls back to OCR for scanned/image PDFs."""
    text = ""
    for pdf in docs:
        try:
            pdf_bytes = pdf.read()
            pdf.seek(0)  # Reset for potential reuse
            
            # Check file size (warn if > 50MB)
            file_size_mb = len(pdf_bytes) / (1024 * 1024)
            if file_size_mb > 50:
                st.warning(f"⚠️ {pdf.name} is large ({file_size_mb:.1f}MB). Processing may take longer.")

            # --- Try normal text extraction first ---
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf_text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text

            # --- Fallback to OCR if text extraction yielded nothing ---
            if not pdf_text.strip() and OCR_AVAILABLE:
                try:
                    images = convert_from_bytes(pdf_bytes)
                    ocr_text = ""
                    for img in images:
                        page_ocr = pytesseract.image_to_string(img)
                        if page_ocr:
                            ocr_text += page_ocr + "\n"
                    if ocr_text.strip():
                        pdf_text = ocr_text
                        st.info(f"📷 OCR applied to **{pdf.name}** — scanned PDF detected.")
                    else:
                        st.warning(f"⚠️ Could not extract text from **{pdf.name}** (even with OCR).")
                except Exception as e:
                    st.warning(f"⚠️ OCR failed for **{pdf.name}**: {e}")
            elif not pdf_text.strip():
                st.warning(f"⚠️ Could not extract text from **{pdf.name}**. Install pytesseract for OCR support.")

            text += pdf_text
        except Exception as e:
            st.error(f"❌ Error processing **{pdf.name}**: {str(e)}")
            continue
            
    return text


def get_chunks(raw_text):
    """Split extracted text into overlapping chunks for the knowledge base."""
    # Clean the raw text first
    raw_text = raw_text.encode('utf-8', errors='ignore').decode('utf-8')
    raw_text = ' '.join(raw_text.split())  # Remove extra whitespace
    
    text_splitter = CharacterTextSplitter(
        separator=CHUNK_SEPARATOR,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)
    # Ensure all chunks are valid strings with proper encoding
    cleaned_chunks = []
    for chunk in chunks:
        if chunk and chunk.strip():
            # Clean each chunk
            clean_text = str(chunk).encode('utf-8', errors='ignore').decode('utf-8')
            clean_text = ' '.join(clean_text.split()).strip()
            if clean_text:
                cleaned_chunks.append(clean_text)
    return cleaned_chunks


@st.cache_resource(show_spinner="Loading embedding model (one-time)...")
def get_embeddings():
    """Load and cache the HuggingFace embedding model. Only runs once."""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        encode_kwargs={"normalize_embeddings": False}
    )
    return embeddings


def get_vectorstore(chunks):
    """Create a FAISS vector store (knowledge base) from text chunks using cached embeddings."""
    embeddings = get_embeddings()
    try:
        vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
        return vectorstore
    except Exception as e:
        st.error(f"❌ Error creating vector store: {str(e)}")
        raise


def save_vectorstore(vectorstore):
    """Persist the FAISS knowledge base to disk for reuse."""
    vectorstore.save_local(VECTORSTORE_PERSIST_DIR)
    return True


def load_vectorstore():
    """Load a previously saved FAISS knowledge base from disk."""
    if os.path.exists(VECTORSTORE_PERSIST_DIR):
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(
            VECTORSTORE_PERSIST_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vectorstore
    return None


# ============================================================
# LLM INITIALIZATION (Groq)
# ============================================================

@st.cache_resource(show_spinner=False)
def get_groq_client():
    """Initialize and cache the Groq client (one-time, survives reruns)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        st.error("❌ **GROQ_API_KEY not configured!**\n\nPlease set your Groq API key in the environment variables.\nGet a free key at: https://console.groq.com")
        st.stop()
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Failed to initialize Groq client: {str(e)}")
        st.stop()


# ============================================================
# VOICE I/O FUNCTIONS
# ============================================================

def transcribe_audio(audio_file):
    """Fast transcription using Groq Whisper API.
    Accepts WebM/Opus directly from browser — no conversion needed."""
    try:
        audio_file.seek(0)
        raw_bytes = audio_file.read()
        audio_file.seek(0)
        if not raw_bytes or len(raw_bytes) < 100:
            return None
        client = get_groq_client()
        # Groq Whisper accepts WebM, WAV, MP3, OGG, FLAC natively
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", raw_bytes, "audio/webm"),
            model="whisper-large-v3-turbo",
            response_format="text",
            language="en",
        )
        result = transcription.strip() if isinstance(transcription, str) else str(transcription).strip()
        return result if result else None
    except Exception as e:
        # Fallback to Google STT if Groq Whisper fails
        try:
            recognizer = sr.Recognizer()
            audio_file.seek(0)
            raw_bytes = audio_file.read()
            audio_file.seek(0)
            from pydub import AudioSegment
            seg = AudioSegment.from_file(io.BytesIO(raw_bytes))
            wav_buf = io.BytesIO()
            seg.export(wav_buf, format="wav")
            wav_buf.seek(0)
            with sr.AudioFile(wav_buf) as source:
                audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
        except Exception:
            st.warning(f"⚠️ Voice transcription failed: {e}")
            return None


def text_to_speech(text):
    """Convert text to speech using gTTS and return MP3 audio bytes."""
    try:
        tts = gTTS(text=text[:500], lang="en", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        st.warning(f"⚠️ Text-to-speech error: {e}")
        return None


def get_audio_player_html(audio_bytes):
    """Generate an auto-play HTML audio element from audio bytes."""
    b64_audio = base64.b64encode(audio_bytes).decode()
    return f'<audio autoplay controls style="max-width:360px;height:34px;border-radius:12px;"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>'


# ============================================================
# RAG - RETRIEVAL AUGMENTED GENERATION
# ============================================================

def get_relevant_context(vectorstore, question, k=RETRIEVAL_TOP_K):
    """Retrieve top-k relevant chunks from the FAISS vector DB for RAG."""
    docs = vectorstore.similarity_search(question, k=k)
    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[Chunk {i}]:\n{doc.page_content}")
    return "\n\n".join(context_parts)


def build_rag_prompt(question, context, chat_history):
    """Build the full RAG prompt combining system prompt, context, history, and question."""
    # Build chat history string (trim to last 4 turns = 8 messages for speed)
    MAX_HISTORY_TURNS = 4
    history_text = ""
    if chat_history:
        recent_history = chat_history[-(MAX_HISTORY_TURNS * 2):]
        for role, text in recent_history:
            history_text += f"{role}: {text}\n"

    # Compose the full RAG prompt
    prompt = (
        f"### SYSTEM INSTRUCTIONS ###\n{SYSTEM_PROMPT}\n\n"
        f"### RETRIEVED DOCUMENT CONTEXT (from Knowledge Base) ###\n"
        f"--- START OF DOCUMENT CONTEXT ---\n{context}\n--- END OF DOCUMENT CONTEXT ---\n\n"
        f"### CONVERSATION HISTORY ###\n{history_text}\n"
        f"### USER QUESTION ###\n{question}\n\n"
        "### FINAL ANSWERING RULES ###\n"
        "Step 1: Search ONLY within the DOCUMENT CONTEXT above for information directly "
        "relevant to the question.\n"
        "Step 2: CHECK FOR INACCURATE / OUT-OF-RANGE VALUES FIRST: "
        "If the document defines a valid range or set of permitted values for the topic "
        "(e.g., marks 0\u2013100, specific attendance thresholds, defined grade letters), "
        "AND the user's question involves a value that falls OUTSIDE or violates that range, "
        "respond with EXACTLY:\n"
        "  '\u274c Inaccurate value: According to the uploaded document, [topic] must be "
        "in the range [valid range from document]. The value you mentioned ([user value]) "
        "is outside this defined range and is therefore invalid.'\n"
        "  (Replace bracketed placeholders with actual values.)\n"
        "Step 3: CHECK FOR MISSING INFORMATION: If the topic or scenario is simply not "
        "mentioned anywhere in the document context at all, respond with EXACTLY:\n"
        "  '\u26a0\ufe0f This specific information is not available in the uploaded document(s). "
        "Please refer to your institution\'s official regulations.'\n"
        "Step 4: Do NOT extrapolate, calculate, or infer. NEVER use external knowledge. "
        "Your ONLY source of truth is the document context above."
    )
    return prompt


def stream_response(client, model_id, system_prompt, user_prompt, temperature, top_p, max_tokens):
    """Stream response from Groq for typing animation effect."""
    stream = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


def handle_question(question):
    """Process user question through the full RAG pipeline: retrieve → prompt → generate."""
    vectorstore = st.session_state.vectorstore
    client = st.session_state.groq_client

    # RAG Step 1: Retrieve relevant context from vector DB knowledge base
    with st.spinner("🔍 Searching knowledge base..."):
        context = get_relevant_context(vectorstore, question, k=st.session_state.retrieval_k)

    # RAG Step 2: Build the augmented prompt
    prompt = build_rag_prompt(question, context, st.session_state.chat_history)

    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    # RAG Step 3: Generate response with typing animation (streaming)
    answer = None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with st.chat_message("assistant", avatar="🎓"):
                with st.spinner("Thinking..."):
                    # Small delay to show spinner before streaming starts
                    pass
                answer = st.write_stream(
                    stream_response(
                        client,
                        st.session_state.selected_model_id,
                        SYSTEM_PROMPT,
                        prompt,
                        st.session_state.temperature,
                        st.session_state.top_p,
                        st.session_state.max_tokens,
                    )
                )
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    st.warning(f"⏳ Rate limited. Waiting {wait_time}s before retry ({attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    st.error(
                        "❌ **Rate limit reached.** Please wait a moment and try again.\n\n"
                        "Free tier has rate limits. Try again shortly."
                    )
                    return
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower() or "connect" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    st.warning(f"⏳ Connection issue. Retrying in {wait_time}s ({attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    st.error("❌ Connection error. Please check your internet and try again.")
                    return
            else:
                st.error(f"❌ Error: {error_msg}")
                return

    if answer is None:
        return

    # Update chat history
    st.session_state.chat_history.append(("user", question))
    st.session_state.chat_history.append(("assistant", answer))

    # Generate TTS for the bot answer if voice is enabled
    if st.session_state.get("voice_output_enabled", False):
        tts_audio = text_to_speech(answer)
        if tts_audio:
            st.session_state.last_tts_audio = tts_audio


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for API key early
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        st.error(
            "❌ **GROQ_API_KEY not configured!**\n\n"
            "Please set your Groq API key in the environment variables.\n\n"
            "Get a free key at: https://console.groq.com"
        )
        st.stop()
    
    st.set_page_config(
        page_title="Education Examination & Evaluation Process Explainer",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inject CSS + non-blocking font preload (speeds up first paint)
    st.markdown(css, unsafe_allow_html=True)

    # Show startup message while models load (first time only)
    try:
        # Preload embeddings in background - shows spinner while loading
        _ = get_embeddings()
    except Exception as e:
        st.error(f"⚠️ Embedding model loading failed: {e}")
        return

    # Initialize session state
    if "vectorstore" not in st.session_state:
        # Auto-load saved KB on startup so it's ready after refresh
        saved = load_vectorstore()
        st.session_state.vectorstore = saved
        if saved:
            st.session_state.kb_doc_count = st.session_state.get("kb_doc_count", 1)
    if "groq_client" not in st.session_state:
        st.session_state.groq_client = get_groq_client()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "kb_doc_count" not in st.session_state:
        st.session_state.kb_doc_count = 0
    if "kb_chunk_count" not in st.session_state:
        st.session_state.kb_chunk_count = 0
    if "retrieval_k" not in st.session_state:
        st.session_state.retrieval_k = RETRIEVAL_TOP_K
    if "temperature" not in st.session_state:
        st.session_state.temperature = DEFAULT_TEMPERATURE
    if "top_p" not in st.session_state:
        st.session_state.top_p = DEFAULT_TOP_P
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = DEFAULT_MAX_TOKENS
    if "selected_model_id" not in st.session_state:
        st.session_state.selected_model_id = AVAILABLE_MODELS[DEFAULT_MODEL]
    if "voice_output_enabled" not in st.session_state:
        st.session_state.voice_output_enabled = True
    if "last_tts_audio" not in st.session_state:
        st.session_state.last_tts_audio = None
    if "last_uploaded_file_ids" not in st.session_state:
        st.session_state.last_uploaded_file_ids = []

    # ===== SIDEBAR =====
    with st.sidebar:
        # -- Branding --
        st.markdown('<div class="sidebar-title">🎓 Exam Explainer</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-subtitle">Education Examination & Evaluation Process Explainer Bot</div>', unsafe_allow_html=True)
        st.markdown("---")

        # ---- 📘 About This Bot ----
        st.markdown('<div class="section-header">📘 About This Bot</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="about-box">'
            'This bot helps students understand <b>examination and evaluation processes</b> '
            'from uploaded academic documents. Ask about grading, revaluation, '
            'supplementary exams, attendance rules, and more.'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")

        # ---- STEP 1: Upload Academic Documents ----
        st.markdown('<div class="section-header">📄 Step 1 — Upload Academic Documents</div>', unsafe_allow_html=True)
        docs = st.file_uploader(
            "Upload exam regulation PDFs, syllabi, or academic handbooks",
            accept_multiple_files=True,
            type=["pdf"],
            label_visibility="collapsed",
            key="pdf_uploader"
        )
        
        # Show file info and build button
        if docs:
            st.caption(f"📎 {len(docs)} document(s) selected")
            
            # Check if these are new files
            current_file_ids = [doc.file_id for doc in docs]
            last_file_ids = st.session_state.get("last_uploaded_file_ids", [])
            files_changed = current_file_ids != last_file_ids
            
            # Show build button
            col1, col2 = st.columns(2)
            with col1:
                build_btn = st.button(
                    "🔨 Build KB" if files_changed else "🔨 Rebuild KB",
                    use_container_width=True,
                    type="primary" if files_changed else "secondary",
                    help="Process PDFs and create knowledge base"
                )
            with col2:
                load_btn = st.button(
                    "📂 Load Saved KB",
                    use_container_width=True,
                    help="Load previously saved knowledge base"
                )
            
            # Build KB when button clicked
            if build_btn:
                progress_bar = st.progress(0, text="Starting...")
                try:
                    # Step 1: Extract text
                    progress_bar.progress(20, text="📄 Extracting text from PDFs...")
                    raw_text = get_pdf_text(docs)
                    
                    if not raw_text.strip():
                        st.error("❌ Could not extract text from the PDFs. Please ensure they contain readable text.")
                        progress_bar.empty()
                    else:
                        # Step 2: Create chunks
                        progress_bar.progress(40, text="✂️ Splitting text into chunks...")
                        text_chunks = get_chunks(raw_text)
                        
                        # Step 3: Create embeddings and vectorstore
                        progress_bar.progress(60, text="🧠 Creating embeddings (this may take a minute)...")
                        vectorstore = get_vectorstore(text_chunks)
                        
                        # Step 4: Save
                        progress_bar.progress(80, text="💾 Saving knowledge base...")
                        save_vectorstore(vectorstore)
                        
                        # Step 5: Update session state
                        progress_bar.progress(100, text="✅ Complete!")
                        st.session_state.vectorstore = vectorstore
                        st.session_state.kb_doc_count = len(docs)
                        st.session_state.kb_chunk_count = len(text_chunks)
                        st.session_state.last_uploaded_file_ids = current_file_ids
                        
                        progress_bar.empty()
                        st.success(
                            f"✅ **Knowledge Base Built Successfully!**\n\n"
                            f"📚 {len(docs)} document(s) → {len(text_chunks)} knowledge chunks\n\n"
                            f"You can now ask questions!"
                        )
                        st.balloons()
                        
                except Exception as e:
                    progress_bar.empty()
                    st.error(f"❌ Error building knowledge base: {str(e)}\n\nPlease try again or upload different PDFs.")
                    import traceback
                    with st.expander("🔍 Technical Details"):
                        st.code(traceback.format_exc())
            
            # Load saved KB
            if load_btn:
                with st.spinner("📂 Loading saved knowledge base..."):
                    try:
                        vectorstore = load_vectorstore()
                        if vectorstore:
                            st.session_state.vectorstore = vectorstore
                            st.success("✅ Knowledge Base Loaded Successfully!")
                        else:
                            st.warning("⚠️ No saved knowledge base found. Please build one first using the button above.")
                    except Exception as e:
                        st.error(f"❌ Error loading knowledge base: {str(e)}")
        else:
            # Show load button even without files
            if st.button("📂 Load Saved KB", use_container_width=True, help="Load previously saved knowledge base"):
                with st.spinner("📂 Loading saved knowledge base..."):
                    try:
                        vectorstore = load_vectorstore()
                        if vectorstore:
                            st.session_state.vectorstore = vectorstore
                            st.success("✅ Knowledge Base Loaded Successfully!")
                        else:
                            st.info("ℹ️ No saved knowledge base found. Please upload PDFs above to create one.")
                    except Exception as e:
                        st.error(f"❌ Error loading knowledge base: {str(e)}")

        st.markdown("---")

        # ---- STEP 2: Choose AI Model ----
        st.markdown('<div class="section-header">🤖 Step 2 — Choose AI Model</div>', unsafe_allow_html=True)
        selected_model_name = st.selectbox(
            "Model",
            list(AVAILABLE_MODELS.keys()),
            index=list(AVAILABLE_MODELS.keys()).index(DEFAULT_MODEL),
            label_visibility="collapsed"
        )
        selected_model_id = AVAILABLE_MODELS[selected_model_name]

        st.markdown("---")

        # ---- STEP 3: Settings (collapsible) ----
        st.markdown('<div class="section-header">⚙️ Step 3 — Settings</div>', unsafe_allow_html=True)
        with st.expander("Generation Parameters", expanded=False):
            temperature = st.slider("Temperature", 0.0, 1.0, DEFAULT_TEMPERATURE, 0.05,
                                    help="Lower = precise answers, Higher = creative answers")
            top_p = st.slider("Top-P", 0.0, 1.0, DEFAULT_TOP_P, 0.05,
                               help="Nucleus sampling threshold")
            max_tokens = st.slider("Max Tokens", 256, 8192, DEFAULT_MAX_TOKENS, 256,
                                   help="Max response length")

        with st.expander("Retrieval Settings", expanded=False):
            retrieval_k = st.slider("Chunks to retrieve", 1, 10, RETRIEVAL_TOP_K, 1,
                                    help="More chunks = broader context, but slower")
            st.session_state.retrieval_k = retrieval_k

        # Store current settings in session state
        st.session_state.selected_model_id = selected_model_id
        st.session_state.temperature = temperature
        st.session_state.top_p = top_p
        st.session_state.max_tokens = max_tokens

        st.markdown("---")

        # ---- STEP 4: Voice Settings ----
        st.markdown('<div class="section-header">🎙️ Step 4 — Voice</div>', unsafe_allow_html=True)
        st.session_state.voice_output_enabled = st.toggle(
            "🔊 Read answers aloud",
            value=st.session_state.voice_output_enabled,
            help="Enable text-to-speech for bot responses"
        )

        st.markdown("---")

        # ---- 📊 Status Dashboard ----
        st.markdown('<div class="section-header">📊 Status</div>', unsafe_allow_html=True)

        if st.session_state.vectorstore is not None:
            st.markdown(
                '<span class="status-badge status-ready">● Academic Knowledge Base Ready</span>',
                unsafe_allow_html=True
            )
            if st.session_state.kb_doc_count > 0:
                st.markdown(
                    f'<div class="status-row">'
                    f'<span class="status-label">Documents</span>'
                    f'<span class="status-value">{st.session_state.kb_doc_count}</span>'
                    f'</div>'
                    f'<div class="status-row">'
                    f'<span class="status-label">Chunks</span>'
                    f'<span class="status-value">{st.session_state.kb_chunk_count}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<span class="status-badge status-waiting">○ No Knowledge Base — Upload PDFs above</span>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="status-row">'
            f'<span class="status-label">Model</span>'
            f'<span class="status-value">{selected_model_name}</span>'
            f'</div>'
            f'<div class="status-row">'
            f'<span class="status-label">Temperature</span>'
            f'<span class="status-value">{temperature}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")

        # ---- ⚖️ Academic Integrity Notice ----
        st.markdown('<div class="section-header">⚖️ Academic Integrity Notice</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="integrity-notice">'
            '⚠️ This bot is designed <b>only to explain</b> examination and evaluation processes. '
            'It will <b>not</b>:<br>'
            '• Predict or estimate grades<br>'
            '• Solve exam questions<br>'
            '• Provide model answers<br>'
            '• Assist with academic dishonesty<br><br>'
            '<em>Use responsibly and ethically.</em>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.last_tts_audio = None
            st.rerun()

    # ===== MAIN CHAT AREA =====
    st.markdown(
        '<div class="main-header">'
        '<h1>🎓 Education Examination & Evaluation Process Explainer</h1>'
        '<p>Upload academic documents and ask about exam patterns, grading, revaluation, and more</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # Show welcome message when no KB and no chat
    if st.session_state.vectorstore is None and not st.session_state.chat_history:
        st.markdown(
            '<div class="welcome-box">'
            '<h3>👋 Welcome, Student!</h3>'
            '<p>To get started:</p>'
            '<ol>'
            '<li>📄 <b>Upload</b> your exam regulation PDFs in the sidebar (left panel)</li>'
            '<li>🔨 <b>Click "Build KB"</b> to process the documents</li>'
            '<li>💬 <b>Ask</b> questions about examination patterns, grading, revaluation, and more</li>'
            '</ol>'
            '<p><em>Example questions you can ask:</em></p>'
            '<ul>'
            '<li>"How does the grading system work?"</li>'
            '<li>"What is the revaluation process?"</li>'
            '<li>"What are the attendance requirements for eligibility?"</li>'
            '<li>"How do supplementary exams work?"</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )

    # Show existing chat history using st.chat_message
    if st.session_state.chat_history:
        for role, text in st.session_state.chat_history:
            if role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(text)
            else:
                with st.chat_message("assistant", avatar="🎓"):
                    st.markdown(text)

    # ---- Voice Input (hidden off-screen — triggered by custom mic button) ----
    audio_file = st.audio_input("voice", key="voice_input", label_visibility="collapsed")

    if audio_file is not None:
        audio_id = audio_file.file_id
        if st.session_state.get("last_audio_id") != audio_id:
            st.session_state.last_audio_id = audio_id
            with st.spinner("🎙️ Transcribing your voice..."):
                transcribed = transcribe_audio(audio_file)
            if transcribed:
                # Store in session_state so it survives the rerun triggered below
                st.session_state["pending_voice"] = transcribed
                st.toast(f'🎙️ You said: "{transcribed}"', icon="✅")
            else:
                st.warning("⚠️ Could not understand the audio. Please try again.")

    # ---- Custom + and Mic buttons — injected into DOM, positioned by iframe JS ----
    st.markdown(
        '''
        <div class="chatbar-plus" id="chatbarPlus" title="Attach">+</div>
        <div class="chatbar-mic"  id="chatbarMic"  title="Voice input">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8"  y1="23" x2="16" y2="23"/>
          </svg>
        </div>
        ''',
        unsafe_allow_html=True
    )
    # Zero-height iframe — runs JS in same-origin context to pin buttons onto pill bar
    stcomp.html(
        """
        <script>
        (function() {
          var MAX = 80, n = 0;
          function pin() {
            try {
              var pd   = window.parent.document;
              var pill = pd.querySelector('[data-testid="stChatInput"]');
              var plus = pd.getElementById('chatbarPlus');
              var mic  = pd.getElementById('chatbarMic');
              if (!pill || !plus || !mic) {
                if (++n < MAX) setTimeout(pin, 200);
                return;
              }
              var r    = pill.getBoundingClientRect();
              var btnH = 32;
              var cy   = r.top + (r.height - btnH) / 2;
              // + inside pill on the LEFT
              plus.style.position = 'fixed';
              plus.style.top  = cy + 'px';
              plus.style.left = (r.left + 12) + 'px';
              plus.style.display = 'flex';
              plus.classList.add('ready');
              // mic inside pill on the RIGHT
              mic.style.position = 'fixed';
              mic.style.top  = cy + 'px';
              mic.style.left = (r.right - btnH - 12) + 'px';
              mic.style.display = 'flex';
              mic.classList.add('ready');
              mic.onclick = function() {
                var btn = pd.querySelector('[data-testid="stAudioInput"] button');
                if (btn) { btn.click(); mic.classList.toggle('recording'); }
              };
              window.parent.addEventListener('resize', function(){ setTimeout(pin,100); }, {once:true});
            } catch(e) {}
          }
          pin();
          [300, 800, 1600, 3000].forEach(function(d){ setTimeout(pin, d); });

          // Click anywhere on pill → focus textarea
          function bindPillClick() {
            var pd   = window.parent.document;
            var pill = pd.querySelector('[data-testid="stChatInput"]');
            if (!pill) { setTimeout(bindPillClick, 300); return; }
            pill.addEventListener('click', function(e) {
              var ta = pill.querySelector('textarea');
              if (ta && e.target !== ta) ta.focus();
            });
          }
          setTimeout(bindPillClick, 500);
        })();
        </script>
        """,
        height=0,
        scrolling=False
    )
    question = st.chat_input("Ask about your exams, grades or evaluation...")

    # Use typed question OR pending voice transcription
    voice_question = st.session_state.pop("pending_voice", None)
    active_question = question or voice_question

    if active_question:
        if st.session_state.vectorstore is None:
            st.warning("⚠️ Please upload PDFs and build a knowledge base first (see sidebar).")
        elif st.session_state.groq_client is None:
            st.warning("⚠️ Model not ready. Check your GROQ_API_KEY in the .env file.")
        else:
            handle_question(active_question)

            # Auto-play TTS audio if available
            if st.session_state.get("last_tts_audio"):
                st.markdown(
                    get_audio_player_html(st.session_state.last_tts_audio),
                    unsafe_allow_html=True
                )
                st.session_state.last_tts_audio = None


if __name__ == '__main__':
    main()