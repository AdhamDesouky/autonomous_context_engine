import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def test_retrieval():
    print("Connecting to ChromaDB...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vector_store = Chroma(
        collection_name="technical_docs",
        embedding_function=embeddings,
        persist_directory="./data/vector_store"
    )
    
    query = "IP address subnet"
    results = vector_store.similarity_search(query, k=1)
    
    if results:
        print("\n[SUCCESS] Memory retrieved:")
        print(f"File: {results[0].metadata.get('source_file')} | Page: {results[0].metadata.get('page')}")
        print(f"Content: {results[0].page_content[:200]}...")
    else:
        print("\n[FAIL] No data found. You must re-run ingestion in this new directory:")
        print("uv run python src/autonomous_context_engine/pipeline/ingestion.py")

if __name__ == "__main__":
    test_retrieval()