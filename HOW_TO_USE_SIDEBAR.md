# 📖 How to Use the Sidebar

## 🎯 Quick Guide

The sidebar is your control panel for the Education Examination Explainer Bot. Here's everything you need to know!

---

## 📍 Where is the Sidebar?

### Desktop/Laptop
- **Location**: Left side of the screen
- **Toggle**: Click the **`>`** arrow in the top-left corner
- **Default**: Should be **expanded** (visible) when you first open the app

### Mobile/Tablet
- **Location**: Slides in from the left
- **Toggle**: Tap the **☰** (hamburger menu) in the top-left
- **Default**: Collapsed to save screen space

---

## 🎛️ Sidebar Sections

### 1️⃣ Step 1 — Upload Academic Documents
**What it does**: Upload your exam regulation PDFs

**How to use**:
1. Click **"Browse files"** button
2. Select one or more PDF files
3. Click **"Open"**
4. You'll see: "📎 X document(s) selected"

**Then**:
- Click **"🔨 Build KB"** to process the PDFs
- Or click **"📂 Load KB"** to load previously saved knowledge base

**What happens**:
- PDFs are read and text is extracted
- Text is split into chunks
- Chunks are converted to embeddings
- Knowledge base is created and saved
- You'll see: "📚 Academic Knowledge Base Successfully Built!"

---

### 2️⃣ Step 2 — Choose AI Model
**What it does**: Select which AI model to use for answering questions

**Available models**:
- **Llama 3.3 70B** (Default) - Best quality answers
- **Llama 3.1 8B (Fast)** - Fastest responses
- **Mixtral 8x7B** - Good for long documents
- **Gemma2 9B** - Lightweight option

**How to use**:
1. Click the dropdown menu
2. Select your preferred model
3. Model changes immediately

**Tip**: Start with Llama 3.3 70B for best results!

---

### 3️⃣ Step 3 — Settings
**What it does**: Fine-tune how the AI generates answers

#### Generation Parameters (Click to expand)

**Temperature** (0.0 - 1.0)
- **Lower (0.0-0.3)**: More focused, precise answers
- **Higher (0.7-1.0)**: More creative, varied answers
- **Default**: 0.0 (most accurate for exam info)

**Top-P** (0.0 - 1.0)
- Controls diversity of word choices
- **Default**: 0.95 (good balance)
- **Tip**: Keep at default unless experimenting

**Max Tokens** (256 - 8192)
- Maximum length of the answer
- **Default**: 2048 (about 1500 words)
- **Increase**: For longer, detailed answers
- **Decrease**: For shorter, concise answers

#### Retrieval Settings (Click to expand)

**Chunks to retrieve** (1 - 10)
- How many document sections to search
- **Default**: 2 chunks
- **More chunks**: Broader context, slower
- **Fewer chunks**: Faster, more focused

---

### 4️⃣ Step 4 — Voice
**What it does**: Enable/disable text-to-speech for answers

**Toggle**: 🔊 Read answers aloud
- **ON**: Bot will speak answers (uses gTTS)
- **OFF**: Text only (faster)

**How to use voice input**:
1. Click the **microphone icon** in the chat input
2. Allow browser microphone access
3. Speak your question clearly
4. Wait for transcription
5. Question is automatically sent

---

### 📊 Status Dashboard
**What it shows**: Current state of your knowledge base

**When no KB loaded**:
- ○ No Knowledge Base — Upload PDFs above

**When KB loaded**:
- ● Academic Knowledge Base Ready
- **Documents**: Number of PDFs processed
- **Chunks**: Number of text chunks created
- **Model**: Currently selected AI model
- **Temperature**: Current temperature setting

---

### ⚖️ Academic Integrity Notice
**Important reminder**: This bot is for explaining exam processes only

**Will NOT**:
- ❌ Predict or estimate grades
- ❌ Solve exam questions
- ❌ Provide model answers
- ❌ Assist with academic dishonesty

**Use responsibly and ethically!**

---

### 🗑️ Clear Chat Button
**What it does**: Clears all chat history

**How to use**:
1. Click **"🗑️ Clear Chat"**
2. All messages are deleted
3. Knowledge base remains loaded
4. You can start fresh conversation

**Note**: This does NOT delete your uploaded PDFs or knowledge base!

---

## 🎬 Step-by-Step Workflow

### First Time Setup (5 minutes)

1. **Open Sidebar** (if collapsed)
   - Click `>` arrow in top-left

2. **Upload PDFs**
   - Click "Browse files"
   - Select exam regulation PDFs
   - Click "Open"

3. **Build Knowledge Base**
   - Click "🔨 Build KB"
   - Wait 30-60 seconds
   - See success message

4. **Choose Model** (Optional)
   - Keep default "Llama 3.3 70B"
   - Or select faster model

5. **Start Asking Questions!**
   - Type in chat input at bottom
   - Press Enter
   - Get answers!

---

### Regular Usage (30 seconds)

1. **Open App**
   - Knowledge base auto-loads

2. **Check Status**
   - Sidebar shows "● Knowledge Base Ready"

3. **Ask Questions**
   - Type or speak your question
   - Get instant answers

4. **Adjust Settings** (if needed)
   - Change model for speed
   - Adjust temperature for creativity

---

## 💡 Pro Tips

### Tip 1: Keep Sidebar Open
- Easier to monitor status
- Quick access to settings
- See what's loaded

### Tip 2: Build KB Once
- Knowledge base is saved automatically
- No need to rebuild every time
- Just click "📂 Load KB" next time

### Tip 3: Use Fast Model for Quick Questions
- Switch to "Llama 3.1 8B (Fast)"
- Get answers in 1-2 seconds
- Good for simple questions

### Tip 4: Increase Chunks for Complex Questions
- Go to Retrieval Settings
- Increase to 4-5 chunks
- Better for multi-part questions

### Tip 5: Lower Temperature for Accuracy
- Keep at 0.0 for exam information
- Prevents hallucinations
- Most accurate answers

---

## 🐛 Common Issues

### Issue: Sidebar Not Visible
**Solution**: Click the `>` arrow in top-left corner

### Issue: Can't Upload PDFs
**Solution**: 
- Check file is actually a PDF
- File size should be < 100MB
- Try different PDF

### Issue: Build KB Fails
**Solution**:
- Check PDF has readable text (not just images)
- Try uploading one PDF at a time
- Check error message for details

### Issue: Settings Don't Change
**Solution**:
- Make sure you moved the slider
- Settings apply to next question
- Try asking a new question

### Issue: Status Shows "No Knowledge Base"
**Solution**:
- Upload PDFs first
- Click "🔨 Build KB"
- Wait for success message

---

## 📱 Mobile Usage

### Opening Sidebar on Mobile
1. Tap **☰** menu in top-left
2. Sidebar slides in from left
3. Use all controls normally
4. Tap outside sidebar to close

### Tips for Mobile
- Sidebar auto-closes after selection
- Use voice input for easier typing
- Rotate to landscape for more space
- Pinch to zoom if text is small

---

## ⌨️ Keyboard Shortcuts

- **Enter**: Send message
- **Shift+Enter**: New line in message
- **Ctrl+K**: Focus chat input (some browsers)
- **Esc**: Close sidebar (some browsers)

---

## 🎨 Customization

### Want to Change Sidebar Width?
Edit `.streamlit/config.toml`:
```toml
[ui]
sidebarWidth = 300  # Adjust number
```

### Want Different Colors?
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"  # Accent color
secondaryBackgroundColor = "#262730"  # Sidebar color
```

---

## ✅ Checklist: Am I Using Sidebar Correctly?

- [ ] Sidebar is visible (expanded)
- [ ] I uploaded at least one PDF
- [ ] I clicked "🔨 Build KB"
- [ ] Status shows "● Knowledge Base Ready"
- [ ] I selected an AI model
- [ ] I can see all sections (Steps 1-4, Status, etc.)
- [ ] I can ask questions and get answers
- [ ] I know how to clear chat if needed

---

## 🆘 Need More Help?

### Documentation
- **SIDEBAR_FIX.md** - Technical details about sidebar
- **QUICKSTART.md** - Quick start guide
- **README.md** - Full project documentation

### Support
- Check browser console (F12) for errors
- Try different browser (Chrome, Firefox, Edge)
- Clear browser cache and refresh
- Create GitHub issue if problem persists

---

## 🎉 You're Ready!

Now you know everything about using the sidebar. Go ahead and:
1. Upload your exam PDFs
2. Build your knowledge base
3. Start asking questions
4. Get accurate answers!

**Happy learning!** 📚✨

---

**Guide Version**: 1.0  
**Last Updated**: May 11, 2026  
**For**: Education Examination Explainer Bot
