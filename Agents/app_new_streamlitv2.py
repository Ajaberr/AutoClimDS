import streamlit as st
import sys
import os
import time
import json
import re
import zipfile
import io as _io
from typing import Dict, Any

# Load AWS + API credentials from .env before any agent imports
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

# --- Configuration ---
# 🔒 Security Configuration
# Add allowed emails here. They must also end with @columbia.edu
ALLOWED_EMAILS = [
    "your-uni@columbia.edu",
]

# Import agents
# Note: Ensure these are in the python path or same directory
try:
    from climate_research_orchestrator_new_V1 import create_climate_research_orchestrator
    import climate_research_orchestrator_new_V1 as _orch_module
except ImportError:
    st.error("Could not import agents. Please ensure you are running this from the 'Agents/Final' directory.")
    st.stop()

# --- Page Config ---
st.set_page_config(
    page_title="AutoClimDS: Climate Research Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Authentication Logic ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

import uuid
from datetime import datetime

def check_login():
    """Display login screen and handle authentication"""
    st.markdown("""
        <style>
            .stApp {
                background-color: #f0f2f6;
            }
            .login-container {
                max-width: 400px;
                margin: auto;
                padding: 2rem;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 AutoClimDS Login")
        st.markdown("Please sign in with your **Columbia University** email.")
        
        email = st.text_input("Email Address", placeholder="uni@columbia.edu")
        
        if st.button("Sign In", use_container_width=True, type="primary"):
            if not email:
                st.error("Please enter an email address.")
                return
            
            # Normalize email
            email_check = email.strip().lower()
            
            # Validation Logic
            is_columbia = email_check.endswith("@columbia.edu")
            is_allowed = email_check in [e.lower() for e in ALLOWED_EMAILS]
            
            if is_columbia and is_allowed:
                st.session_state.authenticated = True
                st.session_state.user_email = email_check  # Store email for logging
                
                # --- Session & Concurrency Initialization ---
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.session_start_time = datetime.now()
                
                # Token Accumulators
                st.session_state.session_tokens = {
                    'input': 0,
                    'output': 0,
                    'total': 0,
                    'cost': 0.0
                }
                
                # File Isolation Checkpoints
                # We record the time of login. 
                # Files modified AFTER this time are considered "new" for this session.
                st.session_state.file_scan_start_time = time.time()
                st.session_state.my_files = [] # List of files generated in this session
                
                st.toast("✅ Login successful! Redirecting...", icon="🎉")
                time.sleep(1)
                st.rerun()
            elif not is_columbia:
                 st.error("❌ Access denied. You must use a valid @columbia.edu email address.")
            else:
                 st.error("❌ Access denied. Your email is not in the allowed list.")

if not st.session_state.authenticated:
    check_login()
    st.stop()  # Stop execution here if not authenticated

# ==============================================================================
# MAIN APPLICATION (Authenticated)
# ==============================================================================

# --- Custom Callback Handler ---
from langchain.callbacks.base import BaseCallbackHandler

class SafeStreamlitCallbackHandler(BaseCallbackHandler):
    """
    A robust callback handler that logs agent actions to a Streamlit container
    without crashing on missing 'Thoughts' or malformed chains.
    """
    def __init__(self, parent_container):
        self.container = parent_container.empty()
        self.text_log = ""
        self.status = None
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: list[str], **kwargs: Any) -> None:
        pass # Too verbose to show raw prompts

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        tool_name = serialized.get("name", "Unknown Tool")
        
        # Create or update status expander
        if self.status:
            self.status.update(label=f"✅ Finished: {self.status_label}", state="complete")
        
        self.status_label = f"Using tool: **{tool_name}**"
        self.status = self.container.status(self.status_label, expanded=True)
        self.status.write(f"**Input:** `{input_str}`")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        if self.status:
            self.status.write(f"**Output:** {output[:4000]}..." if len(output) > 4000 else f"**Output:** {output}")
            self.status.update(label=f"✅ Completed: {self.status_label}", state="complete", expanded=False)
            self.status = None

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        if self.status:
            self.status.write(f"❌ **Error:** {str(error)}")
            self.status.update(label=f"❌ Failed: {self.status_label}", state="error")
            self.status = None

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Capture token usage from LLM response"""
        try:
            # Check for usage in llm_output
            if hasattr(response, 'llm_output') and response.llm_output:
                usage = response.llm_output.get('token_usage', {})
                model_id = response.llm_output.get('model_id', 'unknown')
                
                if usage:
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)
                    total_tokens = input_tokens + output_tokens
                    
                    # --- Cost Calculation (Dummy/Estimated) ---
                    # Claude 3 Sonnet pricing (approx): Input $3/1M, Output $15/1M
                    input_cost = (input_tokens / 1_000_000) * 3.0
                    output_cost = (output_tokens / 1_000_000) * 15.0
                    total_cost = input_cost + output_cost
                    
                    # --- CUMULATIVE UPDATE ---
                    st.session_state.session_tokens['input'] += input_tokens
                    st.session_state.session_tokens['output'] += output_tokens
                    st.session_state.session_tokens['total'] += total_tokens
                    st.session_state.session_tokens['cost'] += total_cost
                    
                    # Log to CSV with Cumulative Stats
                    self._log_usage_to_csv(
                        input_tokens, output_tokens, total_tokens, total_cost, model_id,
                        st.session_state.session_tokens # Pass cumulative dict
                    )
                    
                    # Display usage in UI
                    if self.status:
                         msg = f"💰 **Token Usage:** {total_tokens} (Total this session: {st.session_state.session_tokens['total']} | Est Cost: ${st.session_state.session_tokens['cost']:.5f})"
                         self.status.write(msg)

        except Exception as e:
            # Don't break the app just for logging
            print(f"Error logging token usage: {e}")

    def _log_usage_to_csv(self, input_t, output_t, total_t, cost, model, cumulative):
        """Append usage stats to CSV file"""
        import csv
        from datetime import datetime
        
        log_file = "token_usage_log.csv"
        file_exists = os.path.isfile(log_file)
        
        try:
            user_email = st.session_state.get('user_email', 'unknown')
            session_id = st.session_state.get('session_id', 'unknown')
            
            with open(log_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        "Timestamp", "Session_ID", "Email", "Model", 
                        "Input_Tokens", "Output_Tokens", "Total_Tokens", "Cost_Est_USD",
                        "Cumulative_Input", "Cumulative_Output", "Cumulative_Total", "Cumulative_Cost"
                    ])
                
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    session_id,
                    user_email,
                    model,
                    input_t,
                    output_t,
                    total_t,
                    f"{cost:.6f}",
                    cumulative['input'],
                    cumulative['output'],
                    cumulative['total'],
                    f"{cumulative['cost']:.6f}"
                ])
        except Exception as e:
            print(f"Failed to write to CSV: {e}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        if self.status:
            self.status.update(state="complete")



# --- State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am the AutoClimDS Orchestrator. detailed research."}
    ]
    # Add initial greeting detailed
    st.session_state.messages[0]["content"] = """
    👋 **Welcome to AutoClimDS!**
    
    I can help you with:
    - 🛰️ **NASA Satellite Data** (MODIS, GOES)
    - 🌪️ **FEMA Disaster Records** (Floods, Hurricanes)
    - 🏙️ **City 311 Service Requests** (NYC, Chicago, SF)
    - 🖥️ **Climate Simulations** (ERA5, CMIP6)
    
    Simply describe what you need, for example:
    > *"Find flood disaster declarations in Texas for 2021"*
    > *"Download ERA5 temperature data for NYC in July 2023"*
    """

if "agent" not in st.session_state:
    st.session_state.agent = None

# --- Helper Functions ---
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

def remove_emojis(text):
    """Remove emojis and non-latin characters for FPDF compatibility"""
    if not text:
        return ""
    # Keep only common ASCII and Latin-1 printable characters
    # This is a safe subset for basic FPDF without font pack complications
    return text.encode('latin-1', 'ignore').decode('latin-1')

def create_pdf_report(messages, files_list):
    """Generate a PDF report of the conversation and files"""
    if not FPDF:
        return None

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'AutoClimDS Research Report', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)

    # 1. Conversation History
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Conversation Transcript", 0, 1)
    pdf.ln(5)

    for msg in messages:
        role = msg['role'].upper()
        content = msg['content'] or ""

        # Clean markdown wrappers for cleaner text
        content = content.replace('**', '').replace('__', '').replace('`', '')
        # Remove emojis/unsafe chars
        content = remove_emojis(content)
        
        pdf.set_font("Arial", 'B', 10)
        # Colors: Assistant=Blue, User=Green
        pdf.set_text_color(0, 0, 128) if role == 'ASSISTANT' else pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 8, f"[{role}]", 0, 1)
        
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, content)
        pdf.ln(3)

    # 2. Files Generated
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Generated Research Files", 0, 1)
    pdf.ln(5)
    
    if files_list:
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, "The following files were generated/accessed. Paths are absolute for local navigation:")
        pdf.ln(3)
        for f in files_list:
            # Use abspath if available
            abs_path = remove_emojis(f.get('path', f['name']))
            pdf.cell(0, 8, f"- {abs_path}", 0, 1) 
    else:
        pdf.cell(0, 8, "No specific data files detected.", 0, 1)

    return pdf.output(dest='S').encode('latin-1')


def create_memory_md(messages):
    sid = st.session_state.get("session_id", "unknown")
    email = st.session_state.get("user_email", "unknown")
    tokens = st.session_state.get("session_tokens", {})
    lines = [
        "# AutoClimDS Session Memory", "",
        f"**Session ID:** `{sid}`",
        f"**User:** {email}",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Tokens used:** {tokens.get('total', 0):,}  |  **Cost:** ${tokens.get('cost', 0):.3f}",
        "", "---", "", "## Conversation", "",
    ]
    for msg in messages:
        role = "**User**" if msg["role"] == "user" else "**Assistant**"
        lines.append(f"### {role}")
        lines.append(msg["content"].strip())
        lines.append("")
    return "\n".join(lines).encode("utf-8")


def create_jupyter_notebook(messages):
    cells = [{
        "cell_type": "markdown", "metadata": {},
        "source": [f"# AutoClimDS Research Notebook\nSession: {st.session_state.get('session_id', 'unknown')}  \nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"]
    }]
    code_block_re = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)
    for msg in messages:
        if msg["role"] != "assistant":
            continue
        code_blocks = code_block_re.findall(msg["content"])
        text_only = code_block_re.sub("", msg["content"]).strip()
        if text_only:
            cells.append({"cell_type": "markdown", "metadata": {}, "source": [text_only]})
        for code in code_blocks:
            cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [code.strip()]})
    nb = {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.10.0"}},
        "cells": cells
    }
    return json.dumps(nb, indent=2).encode("utf-8")


def create_session_zip(messages, session_id, include_memory=True, include_data=True, include_notebook=True):
    buf = _io.BytesIO()
    scan_start = st.session_state.get("file_scan_start_time", 0)
    search_dirs = ['.', 'era5_data', 'cmip6_out', 'downloads', 'fema_data', 'us_311_data',
                   'floodnet_downloads', 'floodsimbench_downloads', 'mrms_downloads', 'outputs']
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if include_memory:
            zf.writestr(f"{session_id}_memory.md", create_memory_md(messages))
        if include_notebook:
            zf.writestr(f"{session_id}_notebook.ipynb", create_jupyter_notebook(messages))
        zf.writestr(f"{session_id}_session.json", json.dumps({
            "session_id": session_id,
            "user_email": st.session_state.get("user_email", "unknown"),
            "messages": messages,
            "metrics": st.session_state.get("session_tokens", {})
        }, indent=2))
        if include_data:
            added = set()
            for d in search_dirs:
                if not os.path.exists(d):
                    continue
                for fname in os.listdir(d):
                    fpath = os.path.join(d, fname)
                    if fname in added or not os.path.isfile(fpath):
                        continue
                    if os.path.getmtime(fpath) >= scan_start:
                        try:
                            zf.write(fpath, arcname=f"data/{fname}")
                            added.add(fname)
                        except Exception:
                            pass
    buf.seek(0)
    return buf.read()


def initialize_agent():
    """Initialize the orchestrator agent and store in session state"""
    try:
        agent = create_climate_research_orchestrator()
        if agent:
            st.session_state.agent = agent
            return True
        return False
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return False

def show_generated_files():
    """Show files generated during THIS session only"""
    files_found = []
    
    # Get scan start time
    scan_start = st.session_state.get('file_scan_start_time', 0)
    
    with st.sidebar:
        st.divider()
        st.subheader("📂 My Session Files")
        all_dirs = ['.', 'era5_data', 'cmip6_out', 'downloads', 'fema_data', 'us_311_data',
                    'floodnet_downloads', 'floodsimbench_downloads', 'mrms_downloads']

        found_count = 0
        for directory in all_dirs:
            if os.path.isdir(directory):
                try:
                    for root, dirs, filenames in os.walk(directory):
                        for filename in filenames:
                            full_path = os.path.join(root, filename)
                            if (os.path.isfile(full_path)
                                    and not filename.startswith('_')
                                    and not filename.endswith('.py')
                                    and not filename.endswith('.md')):
                                mtime = os.path.getmtime(full_path)
                                if mtime >= scan_start:
                                    st.caption(f"📄 `{filename}`")
                                    with open(full_path, "rb") as f:
                                        st.download_button("⬇️", f, file_name=filename, key=full_path)
                                    found_count += 1
                                    files_found.append({'name': filename, 'path': full_path, 'dir': root})
                except:
                    pass
        if found_count == 0:
            st.caption("*No new files generated in this session.*")
            
    return files_found

# --- UI Layout ---
st.title("🌍 AutoClimDS: Intelligent Research Assistant")

# Sidebar
# Add specific Logout button if authenticated
with st.sidebar:
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    st.divider()

    st.header("⚙️ Configuration")

    _jupyter_on = st.toggle("LAMBDA", value=False, key="jupyter_kernel_toggle")
    if _jupyter_on:
        os.environ["AUTOCLIMDS_JUPYTER_MODE"] = "1"
    else:
        os.environ.pop("AUTOCLIMDS_JUPYTER_MODE", None)

    # Credential Inputs (Safe fallback if env vars missing)
    with st.expander("🔑 API Credentials (Optional)"):
        st.caption("If not set in `.env`, enter keys here.")
        st.session_state['auth_earthdata_username'] = st.text_input("Earthdata Username")
        st.session_state['auth_earthdata_password'] = st.text_input("Earthdata Password", type="password")
        st.session_state['auth_noaa_token'] = st.text_input("NOAA CDO Token", type="password")
    
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.agent = None
        st.rerun()
    
    # Recent files and catch the list
    recent_files = show_generated_files()
    
    # PDF Download
    if FPDF:
        st.divider()
        if st.checkbox("Prepare PDF Report"):
            pdf_bytes = create_pdf_report(st.session_state.messages, recent_files)
            if pdf_bytes:
                st.download_button(
                    label="📄 Download Discussion PDF",
                    data=pdf_bytes,
                    file_name="AutoClimDS_Report.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("Install 'fpdf' to enable PDF export.")

    st.divider()
    st.subheader("💾 Session Memory")

    with st.expander("📦 Save Session", expanded=False):
        _inc_mem  = st.checkbox("Memory summary (.md)",       value=True, key="save_inc_mem")
        _inc_data = st.checkbox("Downloaded data files",       value=True, key="save_inc_data")
        _inc_nb   = st.checkbox("Jupyter notebook (.ipynb)",   value=True, key="save_inc_nb")
        if st.button("Build ZIP", use_container_width=True, key="save_session_zip_btn"):
            _sid = st.session_state.get("session_id", "session")
            with st.spinner("Packaging session…"):
                try:
                    _zip = create_session_zip(st.session_state.messages, _sid,
                                              include_memory=_inc_mem,
                                              include_data=_inc_data,
                                              include_notebook=_inc_nb)
                    st.session_state["_session_zip_bytes"] = _zip
                    st.session_state["_session_zip_name"] = f"{_sid}_autoclimds.zip"
                except Exception as e:
                    st.error(f"Failed to build ZIP: {e}")
        if st.session_state.get("_session_zip_bytes"):
            st.download_button(
                "⬇️ Download ZIP",
                st.session_state["_session_zip_bytes"],
                st.session_state.get("_session_zip_name", "session.zip"),
                "application/zip",
                use_container_width=True,
                key="dl_session_zip"
            )

    with st.expander("📂 Load Session", expanded=False):
        _uploaded_zip = st.file_uploader("Upload session ZIP", type=["zip"], key="load_session_zip_uploader")
        if _uploaded_zip and st.button("Restore Session", use_container_width=True, key="restore_session_btn"):
            try:
                zf = zipfile.ZipFile(_io.BytesIO(_uploaded_zip.read()))
                json_files = [n for n in zf.namelist() if n.endswith("_session.json")]
                if json_files:
                    data = json.loads(zf.read(json_files[0]))
                    st.session_state.messages = data.get("messages", st.session_state.messages)
                    st.session_state["session_tokens"] = data.get("metrics", st.session_state.get("session_tokens", {}))
                    st.success("Session restored! Scroll up to see conversation history.")
                    st.rerun()
                else:
                    st.error("No session JSON found in ZIP.")
            except Exception as e:
                st.error(f"Failed to restore session: {e}")

# --- Main Chat Interface ---

# 1. Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 2. Handle User Input
if prompt := st.chat_input("What is your research question?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Agent Execution
    with st.chat_message("assistant"):
        # Initialize agent if needed
        if not st.session_state.agent:
            if not initialize_agent():
                st.error("Agent initialization failed. Please check logs.")
                st.stop()
        
        # Container for tool outputs (status updates)
        tool_container = st.container()
        callback = SafeStreamlitCallbackHandler(tool_container)
        
        try:
            _orch_module._LAMBDA_CONTEXT = list(st.session_state.messages)

            # Run the agent with the user's prompt
            # We use 'invoke' which maintains chain history if memory is configured in the agent
            response = st.session_state.agent.invoke(
                {"input": prompt},
                {"callbacks": [callback]}
            )
            
            output_text = response.get("output") or "I successfully processed your request."
            
            # Display Final Answer
            st.markdown(output_text)
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
        except Exception as e:
            error_msg = f"❌ An error occurred: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
