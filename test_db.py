from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Connect to the existing database
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
vector_store = Chroma(
    collection_name="technical_docs",
    embedding_function=embeddings,
    persist_directory="./data/vector_store"
)

# Run a test query
query = "What is the maximum voltage?"
results = vector_store.similarity_search(query, k=1) # Get the top 1 result

if results:
    print(f"Found on Page: {results[0].metadata.get('page')}")
    print(f"Source File: {results[0].metadata.get('source_file')}")
    print(f"Content: {results[0].page_content}")
else:
    print("No results found. Database might be empty.")