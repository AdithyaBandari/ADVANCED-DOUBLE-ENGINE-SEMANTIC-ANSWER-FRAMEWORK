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

# Page configuration
st.set_page_config(
    page_title="Semantic Answer Framework",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔍 Advanced Dual Engine Semantic Answer Framework")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Enter your Groq API Key",
        type="password",
        help="Get your API key from https://console.groq.com"
    )
    
    if not api_key:
        st.warning("⚠️ Please enter your Groq API Key to proceed")
    else:
        os.environ['GROQ_API_KEY'] = api_key
    
    # Model selection
    model_option = st.selectbox(
        "Select LLM Model",
        ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        help="Choose which Groq model to use"
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
        "BM25 Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )
    faiss_weight = 1.0 - bm25_weight
    st.write(f"FAISS Weight: {faiss_weight:.1f}")

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = None
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'retrieval_chain' not in st.session_state:
    st.session_state.retrieval_chain = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Cached functions for expensive operations
@st.cache_resource
def get_embedding_model():
    """Cache the embedding model to avoid reloading"""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

@st.cache_resource
def get_llm(api_key, model_name):
    """Cache the LLM to avoid reinitialization"""
    return ChatGroq(
        api_key=api_key,
        model=model_name,
        temperature=0.7
    )

# Main content area
tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "💬 Ask Questions", "📊 Document Info"])

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
            # Clear cached resources
            st.cache_resource.clear()
            st.success("All data cleared!")
    
    if uploaded_files and api_key:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded. Processing...")
        
        if st.button("⚡ Process PDFs", key="process_btn"):
            with st.spinner("Loading and processing PDFs..."):
                try:
                    # Load PDFs
                    documents = []
                    for uploaded_file in uploaded_files:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.getbuffer())
                            tmp_path = tmp_file.name
                        
                        try:
                            loader = PyPDFLoader(tmp_path)
                            documents.extend(loader.load())
                            st.success(f"✅ Loaded: {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"❌ Error loading {uploaded_file.name}: {str(e)}")
                        finally:
                            # Clean up temp file
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                    
                    if not documents:
                        st.error("❌ No documents could be loaded. Please check your PDF files.")
                        st.stop()
                    
                    st.session_state.documents = documents
                    st.info(f"Total pages loaded: {len(documents)}")
                    
                    # Split documents
                    with st.spinner("Splitting documents..."):
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap
                        )
                        chunks = text_splitter.split_documents(documents)
                        st.info(f"Created {len(chunks)} chunks")
                    
                    # Create embeddings
                    with st.spinner("Creating embeddings (this may take a moment)..."):
                        try:
                            embedding_model = get_embedding_model()
                            vector_store = FAISS.from_documents(chunks, embedding_model)
                            st.session_state.vector_store = vector_store
                            st.success("✅ Vector store created")
                        except Exception as e:
                            st.error(f"❌ Embedding error: {str(e)}")
                            st.stop()
                    
                    # Create BM25 retriever
                    with st.spinner("Creating BM25 retriever..."):
                        try:
                            bm25_retriever = BM25Retriever.from_documents(chunks)
                            st.success("✅ BM25 retriever created")
                        except Exception as e:
                            st.error(f"❌ BM25 error: {str(e)}")
                            st.stop()
                    
                    # Create ensemble retriever
                    with st.spinner("Creating ensemble retriever..."):
                        try:
                            ensemble_retriever = EnsembleRetriever(
                                retrievers=[bm25_retriever, vector_store.as_retriever()],
                                weights=[bm25_weight, faiss_weight]
                            )
                            st.success("✅ Ensemble retriever created")
                        except Exception as e:
                            st.error(f"❌ Ensemble retriever error: {str(e)}")
                            st.stop()
                    
                    # Initialize LLM and chain
                    with st.spinner("Initializing LLM and chain..."):
                        try:
                            llm = get_llm(api_key, model_option)
                            
                            prompt = ChatPromptTemplate.from_template("""You are a helpful AI assistant specialized in answering questions about the provided documents.

Answer the question based only on the provided context. Be specific and cite relevant information from the documents.

If the answer cannot be found in the context, clearly state: "I could not find the answer in the uploaded documents."

Context:
{context}

Question: {input}

Answer:""")
                            
                            document_chain = create_stuff_documents_chain(llm, prompt)
                            retrieval_chain = create_retrieval_chain(ensemble_retriever, document_chain)
                            st.session_state.retrieval_chain = retrieval_chain
                            st.success("✅ Retrieval chain initialized")
                        except Exception as e:
                            st.error(f"❌ LLM initialization error: {str(e)}")
                            st.stop()
                    
                    st.success("🎉 All documents processed successfully!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
    
    elif uploaded_files and not api_key:
        st.error("❌ Please enter your Groq API Key first!")

with tab2:
    st.header("💬 Ask Questions")
    
    if st.session_state.retrieval_chain is None:
        st.warning("⚠️ Please upload and process PDF documents first (see Upload & Process tab)")
    else:
        st.info(f"✅ Ready! Your documents are loaded. Ask any question about them.")
        
        # Display chat history
        if st.session_state.chat_history:
            st.subheader("Chat History")
            for i, (question, answer, sources) in enumerate(st.session_state.chat_history):
                with st.container(border=True):
                    col1, col2 = st.columns([0.1, 0.9])
                    with col1:
                        st.write("❓")
                    with col2:
                        st.write(f"**Q:** {question}")
                    
                    st.write(f"**A:** {answer}")
                    if sources:
                        with st.expander("📄 Sources"):
                            for source in sources:
                                st.write(f"- {source}")
                st.divider()
        
        # New question input
        question = st.text_area(
            "Ask a question about your documents:",
            placeholder="e.g., What is semantic search?",
            height=100
        )
        
        col1, col2 = st.columns([4, 1])
        with col2:
            submit_button = st.button("🚀 Ask", type="primary", use_container_width=True)
        
        if submit_button and question:
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
                            sources.add(source)
                    
                    # Add to chat history
                    st.session_state.chat_history.append((question, answer, list(sources)))
                    
                    # Display answer
                    st.success("✅ Answer generated")
                    st.subheader("Answer")
                    st.write(answer)
                    
                    if sources:
                        with st.expander("📄 Sources"):
                            for source in sources:
                                st.write(f"- {source}")
                    
                except Exception as e:
                    st.error(f"❌ Error generating answer: {str(e)}")
        elif submit_button and not question:
            st.warning("⚠️ Please enter a question")

with tab3:
    st.header("📊 Document Information")
    
    if st.session_state.documents is None:
        st.info("No documents loaded yet. Please upload and process PDFs first.")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Pages", len(st.session_state.documents))
        
        with col2:
            total_chars = sum(len(doc.page_content) for doc in st.session_state.documents)
            st.metric("Total Characters", f"{total_chars:,}")
        
        with col3:
            if st.session_state.vector_store:
                st.metric("Vector Store Status", "✅ Ready")
            else:
                st.metric("Vector Store Status", "❌ Not initialized")
        
        st.subheader("Document Details")
        
        # Group documents by source
        docs_by_source = {}
        for doc in st.session_state.documents:
            source = doc.metadata.get('source', 'Unknown')
            if source not in docs_by_source:
                docs_by_source[source] = []
            docs_by_source[source].append(doc)
        
        for source, docs in docs_by_source.items():
            with st.expander(f"📄 {Path(source).name} ({len(docs)} pages)", expanded=False):
                for i, doc in enumerate(docs):
                    page_num = doc.metadata.get('page', i)
                    char_count = len(doc.page_content)
                    st.write(f"**Page {page_num}** ({char_count} characters)")
                    preview = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                    st.write(preview)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Advanced Dual Engine Semantic Answer Framework</strong></p>
    <p>Powered by LangChain, FAISS, BM25, and Groq</p>
    <p style='font-size: 0.85em;'>v2.0 - Optimized for Streamlit Cloud</p>
</div>
""", unsafe_allow_html=True)
