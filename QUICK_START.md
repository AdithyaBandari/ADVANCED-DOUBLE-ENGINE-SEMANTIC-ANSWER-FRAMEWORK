# ⚡ Quick Start Guide

## 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# 3. Open browser at http://localhost:8501
```

## 2-Minute First Run

1. **Get API Key**
   - Go to https://console.groq.com
   - Click "API Keys" → "Create New API Key"
   - Copy the key

2. **Upload Documents**
   - In the app, paste API key in sidebar
   - Go to "Upload & Process" tab
   - Click "Upload your PDF files"
   - Select 1+ PDFs from your computer
   - Click "Process PDFs" button
   - Wait for ✅ success message

3. **Ask Questions**
   - Go to "Ask Questions" tab
   - Type your question
   - Click "Ask" button
   - Read the answer!

## One-Page Reference

### Configuration (Sidebar)

| Setting | Default | Range | Notes |
|---------|---------|-------|-------|
| Groq API Key | — | Required | Get from groq.com |
| LLM Model | llama-3.1-8b | 3 options | Fast vs Powerful tradeoff |
| Chunk Size | 1000 | 500-2000 | Bigger = more context |
| Chunk Overlap | 20 | 0-200 | Prevent info loss |
| BM25 Weight | 0.5 | 0.0-1.0 | Keyword search strength |

### Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Submit question | Ctrl/Cmd + Enter |
| Focus question box | Tab to text area |
| Clear input | Select all + Delete |

### Tab Guide

| Tab | Purpose |
|-----|---------|
| 📤 Upload | Load PDFs and configure |
| 💬 Ask | Question & answer interface |
| 📊 Info | View document statistics |

## Common Questions in 10 Seconds

**Q: Where's my API key?**
→ https://console.groq.com/keys

**Q: Why is it slow?**
→ First run downloads embedding model (2-5 min), then it's fast

**Q: Can I upload multiple files?**
→ Yes! Select multiple files in the upload dialog

**Q: Will my data be saved?**
→ No! Click "Reset All Data" to clear everything

**Q: What if the answer is wrong?**
→ Check document content in "Document Info" tab

**Q: Can I change the LLM?**
→ Yes! Dropdown in the sidebar

**Q: Is it free?**
→ Groq has a free tier with limits

**Q: Do I need GPU?**
→ No! CPU works fine (slower is all)

## File Structure

```
your-project/
├── app.py                           # Main Streamlit app
├── requirements.txt                 # Python dependencies
├── README.md                        # Full documentation
├── QUICK_START.md                   # This file
└── TIPS_AND_BEST_PRACTICES.md      # Advanced tips
```

## Environment Setup (Windows)

```powershell
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run app
streamlit run app.py
```

## Environment Setup (Mac/Linux)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run app
streamlit run app.py
```

## Recommended Settings by Use Case

### Research Papers
```
Chunk Size: 1200
Chunk Overlap: 50
BM25 Weight: 0.3
Model: mixtral-8x7b
```

### Technical Documentation
```
Chunk Size: 800
Chunk Overlap: 30
BM25 Weight: 0.7
Model: llama-3.1-8b
```

### General Text
```
Chunk Size: 1000
Chunk Overlap: 20
BM25 Weight: 0.5
Model: llama-3.1-8b (default)
```

### Legal Documents
```
Chunk Size: 1500
Chunk Overlap: 100
BM25 Weight: 0.8
Model: mixtral-8x7b
```

## Troubleshooting in 30 Seconds

**App won't start**
```bash
pip install --upgrade streamlit
streamlit run app.py
```

**ImportError: No module**
```bash
pip install -r requirements.txt --upgrade
```

**Slow processing**
→ Reduce chunk size or use fewer PDFs

**Poor answers**
→ Adjust BM25/FAISS weights or rephrase questions

**API errors**
→ Check API key at https://console.groq.com/keys

## Cost Estimate

| Document Count | Avg Questions | Est. Cost |
|---|---|---|
| 5 small PDFs | 10 questions | ~$0.01 |
| 20 medium PDFs | 50 questions | ~$0.05 |
| 100 large PDFs | 200 questions | ~$0.20 |

*Based on Groq free tier limits. Actual cost varies by model.*

## Next Steps

1. ✅ Install and run the app
2. ✅ Upload some test PDFs
3. ✅ Ask a few questions
4. ✅ Adjust settings based on results
5. ✅ Read TIPS_AND_BEST_PRACTICES.md for advanced usage

## Support Resources

| Resource | Link |
|----------|------|
| Groq Docs | https://console.groq.com/docs |
| Streamlit Help | https://docs.streamlit.io |
| LangChain Guide | https://python.langchain.com |
| GitHub Issues | Create an issue in repo |

---

**Ready to go? → `streamlit run app.py` 🚀**
