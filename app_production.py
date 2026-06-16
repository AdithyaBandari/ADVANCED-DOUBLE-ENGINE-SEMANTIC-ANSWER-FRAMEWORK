"""
Production version of the Semantic Answer Framework
Uses environment variables for API keys instead of UI input
"""

import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
import tempfile
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Semantic Answer Framework - Production",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔍 Advanced Dual Engine Semantic Answer Framework")
st.markdown("*Production Version - Environment-based Configuration*")

# Check for API key in environment
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    st.error("""
    ❌ GROQ_API_KEY environment variable not set!
    
    To run this app, set the environment variable:
    
    **Linux/Mac:**
    ```bash
    export GROQ_API_KEY="your-api-key-here"
    streamlit run app_production.py
    ```
    
    **Windows (PowerShell):**
    ```powershell
    $env:GROQ_API_KEY = "your-api-key-here"
    streamlit run app_production.py
    ```
    
    **Windows (Command Prompt):**
    ```cmd
    set GROQ_API_KEY=your-api-key-here
    streamlit run app_production.py
    ```
    
    Get your API key from: https://console.groq.com/keys
    """)
    st.stop()

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.success("✅ API Key loaded from environment")
    
    # Model selection
    model_option = st.selectbox(
        "Select LLM Model",
        ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        help="Choose which Groq model to use"
    )
    
    # Number of retrieved documents
    num_retrieved = st.slider(
        "Number of Retrieved Documents",
        min_value=1,
        max_value=10,
        value=4,
        help="How many document chunks to retrieve for context"
    )
    
    # Chunk settings
    st.subheader("Text Splitting Settings")
    chunk_size = st.slider(
        "Chunk Size",
        min_value=500,
        max_value=2000,
        value=1000,
        step=100,
        help="Size of text chunks for processing"
    )
    chunk_overlap = st.slider(
        "Chunk Overlap",
        min_value=0,
        max_value=200,
        value=20,
        step=10,
        help="Overlap between chunks"
    )
    
    # Retriever weights
    st.subheader("Retriever Weights")
    bm25_weight = st.slider(
        "BM25 Weight (Keyword Search)",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )
    faiss_weight = 1.0 - bm25_weight
    st.write(f"FAISS Weight (Semantic Search): {faiss_weight:.1f}")
    
    # Temperature
    temperature = st.slider(
        "LLM Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative, Lower = more deterministic"
    )

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = None
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'retrieval_chain' not in st.session_state:
    st.session_state.retrieval_chain = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'ensemble_retriever' not in st.session_state:
    st.session_state.ensemble_retriever = None

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "💬 Ask Questions", "📊 Document Info", "⚙️ API Settings"])

with tab1:
    st.header("Upload PDF Documents")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Upload your PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="You can upload multiple PDF files at once"
        )
    
    with col2:
        if st.button("🔄 Reset All Data", key="reset_btn"):
            st.session_state.documents = None
            st.session_state.vector_store = None
            st.session_state.retrieval_chain = None
            st.session_state.chat_history = []
            st.session_state.ensemble_retriever = None
            st.success("All data cleared!")
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded. Processing...")
        
        if st.button("⚡ Process PDFs", key="process_btn"):
            with st.spinner("Loading and processing PDFs..."):
                try:
                    # Load PDFs
                    documents = []
                    progress_bar = st.progress(0)
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.getbuffer())
                            tmp_path = tmp_file.name
                        
                        try:
                            loader = PyPDFLoader(tmp_path)
                            docs = loader.load()
                            documents.extend(docs)
                            st.success(f"✅ Loaded: {uploaded_file.name} ({len(docs)} pages)")
                            progress_bar.progress((idx + 1) / len(uploaded_files))
                        except Exception as e:
                            st.error(f"❌ Error loading {uploaded_file.name}: {str(e)}")
                        finally:
                            # Clean up temp file
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                    
                    st.session_state.documents = documents
                    st.info(f"Total pages loaded: {len(documents)}")
                    logger.info(f"Loaded {len(documents)} pages from {len(uploaded_files)} files")
                    
                    # Split documents
                    with st.spinner("Splitting documents..."):
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap
                        )
                        chunks = text_splitter.split_documents(documents)
                        st.info(f"Created {len(chunks)} chunks")
                        logger.info(f"Created {len(chunks)} chunks")
                    
                    # Create embeddings
                    with st.spinner("Creating embeddings (this may take a moment)..."):
                        embedding_model = HuggingFaceEmbeddings(
                            model_name="sentence-transformers/all-MiniLM-L6-v2",
                            cache_folder=".cache/embeddings"
                        )
                        vector_store = FAISS.from_documents(chunks, embedding_model)
                        st.session_state.vector_store = vector_store
                        st.success("✅ Vector store created")
                        logger.info("Vector store created successfully")
                    
                    # Create BM25 retriever
                    with st.spinner("Creating BM25 retriever..."):
                        bm25_retriever = BM25Retriever.from_documents(chunks)
                        st.success("✅ BM25 retriever created")
                        logger.info("BM25 retriever created")
                    
                    # Create ensemble retriever
                    with st.spinner("Creating ensemble retriever..."):
                        ensemble_retriever = EnsembleRetriever(
                            retrievers=[bm25_retriever, vector_store.as_retriever()],
                            weights=[bm25_weight, faiss_weight]
                        )
                        st.session_state.ensemble_retriever = ensemble_retriever
                        st.success("✅ Ensemble retriever created")
                        logger.info("Ensemble retriever created")
                    
                    # Initialize LLM and chain
                    with st.spinner("Initializing LLM and chain..."):
                        llm = ChatGroq(
                            api_key=api_key,
                            model=model_option,
                            temperature=temperature
                        )
                        
                        prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant specialized in answering questions about the provided documents.

Your task is to provide accurate, helpful answers based ONLY on the information in the provided context.

Guidelines:
- Answer only from the provided context
- Be specific and cite relevant information when possible
- If the answer cannot be found in the documents, clearly state: "I could not find the answer in the provided documents."
- Keep answers concise but complete
- If relevant, mention which document or section the information comes from

Context:
{context}

Question:
{input}

Answer:
""")
                        
                        document_chain = create_stuff_documents_chain(llm, prompt)
                        retrieval_chain = create_retrieval_chain(ensemble_retriever, document_chain)
                        st.session_state.retrieval_chain = retrieval_chain
                        st.success("✅ Retrieval chain initialized")
                        logger.info("Retrieval chain initialized")
                    
                    st.success("🎉 All documents processed successfully!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error processing documents: {str(e)}")
                    logger.error(f"Error processing documents: {str(e)}", exc_info=True)

with tab2:
    st.header("💬 Ask Questions")
    
    if st.session_state.retrieval_chain is None:
        st.warning("⚠️ Please upload and process PDF documents first (see Upload & Process tab)")
    else:
        st.info(f"✅ Ready! Your documents are loaded. Ask any question about them.")
        
        # Display chat history in collapsible section
        if st.session_state.chat_history:
            with st.expander(f"📜 Chat History ({len(st.session_state.chat_history)} messages)", expanded=False):
                for i, (question, answer, sources) in enumerate(st.session_state.chat_history):
                    st.markdown(f"**Q{i+1}: {question}**")
                    st.write(answer)
                    if sources:
                        st.caption(f"📄 Sources: {', '.join(sources)}")
                    st.divider()
        
        # New question input
        question = st.text_area(
            "Ask a question about your documents:",
            placeholder="e.g., What are the main topics covered in these documents?",
            height=100,
            key="question_input"
        )
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col2:
            if st.button("🚀 Ask", type="primary", use_container_width=True):
                submit = True
            else:
                submit = False
        
        with col3:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        if submit and question:
            with st.spinner("Searching and generating answer..."):
                try:
                    response = st.session_state.retrieval_chain.invoke(
                        {"input": question}
                    )
                    
                    answer = response.get("answer", "No answer generated")
                    
                    # Extract sources from context
                    sources = set()
                    for doc in response.get("context", []):
                        if hasattr(doc, 'metadata'):
                            source = doc.metadata.get('source', 'Unknown source')
                            sources.add(Path(source).name)
                    
                    # Add to chat history
                    st.session_state.chat_history.append((question, answer, list(sources)))
                    logger.info(f"Question processed: {question[:50]}...")
                    
                    # Display answer
                    st.success("✅ Answer generated")
                    st.subheader("Answer")
                    st.write(answer)
                    
                    if sources:
                        st.divider()
                        with st.expander("📄 Document Sources"):
                            for source in sources:
                                st.write(f"- {source}")
                    
                except Exception as e:
                    st.error(f"❌ Error generating answer: {str(e)}")
                    logger.error(f"Error generating answer: {str(e)}", exc_info=True)
        
        elif submit and not question:
            st.warning("⚠️ Please enter a question")

with tab3:
    st.header("📊 Document Information")
    
    if st.session_state.documents is None:
        st.info("No documents loaded yet. Please upload and process PDFs first.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pages", len(st.session_state.documents))
        
        with col2:
            total_chars = sum(len(doc.page_content) for doc in st.session_state.documents)
            st.metric("Total Characters", f"{total_chars:,}")
        
        with col3:
            total_words = sum(len(doc.page_content.split()) for doc in st.session_state.documents)
            st.metric("Total Words", f"{total_words:,}")
        
        with col4:
            if st.session_state.vector_store:
                st.metric("Vector Store", "✅ Ready")
            else:
                st.metric("Vector Store", "❌ Not Ready")
        
        st.subheader("Document Details")
        
        # Group documents by source
        docs_by_source = {}
        for doc in st.session_state.documents:
            source = doc.metadata.get('source', 'Unknown')
            if source not in docs_by_source:
                docs_by_source[source] = []
            docs_by_source[source].append(doc)
        
        for source, docs in docs_by_source.items():
            source_name = Path(source).name
            total_chars = sum(len(doc.page_content) for doc in docs)
            
            with st.expander(f"📄 {source_name} ({len(docs)} pages, {total_chars:,} chars)", expanded=False):
                for i, doc in enumerate(docs):
                    page_num = doc.metadata.get('page', i)
                    char_count = len(doc.page_content)
                    st.write(f"**Page {page_num}** ({char_count} characters)")
                    
                    content_preview = doc.page_content[:300]
                    if len(doc.page_content) > 300:
                        content_preview += "..."
                    
                    st.caption(content_preview)

with tab4:
    st.header("⚙️ API Settings & Usage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Environment Configuration")
        st.write("""
        This app is configured to use environment variables for security.
        
        **Set before running:**
        ```bash
        export GROQ_API_KEY="your-key-here"
        streamlit run app_production.py
        ```
        """)
        
        if api_key:
            masked_key = api_key[:10] + "..." + api_key[-4:]
            st.success(f"✅ API Key configured: {masked_key}")
    
    with col2:
        st.subheader("Current Settings")
        st.write(f"**Model:** {model_option}")
        st.write(f"**Temperature:** {temperature}")
        st.write(f"**Retrieved Docs:** {num_retrieved}")
    
    st.subheader("Usage Statistics")
    if st.session_state.chat_history:
        st.write(f"**Total Questions Asked:** {len(st.session_state.chat_history)}")
        
        # Estimate token usage
        total_input_tokens = sum(len(q.split()) * 1.3 for q, _, _ in st.session_state.chat_history)
        total_output_tokens = sum(len(a.split()) * 1.3 for _, a, _ in st.session_state.chat_history)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estimated Input Tokens", f"{int(total_input_tokens):,}")
        with col2:
            st.metric("Estimated Output Tokens", f"{int(total_output_tokens):,}")
        with col3:
            st.metric("Total Estimated", f"{int(total_input_tokens + total_output_tokens):,}")
    else:
        st.info("No questions asked yet")
    
    st.subheader("Performance Tips")
    st.markdown("""
    - Adjust **Chunk Size** based on document type
    - Tune **Retriever Weights** for your use case
    - Monitor **Temperature** for consistency vs. creativity
    - Check **Groq Console** for actual API usage
    """)

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.caption("🔍 Semantic Answer Framework")
with col2:
    st.caption("Environment-based Production Version")
with col3:
    if st.button("ℹ️ About", key="about_btn"):
        st.info("""
        **Advanced Dual Engine Semantic Answer Framework**
        
        This production version uses environment variables for API configuration
        and includes enhanced logging and security features.
        
        **Tech Stack:**
        - LangChain for orchestration
        - FAISS for semantic search
        - BM25 for keyword search
        - Groq API for fast LLM inference
        - HuggingFace embeddings
        
        **Features:**
        - Dual retrieval: semantic + keyword search
        - Production-ready configuration
        - Environment-based security
        - Usage statistics
        - Chat history
        """)
