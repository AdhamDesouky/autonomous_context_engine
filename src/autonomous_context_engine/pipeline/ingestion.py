import os
import tempfile
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"

# Initialize Embeddings & Vector Store globally for reuse
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
vector_store = Chroma(
    collection_name="technical_docs",
    embedding_function=embeddings,
    persist_directory=str(VECTOR_STORE_DIR)
)

def get_indexed_files() -> set:
    """Returns a set of filenames already present in the database."""
    results = vector_store.get(include=['metadatas'])
    if not results or not results['metadatas']:
        return set()
    return {m.get("source_file") for m in results['metadatas'] if m}

def process_uploads(uploaded_files) -> str:
    """
    Main entry point for Streamlit UI.
    Processes a list of UploadedFile objects and adds them to Chroma.
    """
    if not uploaded_files:
        return "No files provided."

    indexed_files = get_indexed_files()
    new_docs = []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    for uploaded_file in uploaded_files:
        if uploaded_file.name in indexed_files:
            continue # Skip files already in the database

        # 1. Save buffer to temp file for PyMuPDFLoader
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            # 2. Load with your preferred loader
            loader = PyMuPDFLoader(tmp_path)
            docs = loader.load()
            
            # 3. Enforce metadata
            for doc in docs:
                doc.metadata["source_file"] = uploaded_file.name
                if "page" not in doc.metadata:
                    doc.metadata["page"] = -1
            
            # 4. Split into chunks
            chunks = text_splitter.split_documents(docs)
            new_docs.extend(chunks)
        finally:
            os.remove(tmp_path) # Clean up disk

    # 5. Batch Add to DB
    if new_docs:
        vector_store.add_documents(new_docs)
        return f"✅ Successfully indexed {len(new_docs)} new chunks from {len(uploaded_files)} files."
    
    return "ℹ️ All uploaded files were already present in the database."

# Keep your original run_pipeline for CLI/Manual usage
def run_pipeline():
    RAW_DATA_DIR = BASE_DIR / "data" / "raw"
    if not RAW_DATA_DIR.exists(): return
        
    pdf_files = list(RAW_DATA_DIR.glob("*.pdf"))
    all_docs = []
    
    # Simple logic: load everything that isn't indexed
    indexed = get_indexed_files()
    for pdf in pdf_files:
        if pdf.name not in indexed:
            print(f"Processing: {pdf.name}")
            loader = PyMuPDFLoader(str(pdf))
            docs = loader.load()
            for d in docs: d.metadata["source_file"] = pdf.name
            all_docs.extend(docs)

    if all_docs:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(all_docs)
        vector_store.add_documents(chunks)
        print(f"Ingested {len(chunks)} chunks.")
    else:
        print("Database is already up to date.")

if __name__ == "__main__":
    run_pipeline()