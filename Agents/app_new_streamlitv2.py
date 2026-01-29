import streamlit as st
import sys
import os
import time
from typing import Dict, Any

# --- Configuration ---
# 🔒 Security Configuration
# Add allowed emails here. They must also end with @columbia.edu
ALLOWED_EMAILS = [
    "check@columbia.edu",
    "ar4982@columbia.edu", 
]

# Import agents
# Note: Ensure these are in the python path or same directory
try:
    from climate_research_orchestrator_new_V1 import create_climate_research_orchestrator
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
        content = msg['content']
        
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
        # Directories to scan
        search_dirs = ['.', 'era5_data', 'cmip6_out', 'downloads', 'fema_data', 'us_311_data']
        
        found_count = 0
        for directory in search_dirs:
            if os.path.isdir(directory):
                try:
                    for filename in os.listdir(directory):
                        full_path = os.path.join(directory, filename)
                        if os.path.isfile(full_path) and not filename.startswith('_') and not filename.endswith('.py') and not filename.endswith('.md'):
                             # CONCURRENCY FIX: 
                             # Only show files modified AFTER the session started (login time)
                             # This effectively isolates this user's session view from old files or other users' files
                             mtime = os.path.getmtime(full_path)
                             if mtime >= scan_start:
                                st.caption(f"📄 `{filename}`")
                                with open(full_path, "rb") as f:
                                    st.download_button("⬇️", f, file_name=filename, key=full_path)
                                found_count += 1
                                files_found.append({'name': filename, 'path': full_path, 'dir': directory})
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
            # Run the agent with the user's prompt
            # We use 'invoke' which maintains chain history if memory is configured in the agent
            response = st.session_state.agent.invoke(
                {"input": prompt},
                {"callbacks": [callback]}
            )
            
            output_text = response.get("output", "I successfully processed your request.")
            
            # Display Final Answer
            st.markdown(output_text)
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
        except Exception as e:
            error_msg = f"❌ An error occurred: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
