import sys
import io
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
VECTOR_STORE_DIR = BASE_DIR / "data" / "vector_store"

# Initialize Server
mcp = FastMCP("ACE_Memory_Server")

# Connect to Database
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
vector_store = Chroma(
    collection_name="technical_docs",
    embedding_function=embeddings,
    persist_directory=str(VECTOR_STORE_DIR)
)

@mcp.tool()
def query_documentation(query: str, num_results: int = 3) -> str:
    """Search the technical documentation database for engineering specs or maintenance protocols."""
    results = vector_store.similarity_search(query, k=num_results)
    if not results:
        return "No relevant documentation found."
        
    formatted_results = []
    for i, doc in enumerate(results):
        source = doc.metadata.get("source_file", "Unknown")
        page = doc.metadata.get("page", "Unknown")
        formatted_results.append(f"--- Result {i+1} ---\nSource: {source} (Page {page})\nContent: {doc.page_content}\n")
    return "\n".join(formatted_results)

@mcp.tool()
def execute_python_code(script: str) -> str:
    """Execute a Python snippet to calculate metrics or filter arrays. Returns stdout."""
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        exec(script, {})
        output = redirected_output.getvalue()
        return output if output else "Code executed successfully with no output."
    except Exception as e:
        return f"Execution Error: {str(e)}"
    finally:
        sys.stdout = old_stdout

if __name__ == "__main__":
    mcp.run()