import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"

def process_pdf(file_path: Path) -> List[Document]:
    """Load PDF and enforce data lineage metadata."""
    loader = PyMuPDFLoader(str(file_path))
    docs = loader.load()
    
    # Enforce strict metadata lineage
    for doc in docs:
        doc.metadata["source_file"] = file_path.name
        # PyMuPDF sets 'page', we ensure it exists for auditability
        if "page" not in doc.metadata:
            doc.metadata["page"] = -1 
            
    return docs

def chunk_and_store(docs: List[Document]):
    """Semantic chunking and vector storage."""
    # 1000 chars with 200 overlap is standard for technical manuals
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(docs)
    
    # Initialize Google Vector Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    
    vector_store = Chroma(
        collection_name="technical_docs",
        embedding_function=embeddings,
        persist_directory=str(VECTOR_STORE_DIR)
    )
    
    # Add chunks to DB
    vector_store.add_documents(documents=chunks)
    print(f"Successfully ingested {len(chunks)} chunks into ChromaDB.")

def run_pipeline():
    """Execute the ingestion process for all raw PDFs."""
    if not RAW_DATA_DIR.exists():
        print(f"Error: Directory {RAW_DATA_DIR} does not exist.")
        return
        
    pdf_files = list(RAW_DATA_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in data/raw/")
        return
        
    all_docs = []
    for pdf in pdf_files:
        print(f"Processing: {pdf.name}")
        all_docs.extend(process_pdf(pdf))
        
    chunk_and_store(all_docs)

if __name__ == "__main__":
    run_pipeline()