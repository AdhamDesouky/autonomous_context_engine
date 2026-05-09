import streamlit as st
import re
from langchain_core.messages import HumanMessage
from src.autonomous_context_engine.agents.agent import app as agent_app
from src.autonomous_context_engine.pipeline.ingestion import process_uploads

# --- 1. System Configuration ---
st.set_page_config(
    page_title="The ACE Protocol", 
    page_icon="💠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Enterprise Brand CSS ---
# Injects a premium, clean aesthetic using the 'Inter' font (industry standard for UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean, spacious chat bubbles */
    .stChatMessage { 
        border-radius: 6px; 
        padding: 1.5rem; 
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        background-color: rgba(20, 20, 25, 0.4);
    }
    
    /* Hide the default anchor links */
    .css-16iqbz a { display: none; } 
    
    /* Premium Citation Cards */
    .citation-card {
        padding: 16px; 
        border: 1px solid #2A2B32; 
        border-radius: 6px; 
        margin-bottom: 12px; 
        background-color: #121216;
        transition: border-color 0.2s ease;
    }
    .citation-card:hover {
        border-color: #4F46E5; /* Subtle indigo highlight on hover */
    }
    .citation-link {
        color: #818CF8 !important; 
        text-decoration: none; 
        font-weight: 500; 
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .citation-section {
        font-size: 0.8rem; 
        color: #9CA3AF; 
        margin: 8px 0; 
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .citation-snippet {
        font-size: 0.9rem; 
        color: #D1D5DB; 
        border-left: 2px solid #4F46E5; 
        padding-left: 14px; 
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. UI Helpers ---
def render_formatted_sources(source_str):
    """Parses raw tool output into sleek, enterprise-grade citation cards."""
    if not source_str or "--- Result" not in source_str:
        return st.write(source_str)
    
    results = re.split(r'--- Result \d+ ---', source_str)
    
    for res in results:
        if not res.strip(): continue
        
        s_match = re.search(r'Source: (.*?) \(Page (.*?)\)', res)
        c_match = re.search(r'Content: (.*)', res, re.DOTALL)
        
        if s_match and c_match:
            file_name = s_match.group(1).strip()
            page_num = s_match.group(2).strip()
            raw_content = c_match.group(1).strip()
            
            content_lines = raw_content.split('\n')
            section_title = content_lines[0].strip() if content_lines else "Context Origin"
            snippet = '\n'.join(content_lines[1:]).strip()[:400] + "..." 
            
            st.markdown(f"""
            <div class="citation-card">
                <div>
                    <a href="/app/static/{file_name}#page={page_num}" target="_blank" class="citation-link">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        {file_name} (Page {page_num})
                    </a>
                </div>
                <div class="citation-section">Reference: {section_title}</div>
                <div class="citation-snippet">{snippet}</div>
            </div>
            """, unsafe_allow_html=True)

# --- 4. State Management ---
if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- 5. System Operations (Sidebar) ---
with st.sidebar:
    st.markdown("### System Operations")
    st.caption("Manage context vectors and active sessions.")
    st.divider()
    
    st.markdown("##### Knowledge Architecture")
    uploaded_files = st.file_uploader(
        "Upload validated technical documentation", 
        type=["pdf"], 
        accept_multiple_files=True,
        help="Supported formats: PDF. Documents are immediately vectorized."
    )
    
    if uploaded_files:
        if st.button("Synchronize Knowledge Base", type="primary", use_container_width=True):
            with st.spinner("Vectorizing documents and optimizing indexes..."):
                result_message = process_uploads(uploaded_files)
                st.success(result_message)
    
    st.divider()
    if st.button("Flush Session Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("The ACE Protocol v3.1 | Status: Online")

# --- 6. Main Intelligence Interface ---
st.markdown("## 💠 The ACE Protocol")
st.caption("Autonomous Context Engine for secure querying of industrial schematics, manuals, and protocols.")
st.markdown("---")

# Render active session
if not st.session_state.messages:
    # Premium empty state
    st.info("System standing by. Enter a technical query below to initiate the context engine.", icon="ℹ️")

for msg in st.session_state.messages:
    # Use custom avatars based on role
    avatar_icon = "👤" if msg["role"] == "user" else "💠"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("View Authenticated Source Material"):
                render_formatted_sources(msg["sources"])

# --- 7. Execution Engine ---
if prompt := st.chat_input("Query the context engine (e.g., 'Define NAT protocols for S7-1500')..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="💠"):
        res_box = st.empty()
        full_res = ""
        raw_sources = ""
        
        # Professional microcopy for the loading state
        with st.spinner("Cross-referencing technical vectors..."):
            inputs = {"messages": [HumanMessage(content=prompt)]}
            
            for output in agent_app.stream(inputs):
                for key, value in output.items():
                    if key == "tools" and "messages" in value:
                        raw_sources = value["messages"][-1].content
                    
                    if key == "agent" and "messages" in value:
                        msg = value["messages"][-1]
                        if isinstance(msg.content, str): 
                            full_res = msg.content
                        elif isinstance(msg.content, list) and msg.content:
                            full_res = msg.content[0].get('text', '')
                        res_box.markdown(full_res)
        
        if raw_sources:
            with st.expander("View Authenticated Source Material"):
                render_formatted_sources(raw_sources)
            
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_res, 
            "sources": raw_sources
        })