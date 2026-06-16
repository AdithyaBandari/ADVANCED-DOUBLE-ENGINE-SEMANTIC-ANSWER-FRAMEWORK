# 🔍 Advanced Dual Engine Semantic Answer Framework - Streamlit App

A powerful Streamlit application that implements a dual-engine semantic search and retrieval-augmented generation (RAG) system. It combines **BM25 keyword search** with **FAISS vector similarity search** to provide highly relevant answers to questions about your documents.

## ✨ Features

- **Dual-Engine Retrieval**: Combines BM25 (keyword-based) and FAISS (semantic vector) retrieval
- **PDF Upload & Processing**: Upload multiple PDF files with automatic text extraction
- **Intelligent Chunking**: Configurable text splitting with customizable chunk size and overlap
- **Groq LLM Integration**: Uses high-speed Groq API with multiple model options
- **Interactive Q&A**: Ask questions about your documents with source attribution
- **Chat History**: Track conversation history with source citations
- **Document Statistics**: View detailed information about loaded documents
- **Configurable Settings**: Adjust weights, models, and processing parameters

## 🚀 Quick Start

### 1. Clone or Download the Files

```bash
cd your-project-directory
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Your Groq API Key

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Generate a new API key
4. Keep it safe (you'll need it to run the app)

### 5. Run the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Tab 1: Upload & Process

1. **Enter API Key**: Paste your Groq API key in the sidebar configuration
2. **Configure Settings** (optional):
   - Select LLM model (llama-3.1-8b-instant, mixtral, or gemma2)
   - Adjust chunk size (500-2000 characters)
   - Set chunk overlap (0-200)
   - Configure retriever weights (BM25 vs FAISS)
3. **Upload PDFs**: Upload one or multiple PDF files
4. **Process**: Click "Process PDFs" to load and index your documents

**What happens during processing:**
- PDFs are extracted and split into chunks
- HuggingFace embeddings are created for semantic search
- FAISS vector store is built for fast similarity search
- BM25 index is created for keyword search
- Both retrievers are combined with configurable weights

### Tab 2: Ask Questions

1. **Type Your Question**: Enter a question about your documents
2. **Get Answer**: Click "Ask" to retrieve and generate an answer
3. **View Sources**: See which documents provided the answer
4. **Track History**: All questions and answers are saved in the chat history

**Features:**
- Answers are sourced only from your documents
- If the answer isn't found, the AI explicitly states this
- Sources are cited for transparency
- Chat history is maintained during the session

### Tab 3: Document Information

- **Statistics**: Total pages, characters, and vector store status
- **Document Details**: View page-by-page content from each uploaded PDF
- **Source Attribution**: See exactly which documents were indexed

## ⚙️ Configuration Options

### Text Splitting Settings
- **Chunk Size**: Larger chunks (1200-2000) preserve context but reduce granularity
- **Chunk Overlap**: Prevents losing information at chunk boundaries

### Retriever Weights
- **BM25 Weight**: Good for exact keyword matching
- **FAISS Weight**: Good for semantic understanding
- Default 50/50 split works well for most use cases
- Adjust based on your document type and needs

### LLM Models
- **llama-3.1-8b-instant**: Fast, good quality (recommended)
- **mixtral-8x7b-32768**: More powerful, slower
- **gemma2-9b-it**: Good balance, instruction-tuned

## 🏗️ Architecture

```
User PDF Files
       ↓
   PyPDFLoader
       ↓
   Text Splitting (RecursiveCharacterTextSplitter)
       ↓
    ┌──────────────────────────────────────┐
    │       Create Embeddings              │
    │  (HuggingFace Transformers)          │
    └──────────────────────────────────────┘
       ↓                    ↓
   FAISS Vector Store   BM25 Retriever
       ↓                    ↓
    └──────────────────────────────────────┘
               Ensemble Retriever
                       ↓
                  Groq LLM
                       ↓
                   Answer with Sources
```

## 📊 How It Works

1. **Document Loading**: PDFs are loaded and text is extracted
2. **Chunking**: Text is split into overlapping chunks to maintain context
3. **Embedding**: Each chunk is converted to a semantic vector using sentence transformers
4. **Dual Indexing**:
   - FAISS stores vectors for semantic similarity search
   - BM25 creates an inverted index for keyword search
5. **Ensemble Retrieval**: Both retrievers are queried and results are combined
6. **LLM Generation**: The top retrieved chunks are passed to Groq LLM with a prompt
7. **Answer Generation**: LLM generates a coherent answer with source attribution

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: For production, use environment variables instead of UI input
- **API Usage**: Monitor your Groq API usage to avoid unexpected charges

## 🛠️ Troubleshooting

### ImportError: No module named 'langchain_classic'
```bash
pip install --upgrade langchain langchain-classic
```

### FAISS GPU issues
The requirements file uses `faiss-cpu`. For GPU support:
```bash
pip uninstall faiss-cpu
pip install faiss-gpu
```

### Out of Memory with Large PDFs
- Reduce chunk size
- Process fewer documents at a time
- Use a machine with more RAM

### Slow Performance
- The first time loading the embedding model takes longer
- Subsequent runs cache the model
- Reduce the number of retrieved documents in the code if needed

## 📝 Customization

### Add a New LLM Model
Edit the model selection in the sidebar:
```python
model_option = st.selectbox(
    "Select LLM Model",
    ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it", "your-new-model"],
)
```

### Change the Prompt Template
Modify the `ChatPromptTemplate.from_template()` section in the "Ask Questions" tab.

### Use Different Embeddings
Replace `sentence-transformers/all-MiniLM-L6-v2` with another HuggingFace model:
```python
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
```

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [BM25 Explanation](https://en.wikipedia.org/wiki/Okapi_BM25)

## 🤝 Contributing

Feel free to modify and extend this application for your needs!

## 📄 License

This project is provided as-is for educational and commercial use.

## 🎯 Key Improvements Over Original Notebook

✅ **Web UI**: Interactive Streamlit interface instead of notebook cells  
✅ **Dynamic File Upload**: Upload PDFs through the UI instead of hardcoded paths  
✅ **Session Management**: Document state is preserved during the session  
✅ **Configuration UI**: Adjust parameters without editing code  
✅ **Chat History**: Track conversation history  
✅ **Error Handling**: Comprehensive error messages and validation  
✅ **Security**: API key is not hardcoded  
✅ **Performance**: Caching and efficient retrieval  
✅ **User Experience**: Organized tabs, progress indicators, and visual feedback  

---

**Happy Searching! 🚀**
