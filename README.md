
# ACE // Operational Intelligence

ACE (Autonomous Context Engine) is an agentic Retrieval-Augmented Generation (RAG) system designed for querying industrial schematics, technical manuals, and standard operating protocols. It leverages a LangGraph agent architecture to dynamically route queries, execute Python code for calculations, and retrieve heavily cited context from technical documents.

## Core Architecture
* **Frontend:** Streamlit with custom enterprise UI styling.
* **Agent Framework:** LangGraph.
* **LLM:** Google Gemini 3.1 Flash-Lite.
* **Vector Store:** ChromaDB.
* **Document Processing:** PyMuPDFLoader with `RecursiveCharacterTextSplitter`.

## Features
* **Dynamic Ingestion:** Upload technical PDFs directly through the UI. The pipeline automatically checks for duplicates, extracts metadata, and vectorizes content.
* **Verifiable Citations:** Responses include structured citation cards. The system serves static files locally, allowing users to click a reference and instantly view the exact page in the original PDF.
* **Python Sandbox:** The agent is equipped with a Python execution tool to perform complex hardware calculations or data processing directly within the chat interface.
* **Persistent Memory:** Utilizes SQLite checkpointers to maintain operational context across long diagnostic sessions.

## Project Structure
```text
autonomous_context_engine/
├── .streamlit/
│   └── config.toml           # Streamlit static server configuration
├── data/
│   └── vector_store/         # Persistent ChromaDB storage
├── static/                   # Raw PDF manuals for static serving
├── src/
│   └── autonomous_context_engine/
│       ├── agents/
│       │   └── agent.py      # LangGraph state graph and tool definitions
│       ├── pipeline/
│       │   └── ingestion.py  # PyMuPDF document loading and embedding logic
│       └── ui/
│           └── app.py        # Streamlit interface and execution loop

```

## Setup & Installation

**1. Clone the repository**

```bash
git clone [https://github.com/yourusername/autonomous_context_engine.git](https://github.com/yourusername/autonomous_context_engine.git)
cd autonomous_context_engine

```

**2. Configure Environment Variables**
Create a `.env` file in the root directory and add your required API keys.

```env
GOOGLE_API_KEY=your_gemini_api_key

```

**3. Enable Static File Serving**
Ensure the `.streamlit/config.toml` file exists with the following configuration:

```toml
[server]
enableStaticServing = true

```

**4. Create the Static Directory Link**
To allow Streamlit to securely serve the PDFs, ensure your raw PDFs are located in `data/raw/` and create a directory junction (Windows) or symlink (macOS/Linux) in the directory where `app.py` resides.

*Windows PowerShell (Run from project root):*

```powershell
New-Item -ItemType Junction -Path "src\autonomous_context_engine\ui\static" -Target "E:\Absolute\Path\To\data\raw"

```

## Usage

Start the Streamlit server:

```bash
$env:PYTHONPATH = "."; uv run streamlit run src/autonomous_context_engine/ui/app.py

```

1. Access the dashboard at `http://localhost:8501`.
2. Expand the sidebar to upload technical manuals (PDFs).
3. Click "Synchronize Knowledge Base" to vectorize the documents.
4. Input queries in the main interface to retrieve cited technical guidance or execute operational calculations.
