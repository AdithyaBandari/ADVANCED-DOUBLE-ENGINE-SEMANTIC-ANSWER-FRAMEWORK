# 💡 Tips & Best Practices

## Query Tips

### Effective Questions
✅ **Good Questions:**
- "What are the main topics covered in these documents?"
- "Explain the process described in Chapter 3"
- "What statistics are mentioned about climate change?"
- "How does X relate to Y according to the documents?"

❌ **Avoid:**
- Vague questions: "Tell me everything"
- Questions outside document scope
- Questions that require external knowledge

### Question Techniques
1. **Be Specific**: More specific questions get better answers
   - ❌ "What is this about?"
   - ✅ "What are the key findings in the research methodology section?"

2. **Ask Follow-ups**: Use chat history to build context
   - Ask an initial question, then ask "Can you explain more about X?"

3. **Reference Sections**: If you know where info is
   - ✅ "According to page 5, what does it say about..."

4. **Multi-part Questions**: Can work well
   - ✅ "What is X and how does it work?"

## Document Preparation

### PDF Quality
- **Quality matters**: Clear, scannable PDFs work best
- **Avoid**: Scanned images without OCR (text must be extractable)
- **Check**: Verify PDFs have selectable text before uploading

### Document Organization
- **Size**: Mix of small and large documents works fine
- **Quantity**: 5-10 documents is ideal; 50+ may be slow
- **Relevance**: More relevant documents = better answers

### Optimal Chunk Settings
| Document Type | Chunk Size | Overlap | Notes |
|---|---|---|---|
| Technical Papers | 1000-1200 | 20-50 | Preserve equations and context |
| Legal Documents | 800-1000 | 50-100 | Important to preserve section context |
| General Text | 1000 | 20 | Default works well |
| Code Documentation | 600-800 | 20 | Smaller chunks for code blocks |

## Retriever Weights Guide

### Use Cases

**Exact Match Heavy (75% BM25, 25% FAISS)**
- Legal documents with specific clauses
- Technical specifications with exact terms
- FAQ-like documents

**Semantic Understanding (25% BM25, 75% FAISS)**
- Abstract concepts and theories
- Literature and prose
- Cross-domain understanding

**Balanced (50% BM25, 50% FAISS)** ← Recommended Default
- General documents
- Mixed content types
- When unsure

**Experimenting**: Try different weights and see which gives better results for your use case!

## Performance Optimization

### For Faster Processing
1. **Reduce chunk size** to 750 (faster but less context)
2. **Increase chunk overlap** to 100 (preserve connections)
3. **Use fewer documents** (process in batches)
4. **Choose faster model**: llama-3.1-8b-instant over mixtral

### For Better Quality Answers
1. **Increase chunk size** to 1200-1500 (more context)
2. **Reduce chunk overlap** to 10 (cleaner chunks)
3. **Use more documents** (richer information)
4. **Choose stronger model**: mixtral-8x7b over faster options

### Memory Management
- Close other applications while running
- Process one batch of PDFs at a time
- Clear cache between sessions if needed: "Reset All Data" button

## Cost Management

### Groq API Pricing
- Free tier available with rate limits
- Monitor your usage in Groq console
- Each API call has a cost

### Cost Reduction
1. **Shorter queries** = lower tokens = lower cost
2. **Fewer questions** per batch = fewer API calls
3. **Smaller chunk overlap** = fewer tokens to process
4. **Cache results** by using chat history

### Monitor Usage
```
Approximate tokens per query:
- Small question: 100-500 tokens
- Medium question: 500-1000 tokens  
- Large question: 1000-2000 tokens
```

## Troubleshooting Common Issues

### "I could not find the answer in the uploaded documents"
**Causes:**
- Question is outside document scope
- Document doesn't contain relevant information
- Query is too vague

**Solutions:**
- Ask more specific questions
- Check document content in Tab 3
- Rephrase question using document terminology
- Verify PDFs were processed correctly

### Slow Response Time
**Causes:**
- Large chunk size slows embedding
- Many documents to search
- Network latency with Groq API

**Solutions:**
- Wait (first embedding load takes longer)
- Reduce number of documents
- Use smaller chunks
- Check internet connection

### Poor Answer Quality
**Causes:**
- Weights not optimal for your documents
- Chunk size too small/large
- Question poorly phrased

**Solutions:**
- Adjust BM25/FAISS weights
- Try different chunk sizes (800-1200)
- Rephrase questions with keywords from docs
- Use longer, more specific questions

### API Key Errors
**Causes:**
- Invalid or expired API key
- Rate limit exceeded
- Wrong API key format

**Solutions:**
- Get fresh key from groq.com
- Wait before making new requests
- Copy key carefully without spaces
- Check API usage limit

## Advanced Usage

### Using with Different LLM Providers
To swap Groq for another LLM (e.g., OpenAI):

```python
# Replace this:
from langchain_groq import ChatGroq
llm = ChatGroq(api_key=api_key, model=model_option)

# With this:
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(api_key=api_key, model="gpt-4")
```

### Custom System Prompts
Modify the prompt template to change behavior:

```python
prompt = ChatPromptTemplate.from_template("""
You are a specialized [field] expert.
Your task is to [specific instruction].
Format your answer as [desired format].

Context: {context}
Question: {input}
Answer:
""")
```

### Batch Processing
For processing many documents:
```python
# Process in groups of 10 PDFs
for i in range(0, len(all_pdfs), 10):
    batch = all_pdfs[i:i+10]
    # Process batch
```

### Logging & Debugging
Enable LangChain debug logging:
```python
import langchain
langchain.debug = True
```

## Data Privacy & Security

### Best Practices
1. **Never share API keys** - treat like passwords
2. **Don't upload confidential data** to public instances
3. **Use environment variables** for credentials:
   ```bash
   export GROQ_API_KEY="your-key-here"
   ```
4. **Run locally** for sensitive documents
5. **Clear session** when done (Reset button)

### For Production Deployment
- Use Streamlit Cloud with environment variables
- Implement access controls
- Log user activity
- Encrypt sensitive documents
- Use VPN for private instances

## Integration Ideas

### Extend the App
1. **Add database storage** for chat history
2. **Export results** to PDF/Word
3. **Team collaboration** with shared documents
4. **Analytics dashboard** for usage tracking
5. **API endpoint** for programmatic access
6. **Multi-user support** with user accounts
7. **Document versioning** and updates
8. **Custom embeddings** for specialized domains

### Integration with Other Tools
- Slack bot for Q&A
- Discord integration
- Email notifications for results
- Webhook for automation
- REST API wrapper

## Monitoring & Maintenance

### Regular Checks
- Monitor API costs weekly
- Check error logs for issues
- Update dependencies monthly
- Test with new PDFs regularly
- Clear old chat history

### Maintenance Commands
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Clear cache
rm -rf ~/.cache/huggingface/

# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## FAQ

**Q: Can I use my own embedding model?**
A: Yes! Replace the HuggingFace model name in the code.

**Q: Will my documents be stored?**
A: Only in your session memory. Reset clears everything.

**Q: Can I use this offline?**
A: Yes, except you need internet for Groq API calls.

**Q: How accurate are the answers?**
A: Depends on document quality, chunks, and LLM. 85-95% accuracy typical.

**Q: Can I upload non-English documents?**
A: Yes! HuggingFace embeddings support 50+ languages.

**Q: How long does processing take?**
A: 100 pages typically takes 2-5 minutes depending on settings.

**Q: Can I combine different PDF sources?**
A: Absolutely! All documents are indexed together.

---

**Happy exploring! 🎉**
