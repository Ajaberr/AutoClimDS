import streamlit as st
import sys
import os
import time
import json
import re
import zipfile
import shutil
import requests
import io as _io
from typing import Dict, Any
from datetime import datetime, date
import uuid
import threading

# Load AWS + API credentials from .env before any agent imports
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

# --- Configuration & Paths ---
BASE_DATA_DIR = os.getenv("AUTO_CLIM_DATA_DIR", ".")
CONFIG_FILE = os.path.join(BASE_DATA_DIR, "user_config.json")
LOG_FILE = os.path.join(BASE_DATA_DIR, "token_usage_log.csv")
SESSIONS_DIR = os.path.join(BASE_DATA_DIR, "sessions")
ADMIN_DEFAULT_PASS = "admin123"

_config_lock = threading.Lock()

import hashlib

def hash_password(password: str) -> str:
    """Hash password string using SHA-256"""
    if not password:
        return ""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify plaintext password against stored SHA-256 hash"""
    if not password or not hashed:
        return False
    return hash_password(password) == hashed

def load_config():
    """Load user configuration with password store support"""
    default_conf = {
        "allowed_emails": ["ayon.roy@columbia.edu", "ar4982@columbia.edu", "trial@columbia.edu"],
        "admin_email": "ayon.roy@columbia.edu",
        "users": {}
    }
    if not os.path.exists(CONFIG_FILE):
        save_config(default_conf)
        return default_conf
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = {}
            if "allowed_emails" not in data:
                data["allowed_emails"] = ["ayon.roy@columbia.edu", "ar4982@columbia.edu", "trial@columbia.edu"]
            return data
    except Exception:
        return default_conf

def save_config(config_data):
    """Save configuration (Thread-Safe)"""
    with _config_lock:
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

config = load_config()

# Import agents
try:
    from climate_research_orchestrator_new_V1 import create_climate_research_orchestrator
    import climate_research_orchestrator_new_V1 as _orch_module
except ImportError:
    st.error("Could not import agents. Please ensure climate_research_orchestrator_new_V1.py is available.")
    st.stop()

# --- Page Config ---
st.set_page_config(
    page_title="AutoClimDS: Climate Research Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Authentication & Session State ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# Persistent Session Auto-Recovery from Query Params
qp_user = st.query_params.get("user")
qp_admin = st.query_params.get("admin") == "true"
if not st.session_state.authenticated and qp_user:
    config_tmp = load_config()
    allowed_emails = [e.lower() for e in config_tmp.get("allowed_emails", [])]
    users_dict = config_tmp.get("users", {})
    admin_email = config_tmp.get("admin_email", "ayon.roy@columbia.edu").lower()
    
    if qp_user.lower() in allowed_emails or qp_user.lower() in users_dict or qp_user.lower() == admin_email:
        st.session_state.authenticated = True
        st.session_state.user_email = qp_user.lower()
        st.session_state.is_admin = qp_admin or (qp_user.lower() == admin_email)
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        if "session_start_time" not in st.session_state:
            st.session_state.session_start_time = datetime.now()
        if "session_tokens" not in st.session_state:
            st.session_state.session_tokens = {'input': 0, 'output': 0, 'total': 0, 'cost': 0.0}
        if "file_scan_start_time" not in st.session_state:
            st.session_state.file_scan_start_time = time.time()
        if "my_files" not in st.session_state:
            st.session_state.my_files = []

def save_session_snapshot():
    """Save current session state to disk for Admin & User inspection (only if user messages exist)"""
    try:
        msgs = st.session_state.get("messages", [])
        has_user_msg = any(m.get("role") == "user" for m in msgs)
        if not has_user_msg:
            return  # Do not store empty sessions without actual user conversation
            
        if not os.path.exists(SESSIONS_DIR):
            os.makedirs(SESSIONS_DIR, exist_ok=True)
            
        sid = st.session_state.get("session_id")
        if not sid or sid == "unknown":
            sid = str(uuid.uuid4())
            st.session_state["session_id"] = sid
            
        session_data = {
            "session_id": sid,
            "session_name": st.session_state.get("session_name", ""),
            "user_email": st.session_state.get("user_email", "unknown"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "messages": msgs,
            "token_usage": st.session_state.get("session_tokens", {})
        }
        
        filename = os.path.join(SESSIONS_DIR, f"{sid}.json")
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(session_data, f, indent=4, default=str)
    except Exception as e:
        print(f"Failed to save session snapshot: {e}")

def get_session_files(session_id: str, full_session_data: dict = None):
    """Find all files associated with a specific session ID via UUID, message parsing, or creation time"""
    files_found = []
    seen_paths = set()
    
    search_dirs = [
        BASE_DATA_DIR,
        os.path.join(BASE_DATA_DIR, 'era5_data'),
        os.path.join(BASE_DATA_DIR, 'downloads'),
        os.path.join(BASE_DATA_DIR, 'fema_data'),
        os.path.join(BASE_DATA_DIR, 'us_311_data'),
        os.path.join(BASE_DATA_DIR, 'outputs'),
        os.path.join(BASE_DATA_DIR, 'uploads'),
        os.path.join(BASE_DATA_DIR, 'mrms_downloads'),
        os.path.join(BASE_DATA_DIR, 'cmip6_out'),
        os.path.join(SESSIONS_DIR, session_id)
    ]
    
    # 1. Match files containing session_id in filename or folder path
    for d in search_dirs:
        if os.path.exists(d):
            try:
                for f in os.listdir(d):
                    fp = os.path.abspath(os.path.join(d, f))
                    if os.path.isfile(fp) and fp not in seen_paths:
                        if session_id and (session_id in f or session_id in fp):
                            if not f.endswith(('.py', '.pyc', '.jsonl', '.db', '.log', '.toml', '.pem')):
                                size_mb = os.path.getsize(fp) / (1024 * 1024)
                                ext = os.path.splitext(f)[1].lower()
                                files_found.append({
                                    "name": f,
                                    "path": fp,
                                    "size_mb": f"{size_mb:.2f} MB",
                                    "type": ext
                                })
                                seen_paths.add(fp)
            except Exception: pass

    # 2. Extract filenames mentioned in message content or attachments
    messages_list = []
    if full_session_data and "messages" in full_session_data:
        messages_list = full_session_data["messages"]
    elif "messages" in st.session_state:
        messages_list = st.session_state.messages
        
    for m in messages_list:
        content = str(m.get("content", ""))
        # Find all filename patterns in content (e.g. texas_flood_disasters_2021.csv, nyc_rain.png)
        found_names = re.findall(r'([a-zA-Z0-9_.-]+\.(?:csv|nc|png|jpg|jpeg|pdf|xlsx|grib|geojson|tif|tiff))', content)
        for fn in found_names:
            if fn.endswith(('.py', '.pyc', '.jsonl', '.db', '.log', '.toml', '.pem', '.json')):
                continue
            for d in search_dirs:
                cand_path = os.path.abspath(os.path.join(d, fn))
                if os.path.isfile(cand_path) and cand_path not in seen_paths:
                    size_mb = os.path.getsize(cand_path) / (1024 * 1024)
                    ext = os.path.splitext(fn)[1].lower()
                    files_found.append({
                        "name": fn,
                        "path": cand_path,
                        "size_mb": f"{size_mb:.2f} MB",
                        "type": ext
                    })
                    seen_paths.add(cand_path)

        for attached_fp in m.get("files", []):
            if os.path.exists(attached_fp):
                fp = os.path.abspath(attached_fp)
                if os.path.isfile(fp) and fp not in seen_paths:
                    fn = os.path.basename(fp)
                    size_mb = os.path.getsize(fp) / (1024 * 1024)
                    ext = os.path.splitext(fn)[1].lower()
                    files_found.append({
                        "name": fn,
                        "path": fp,
                        "size_mb": f"{size_mb:.2f} MB",
                        "type": ext
                    })
                    seen_paths.add(fp)

    # 3. Match files created/modified during the active session duration
    session_start_time = st.session_state.get("file_scan_start_time", 0)
    if session_start_time > 0:
        for d in search_dirs:
            if os.path.exists(d):
                try:
                    for f in os.listdir(d):
                        fp = os.path.abspath(os.path.join(d, f))
                        if os.path.isfile(fp) and fp not in seen_paths:
                            if not f.endswith(('.py', '.pyc', '.jsonl', '.db', '.log', '.toml', '.pem', '.json')):
                                if os.path.getmtime(fp) >= (session_start_time - 10):
                                    size_mb = os.path.getsize(fp) / (1024 * 1024)
                                    ext = os.path.splitext(f)[1].lower()
                                    files_found.append({
                                        "name": f,
                                        "path": fp,
                                        "size_mb": f"{size_mb:.2f} MB",
                                        "type": ext
                                    })
                                    seen_paths.add(fp)
                except Exception: pass

    # Include session JSON summary
    sess_json = os.path.abspath(os.path.join(SESSIONS_DIR, f"{session_id}.json"))
    if os.path.isfile(sess_json) and sess_json not in seen_paths:
        size_mb = os.path.getsize(sess_json) / (1024 * 1024)
        files_found.append({
            "name": f"{session_id}.json",
            "path": sess_json,
            "size_mb": f"{size_mb:.2f} MB",
            "type": ".json"
        })
        seen_paths.add(sess_json)

    return files_found

def create_session_zip(messages, session_id, session_name="", include_memory=True, include_data=True, include_notebook=True):
    # Ensure current snapshot is saved
    save_session_snapshot()
    
    zip_buffer = _io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        if include_memory:
            session_json = json.dumps({
                "session_id": session_id,
                "session_name": session_name,
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "metrics": st.session_state.get("session_tokens", {})
            }, indent=2, default=str)
            zf.writestr(f"{session_id}_session.json", session_json)

            title_str = f"Summary: {session_name} ({session_id})" if session_name else f"Summary ({session_id})"
            md_lines = [f"# AutoClimDS Session {title_str}\n"]
            for m in messages:
                role = "User" if m.get("role") == "user" else "Assistant"
                md_lines.append(f"### {role}\n{str(m.get('content', ''))}\n")
            zf.writestr(f"{session_id}_summary.md", "\n".join(md_lines))

        if include_notebook:
            nb_cells = []
            for m in messages:
                role = "user" if m.get("role") == "user" else "assistant"
                nb_cells.append({
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [f"### {role.capitalize()}\n", str(m.get("content", ""))]
                })
            nb_json = json.dumps({
                "cells": nb_cells,
                "metadata": {"language_info": {"name": "python"}},
                "nbformat": 4, "nbformat_minor": 2
            }, indent=2, default=str)
            zf.writestr(f"{session_id}_notebook.ipynb", nb_json)

        if include_data:
            session_files = get_session_files(session_id, {"messages": messages})
            for sf in session_files:
                fp = sf["path"]
                if os.path.isfile(fp) and not sf["name"].endswith(".json"):
                    arcname = os.path.join("data", sf["name"])
                    zf.write(fp, arcname=arcname)

    return zip_buffer.getvalue()

def create_custom_selective_zip(file_items, session_id, full_session_data=None):
    """Creates a zip archive containing selected file items and session summary/notebook"""
    zip_buffer = _io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        if full_session_data:
            messages = full_session_data.get("messages", [])
            session_json_str = json.dumps(full_session_data, indent=2, default=str)
            zf.writestr(f"{session_id}_session.json", session_json_str)

            md_lines = [f"# AutoClimDS Session Summary ({session_id})\n"]
            for m in messages:
                role = "User" if m.get("role") == "user" else "Assistant"
                md_lines.append(f"### {role}\n{m.get('content', '')}\n")
            zf.writestr(f"{session_id}_summary.md", "\n".join(md_lines))
            
            nb_cells = []
            for m in messages:
                role = "user" if m.get("role") == "user" else "assistant"
                nb_cells.append({
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [f"### {role.capitalize()}\n", m.get("content", "")]
                })
            nb_json = json.dumps({
                "cells": nb_cells,
                "metadata": {"language_info": {"name": "python"}},
                "nbformat": 4, "nbformat_minor": 2
            }, indent=2)
            zf.writestr(f"{session_id}_notebook.ipynb", nb_json)

        for item in file_items:
            fp = item["path"]
            if os.path.isfile(fp):
                arcname = os.path.join("data", item["name"])
                zf.write(fp, arcname=arcname)
                
    return zip_buffer.getvalue()

def get_user_session_tree():
    """Returns dict mapping user_email -> list of session info dicts (skips empty 0-conversation sessions)"""
    user_session_map = {}
    if not os.path.exists(SESSIONS_DIR):
        return user_session_map
        
    session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
    for f in session_files:
        try:
            fp = os.path.join(SESSIONS_DIR, f)
            with open(fp, 'r', encoding='utf-8') as jf:
                meta = json.load(jf)
                msgs = meta.get("messages", [])
                
                # Check if session has actual user conversation
                has_user_msgs = any(m.get("role") == "user" for m in msgs)
                if not has_user_msgs:
                    # Clean up empty orphan session file
                    try:
                        os.remove(fp)
                    except Exception: pass
                    continue

                e = meta.get("user_email", "Unknown/System")
                sid = meta.get("session_id", f.replace(".json", ""))
                sname = meta.get("session_name", "")
                ts = meta.get("last_updated") or meta.get("timestamp") or "N/A"
                
                # Get preview from last user or assistant message
                user_msgs = [m for m in msgs if m.get("role") == "user"]
                preview = user_msgs[-1]['content'][:50] if user_msgs else (msgs[-1]['content'][:50] if msgs else "Empty")
                
                date_obj = None
                date_str = ""
                if ts and len(str(ts)) >= 10:
                    try:
                        date_str = str(ts)[:10]
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except Exception: pass
                
                if e not in user_session_map:
                    user_session_map[e] = []
                user_session_map[e].append({
                    "sid": sid,
                    "session_name": sname,
                    "ts": ts,
                    "date_str": date_str,
                    "date_obj": date_obj,
                    "file": f,
                    "preview": preview,
                    "token_usage": meta.get("token_usage", {}),
                    "full_data": meta
                })
        except Exception: pass
        
    for e in user_session_map:
        user_session_map[e].sort(key=lambda x: x['ts'], reverse=True)
        
    return user_session_map

def filter_sessions_by_date(session_list, date_selection):
    """Filters a list of session dicts by a Streamlit date_input result"""
    if not date_selection:
        return session_list
        
    if isinstance(date_selection, (list, tuple)):
        if len(date_selection) == 2:
            d_start, d_end = date_selection[0], date_selection[1]
            return [s for s in session_list if s.get("date_obj") and d_start <= s["date_obj"] <= d_end]
        elif len(date_selection) == 1:
            d_single = date_selection[0]
            return [s for s in session_list if s.get("date_obj") == d_single]
    elif isinstance(date_selection, date):
        return [s for s in session_list if s.get("date_obj") == date_selection]
        
    return session_list

def check_login():
    """Display login screen and handle authentication & registration for Users & Admins"""
    st.markdown("""
        <style>
            .stApp { background-color: #f0f2f6; }
            .login-container {
                max-width: 520px;
                margin: auto;
                padding: 2rem;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.title("🔒 AutoClimDS Portal")
        st.caption("AI-Powered Climate Data Science System")
        
        tab_login, tab_signup, tab_guide = st.tabs([
            "🔑 Sign In", 
            "📝 Register / Sign Up", 
            "📖 Setup & Token Guide"
        ])
        
        # --- TAB 1: SIGN IN ---
        with tab_login:
            st.markdown("Please sign in with your **Columbia University** email and password.")
            
            email = st.text_input("Email Address", placeholder="uni@columbia.edu", key="login_email").strip().lower()
            password = st.text_input("Password", type="password", key="login_pass")
            
            admin_email = config.get("admin_email", "ayon.roy@columbia.edu").lower()
            is_admin_email = (email == admin_email)
            
            if is_admin_email:
                st.info("👨‍✈️ Admin Account Recognized")
            
            if st.button("Sign In", use_container_width=True, type="primary", key="login_signin_btn"):
                if not email:
                    st.error("Please enter an email address.")
                    return
                if not password:
                    st.error("Please enter your password.")
                    return
                
                # Admin Password Verification
                if is_admin_email:
                    correct_admin_pass = st.secrets.get("ADMIN_PASSWORD", ADMIN_DEFAULT_PASS)
                    user_entry = config.get("users", {}).get(email, {})
                    user_hash = user_entry.get("password_hash", "")
                    
                    if (password == correct_admin_pass) or (user_hash and verify_password(password, user_hash)):
                        st.session_state.authenticated = True
                        st.session_state.is_admin = True
                        st.session_state.user_email = email
                        st.session_state.session_id = str(uuid.uuid4())
                        st.session_state.session_start_time = datetime.now()
                        st.session_state.session_tokens = {'input': 0, 'output': 0, 'total': 0, 'cost': 0.0}
                        st.session_state.file_scan_start_time = time.time()
                        st.session_state.my_files = []
                        st.query_params["user"] = email
                        st.query_params["admin"] = "true"
                        save_session_snapshot()
                        st.toast("✅ Admin Access Granted!", icon="🎉")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid Admin Password.")
                        return
                
                # Regular User Verification
                is_columbia = email.endswith("@columbia.edu")
                allowed_list = [e.lower() for e in config.get("allowed_emails", [])]
                users_dict = config.get("users", {})
                
                if not is_columbia:
                    st.error("❌ Access denied. Must be a valid @columbia.edu email address.")
                    return
                
                if email not in allowed_list and email not in users_dict:
                    st.error("❌ Access denied. Email not registered. Switch to 'Register / Sign Up' tab!")
                    return
                
                # Verify password
                user_entry = users_dict.get(email, {})
                stored_hash = user_entry.get("password_hash")
                
                if stored_hash:
                    if verify_password(password, stored_hash):
                        st.session_state.authenticated = True
                        st.session_state.is_admin = False
                        st.session_state.user_email = email
                        st.session_state.session_id = str(uuid.uuid4())
                        st.session_state.session_start_time = datetime.now()
                        st.session_state.session_tokens = {'input': 0, 'output': 0, 'total': 0, 'cost': 0.0}
                        st.session_state.file_scan_start_time = time.time()
                        st.session_state.my_files = []
                        st.query_params["user"] = email
                        st.query_params.pop("admin", None)
                        save_session_snapshot()
                        st.toast(f"✅ Welcome back, {email}!", icon="🎉")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Incorrect Password.")
                else:
                    # First login for pre-allowed email: set password
                    users_dict[email] = {
                        "password_hash": hash_password(password),
                        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    config["users"] = users_dict
                    save_config(config)
                    
                    st.session_state.authenticated = True
                    st.session_state.is_admin = False
                    st.session_state.user_email = email
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.session_start_time = datetime.now()
                    st.session_state.session_tokens = {'input': 0, 'output': 0, 'total': 0, 'cost': 0.0}
                    st.session_state.file_scan_start_time = time.time()
                    st.session_state.my_files = []
                    st.query_params["user"] = email
                    st.query_params.pop("admin", None)
                    save_session_snapshot()
                    st.toast("✅ Password set for your account & logged in!", icon="🎉")
                    time.sleep(1)
                    st.rerun()

        # --- TAB 2: REGISTER / SIGN UP ---
        with tab_signup:
            st.markdown("#### 📝 Register Columbia Account")
            st.caption("Register your `@columbia.edu` email and create a password for instant access.")
            
            signup_email = st.text_input("Columbia Email to Register", placeholder="your_uni@columbia.edu", key="signup_email").strip().lower()
            signup_pass = st.text_input("Create Password", type="password", key="signup_pass")
            signup_pass_confirm = st.text_input("Confirm Password", type="password", key="signup_pass_confirm")
            
            if st.button("Create Account & Sign In", use_container_width=True, type="primary", key="signup_btn"):
                if not signup_email:
                    st.error("Please enter an email address.")
                elif not signup_email.endswith("@columbia.edu"):
                    st.error("❌ Registration requires a valid `@columbia.edu` email address.")
                elif not signup_pass:
                    st.error("Please enter a password.")
                elif len(signup_pass) < 4:
                    st.error("Password must be at least 4 characters long.")
                elif signup_pass != signup_pass_confirm:
                    st.error("❌ Passwords do not match. Please verify.")
                else:
                    users_dict = config.get("users", {})
                    allowed_list = config.get("allowed_emails", [])
                    
                    if signup_email in users_dict and users_dict[signup_email].get("password_hash"):
                        st.info("ℹ️ Account already exists with a password. Please use the 'Sign In' tab.")
                        return
                    
                    users_dict[signup_email] = {
                        "password_hash": hash_password(signup_pass),
                        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    if signup_email not in allowed_list:
                        allowed_list.append(signup_email)
                    
                    config["users"] = users_dict
                    config["allowed_emails"] = allowed_list
                    save_config(config)
                    
                    st.session_state.authenticated = True
                    st.session_state.is_admin = (signup_email == config.get("admin_email", "ayon.roy@columbia.edu").lower())
                    st.session_state.user_email = signup_email
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.session_start_time = datetime.now()
                    st.session_state.session_tokens = {'input': 0, 'output': 0, 'total': 0, 'cost': 0.0}
                    st.session_state.file_scan_start_time = time.time()
                    st.session_state.my_files = []
                    st.toast(f"✅ Account Created & Logged in as {signup_email}!", icon="🎉")
                    time.sleep(1)
                    st.rerun()

        # --- TAB 3: SETUP & TOKEN GUIDE ---
        with tab_guide:
            st.markdown("#### 📖 Local Configuration & Token Guide")
            st.markdown("""
            **1. Email Sign-Up & Login:**
            - Any user with a `@columbia.edu` email can register via **Register / Sign Up** tab.
            
            **2. Changing Local Admin Email:**
            - To set yourself as the Admin when running locally, open `user_config.json` and change:
              ```json
              {
                  "admin_email": "your.email@columbia.edu"
              }
              ```
            
            **3. Configuring External API Keys:**
            - Store your keys in `Agents/.env` or in the sidebar **🔑 API Credentials** menu:
              - **NOAA CDO Token**: [Get Free NOAA Token](https://www.ncdc.noaa.gov/cdo-web/token)
              - **NASA Earthdata**: [Register Earthdata Account](https://urs.earthdata.nasa.gov)
              - **Copernicus CDS API**: [Copernicus Climate Portal](https://cds.climate.copernicus.eu)
              - **AWS Credentials**: Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` in `.env`.
            """)

if not st.session_state.authenticated:
    check_login()
    st.stop()

# Helper for Session Mapping
def get_session_map():
    mapping = {}
    if os.path.exists(SESSIONS_DIR):
        try:
            for f in os.listdir(SESSIONS_DIR):
                if f.endswith(".json"):
                    fp = os.path.join(SESSIONS_DIR, f)
                    with open(fp, "r", encoding="utf-8", errors="replace") as jf:
                        meta = json.load(jf)
                        sid = meta.get("session_id", f.replace(".json", ""))
                        em = meta.get("user_email")
                        if sid and em and em != "unknown":
                            mapping[sid] = em
        except Exception as e:
            print(f"Error reading session files for map: {e}")
            
    if os.path.exists(LOG_FILE):
        try:
            import csv
            with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sid = row.get("Session_ID")
                    em = row.get("Email")
                    if sid and em and em != "unknown":
                        mapping[sid] = em
        except Exception as e:
            print(f"Error reading log file for session map: {e}")
            
    return mapping

def tag_newly_created_session_files():
    """Find any newly generated data files and prefix them with active session_id if not already prefixed"""
    sid = st.session_state.get("session_id")
    if not sid or sid == "unknown":
        return
        
    target_dirs = [
        BASE_DATA_DIR,
        os.path.join(BASE_DATA_DIR, 'era5_data'),
        os.path.join(BASE_DATA_DIR, 'downloads'),
        os.path.join(BASE_DATA_DIR, 'fema_data'),
        os.path.join(BASE_DATA_DIR, 'us_311_data'),
        os.path.join(BASE_DATA_DIR, 'outputs'),
        os.path.join(BASE_DATA_DIR, 'uploads'),
        os.path.join(BASE_DATA_DIR, 'mrms_downloads'),
        os.path.join(BASE_DATA_DIR, 'cmip6_out')
    ]
    
    session_start_time = st.session_state.get("file_scan_start_time", 0)
    
    for d in target_dirs:
        if os.path.isdir(d):
            try:
                for f in os.listdir(d):
                    if f.startswith('.') or f.endswith(('.py', '.pyc', '.jsonl', '.db', '.log', '.toml', '.pem', '.json')):
                        continue
                    if sid in f:
                        continue
                    fp = os.path.join(d, f)
                    if os.path.isfile(fp):
                        if session_start_time == 0 or os.path.getmtime(fp) >= (session_start_time - 10):
                            new_name = f"{sid}_{f}"
                            new_fp = os.path.join(d, new_name)
                            try:
                                os.rename(fp, new_fp)
                                print(f"Tagged file with session_id: {new_name}")
                            except Exception: pass
            except Exception: pass

# ==============================================================================
# ADMIN DASHBOARD
# ==============================================================================
def admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    st.info(f"Logged in as: {st.session_state.user_email}")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 User Management", 
        "🗄️ File System", 
        "📊 Usage Analytics", 
        "🏥 System Health", 
        "🕵️ User Inspector"
    ])
    
    # --- Tab 1: User Management ---
    with tab1:
        st.subheader("Manage Access & User Accounts")
        current_users = config.get("allowed_emails", [])
        users_dict = config.get("users", {})
        st.write(f"**Total Registered / Allowed Users:** {len(current_users)}")
        
        with st.form("add_user"):
            st.markdown("#### Grant Access to New User")
            new_mail = st.text_input("Email (@columbia.edu)").strip().lower()
            new_pass = st.text_input("Set Initial Password (Optional)", type="password").strip()
            submitted = st.form_submit_button("Grant Access / Register User", type="primary")
            
            if submitted:
                if not new_mail:
                    st.error("Email is required.")
                elif not new_mail.endswith("@columbia.edu"):
                    st.warning("Email must end with @columbia.edu")
                else:
                    if new_mail not in current_users:
                        current_users.append(new_mail)
                    if new_pass:
                        users_dict[new_mail] = {
                            "password_hash": hash_password(new_pass),
                            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    config["allowed_emails"] = current_users
                    config["users"] = users_dict
                    save_config(config)
                    st.success(f"✅ User {new_mail} granted access!")
                    time.sleep(1)
                    st.rerun()

        st.markdown("---")
        st.markdown("#### Current Users & Password Status")
        for u in current_users:
            c1, c2, c3 = st.columns([3, 1.5, 1])
            has_pass = "🔒 Password Set" if (u in users_dict and users_dict[u].get("password_hash")) else "⚠️ No Password Set"
            c1.text(u)
            c2.caption(has_pass)
            if c3.button("Remove", key=f"del_{u}"):
                current_users.remove(u)
                if u in users_dict:
                    del users_dict[u]
                config["allowed_emails"] = current_users
                config["users"] = users_dict
                save_config(config)
                st.success(f"Removed {u}")
                time.sleep(0.5)
                st.rerun()

    # --- Tab 2: File System ---
    with tab2:
        st.subheader("🗄️ Hierarchical File Explorer (By User → Session)")
        st.markdown("Filter files by **User Email**, then by **Session ID**, and download selective ZIP archives.")
        
        target_dirs = [
            BASE_DATA_DIR,
            os.path.join(BASE_DATA_DIR, 'era5_data'),
            os.path.join(BASE_DATA_DIR, 'downloads'),
            os.path.join(BASE_DATA_DIR, 'fema_data'),
            os.path.join(BASE_DATA_DIR, 'us_311_data'),
            os.path.join(BASE_DATA_DIR, 'outputs'),
            SESSIONS_DIR,
            os.path.join(BASE_DATA_DIR, 'uploads')
        ]
        
        # Cleanup
        c_clean1, c_clean2 = st.columns([3, 1])
        c_clean1.info("🧹 Auto-Cleanup: Delete files older than 7 days")
        if c_clean2.button("Run Cleanup", key="btn_run_cleanup"):
            count = 0
            now = time.time()
            limit = 7 * 86400
            for d in target_dirs:
                if os.path.isdir(d):
                    for f in os.listdir(d):
                        fp = os.path.join(d, f)
                        if os.path.isfile(fp):
                            if now - os.path.getmtime(fp) > limit:
                                try:
                                    os.remove(fp)
                                    count += 1
                                except Exception: pass
            st.success(f"Cleaned up {count} files older than 7 days.")
        
        st.divider()
        
        # --- Hierarchical Filters: User -> Date -> Session -> Directory ---
        user_tree = get_user_session_tree()
        all_emails = ["All Users"] + sorted(list(user_tree.keys()))
        
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            selected_user = st.selectbox("1. User Email", all_emails, key="fs_sel_user")
            
        with fc2:
            fs_dates = st.date_input("2. Date Range", value=[], key="fs_date_range")
            
        user_sess_list = user_tree.get(selected_user, []) if selected_user != "All Users" else []
        if fs_dates and user_sess_list:
            user_sess_list = filter_sessions_by_date(user_sess_list, fs_dates)

        with fc3:
            if selected_user != "All Users" and user_sess_list:
                sess_opts = ["All Sessions for this User"] + [
                    f"🏷️ {s['session_name']} | {s['ts']} ({s['sid'][:8]}...)" if s.get('session_name') else f"Session {s['sid'][:8]}... | {s['ts']}"
                    for s in user_sess_list
                ]
                selected_sess_str = st.selectbox("3. Session", sess_opts, key="fs_sel_sess")
            elif selected_user != "All Users":
                selected_sess_str = st.selectbox("3. Session", ["No sessions for date filter"], key="fs_sel_sess")
            else:
                selected_sess_str = st.selectbox("3. Session", ["All Sessions"], key="fs_sel_sess")
                
        with fc4:
            display_dirs = ["All Directories"] + target_dirs
            selected_dir = st.selectbox("4. Directory", display_dirs, key="fs_sel_dir")
            
        # Active session ID
        active_sid = None
        if selected_user != "All Users" and user_sess_list and selected_sess_str not in ["All Sessions for this User", "All Sessions", "No sessions for date filter"]:
            for s in user_sess_list:
                label_check = f"🏷️ {s['session_name']} | {s['ts']} ({s['sid'][:8]}...)" if s.get('session_name') else f"Session {s['sid'][:8]}... | {s['ts']}"
                if label_check == selected_sess_str:
                    active_sid = s['sid']
                    break
                    
        # Collect matching files
        scan_dirs = target_dirs if selected_dir == "All Directories" else [selected_dir]
        session_map = get_session_map()
        
        # Build map of filename -> (sid, user_email) from session JSON files
        file_to_session_map = {}
        if os.path.exists(SESSIONS_DIR):
            for sj in os.listdir(SESSIONS_DIR):
                if sj.endswith(".json"):
                    try:
                        with open(os.path.join(SESSIONS_DIR, sj), "r", encoding="utf-8", errors="replace") as sf:
                            s_meta = json.load(sf)
                            s_id = s_meta.get("session_id", sj.replace(".json", ""))
                            s_user = s_meta.get("user_email", "Unknown/System")
                            msgs = s_meta.get("messages", [])
                            for m in msgs:
                                c_text = str(m.get("content", ""))
                                for fn in re.findall(r'([a-zA-Z0-9_.-]+\.(?:csv|nc|png|jpg|jpeg|pdf|xlsx|grib|geojson|tif|tiff))', c_text):
                                    file_to_session_map[fn] = (s_id, s_user)
                    except Exception: pass

        file_data = []
        
        for d in scan_dirs:
            if os.path.isdir(d):
                try:
                    for f in os.listdir(d):
                        if f in [os.path.basename(LOG_FILE), os.path.basename(CONFIG_FILE)]:
                            continue
                        if f.startswith('.') or f.endswith(('.py', '.toml', 'Dockerfile', '.pem')):
                            continue
                        fp = os.path.join(d, f)
                        if os.path.isfile(fp):
                            size_mb = os.path.getsize(fp) / (1024 * 1024)
                            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M')
                            
                            u_email = "Unknown/System"
                            sid_val = "N/A"
                            match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', f)
                            if match:
                                sid_val = match.group(1)
                                u_email = session_map.get(sid_val, "Unknown Session")
                            elif f in file_to_session_map:
                                sid_val, u_email = file_to_session_map[f]
                            elif active_sid and (active_sid in f or active_sid in fp):
                                sid_val = active_sid
                                u_email = selected_user

                            # Filter logic by User
                            if selected_user != "All Users":
                                if u_email != selected_user and not (active_sid and (active_sid in f or active_sid in fp)):
                                    continue
                                
                            # Filter logic by Session
                            if active_sid:
                                if sid_val != active_sid and active_sid not in f and active_sid not in fp:
                                    continue

                            file_data.append({
                                "File": f, "Dir": d, "Session": sid_val[:8] if sid_val != "N/A" else "N/A", 
                                "FullSID": sid_val, "User": u_email, 
                                "Size (MB)": f"{size_mb:.2f}", "Modified": mtime, "Path": fp
                            })
                except Exception: pass

        if file_data:
            st.markdown(f"**Found {len(file_data)} file(s)** matching your filters.")
            
            # --- Selective ZIP Exporter ---
            with st.expander("📦 Package & Download Filtered Files as ZIP", expanded=True):
                all_fnames = [item["File"] for item in file_data]
                sel_fnames = st.multiselect(
                    "Choose specific files to package into ZIP:",
                    options=all_fnames,
                    default=all_fnames,
                    key="tab2_multisel_zip"
                )
                
                chosen_files = [item for item in file_data if item["File"] in sel_fnames]
                
                c_z1, c_z2 = st.columns(2)
                with c_z1:
                    if st.button("📦 Build ZIP of Selected Files", key="tab2_build_zip_btn", use_container_width=True):
                        zip_buf = _io.BytesIO()
                        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                            for item in chosen_files:
                                zf.write(item["Path"], arcname=os.path.join("data", item["File"]))
                        st.session_state["tab2_zip_bytes"] = zip_buf.getvalue()
                        st.toast(f"✅ Packaged {len(chosen_files)} file(s) into ZIP!")
                        
                    if "tab2_zip_bytes" in st.session_state:
                        st.download_button(
                            f"⬇️ Download ZIP ({len(chosen_files)} files)",
                            st.session_state["tab2_zip_bytes"],
                            file_name="selected_user_files.zip",
                            mime="application/zip",
                            use_container_width=True,
                            key="tab2_dl_zip_btn"
                        )
                with c_z2:
                    if active_sid:
                        target_session_meta = None
                        if selected_user in user_tree:
                            for s in user_tree[selected_user]:
                                if s['sid'] == active_sid:
                                    target_session_meta = s.get('full_data')
                                    break
                        if target_session_meta:
                            s_tag = target_session_meta.get("session_name", "")
                            safe_tag = re.sub(r'[^a-zA-Z0-9_-]', '_', s_tag) if s_tag else ""
                            prefix = f"{safe_tag}_" if safe_tag else ""
                            full_zip_b = create_session_zip(
                                target_session_meta.get("messages", []),
                                active_sid, session_name=s_tag, include_memory=True, include_data=True, include_notebook=True
                            )
                            st.download_button(
                                "📦 Download Full Session ZIP (Data + Memory)",
                                full_zip_b,
                                file_name=f"{prefix}{active_sid[:8]}_full_session.zip",
                                mime="application/zip",
                                use_container_width=True,
                                key=f"tab2_dl_full_zip_{active_sid}"
                            )

            st.divider()
            # File List Table
            h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([3, 1, 1, 2, 1, 2, 0.5, 0.5])
            h1.markdown("**File Name**")
            h2.markdown("**Folder**")
            h3.markdown("**Session**")
            h4.markdown("**User**")
            h5.markdown("**Size**")
            h6.markdown("**Modified**")
            h7.markdown("**DL**")
            h8.markdown("**Del**")
            st.divider()
            
            for item in file_data:
                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([3, 1, 1, 2, 1, 2, 0.5, 0.5])
                c1.write(f"📄 `{item['File']}`")
                c2.code(item['Dir'] if item['Dir'] != "." else "root")
                c3.caption(item['Session'])
                c4.caption(item['User'])
                c5.write(f"{item['Size (MB)']} MB")
                c6.write(item['Modified'])
                
                with open(item['Path'], "rb") as f:
                    c7.download_button("⬇️", f, file_name=item['File'], key=f"adm_dl_{item['Path']}")
                if c8.button("🗑️", key=f"del_file_{item['Path']}"):
                    try:
                        os.remove(item['Path'])
                        st.toast(f"Deleted {item['File']}")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No files found matching the selected user & session filters.")

    # --- Tab 3: Usage Analytics ---
    with tab3:
        st.subheader("📊 Usage Analytics")
        if os.path.exists(LOG_FILE):
            col_d1, col_d2 = st.columns([1, 4])
            with col_d1:
                with open(LOG_FILE, "rb") as f:
                    st.download_button("⬇️ Download Log CSV", f, "token_usage_log.csv", "text/csv")
            try:
                import pandas as pd
                df = pd.read_csv(LOG_FILE)
                if not df.empty:
                    total_cost = df['Cost_Est_USD'].sum() if 'Cost_Est_USD' in df.columns else 0.0
                    total_tokens = df['Total_Tokens'].sum() if 'Total_Tokens' in df.columns else 0
                    unique_users = df['Email'].nunique() if 'Email' in df.columns else 0
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Cost Est.", f"${total_cost:.4f}")
                    m2.metric("Total Tokens", f"{total_tokens:,}")
                    m3.metric("Active Users", unique_users)
                    st.divider()
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.caption("Cost per User ($)")
                        if 'Email' in df.columns and 'Cost_Est_USD' in df.columns:
                            st.bar_chart(df.groupby("Email")["Cost_Est_USD"].sum().sort_values(ascending=False))
                    with c2:
                        st.caption("Token Distribution by Model")
                        if 'Model' in df.columns:
                            st.bar_chart(df['Model'].value_counts())
                            
                    st.caption("Recent Activity Log (Newest First)")
                    st.dataframe(df.tail(15).iloc[::-1], use_container_width=True)
                else:
                    st.info("Log file is empty.")
            except ImportError:
                st.warning("Pandas not installed for visualization.")
        else:
            st.info("No usage log file found yet.")

    # --- Tab 4: System Health ---
    with tab4:
        st.subheader("🏥 System Health Monitor")
        c1, c2 = st.columns(2)
        try:
            total, used, free = shutil.disk_usage(".")
            gb = 1024 ** 3
            c1.metric("Disk Free", f"{free / gb:.2f} GB", f"Total: {total / gb:.1f} GB")
        except Exception as e:
            c1.error(f"Disk check failed: {e}")
            
        try:
            import psutil
            mem = psutil.virtual_memory()
            c2.metric("RAM Usage", f"{mem.percent}%", f"Available: {mem.available / gb:.1f} GB")
        except ImportError:
            c2.warning("`psutil` not installed.")
            
        st.divider()
        st.markdown("#### 🌐 Data Services Status")
        services = [
            {"name": "General Internet", "url": "https://www.google.com/generate_204"},
            {"name": "NASA CMR API", "url": "https://cmr.earthdata.nasa.gov/search/collections.json?page_size=1"},
            {"name": "ERA5 (Copernicus)", "url": "https://cds.climate.copernicus.eu"},
            {"name": "CMIP6 (ESGF)", "url": "https://esgf-node.llnl.gov/esg-search/search?limit=1"},
            {"name": "OpenFEMA API", "url": "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$top=1"},
            {"name": "NYC 311 API", "url": "https://data.cityofnewyork.us/api/views/erm2-nwe9.json"},
        ]
        
        cols = st.columns(3)
        for i, service in enumerate(services):
            with cols[i % 3]:
                try:
                    r = requests.get(service["url"], timeout=5)
                    if r.status_code < 400:
                        st.success(f"✅ **{service['name']}**")
                    else:
                        st.warning(f"⚠️ **{service['name']}**: {r.status_code}")
                except Exception as e:
                    st.error(f"❌ **{service['name']}**")
                    st.caption(f"{type(e).__name__}")

    # --- Tab 5: User Inspector (God Mode) ---
    with tab5:
        st.subheader("🕵️ User Inspector (God Mode)")
        st.info("Replay user sessions, inspect custom session tags, and audit conversation transcripts.")
        
        user_session_map = get_user_session_tree()
        if not user_session_map:
            st.info("No saved user session logs found yet.")
        else:
            all_users = sorted(list(user_session_map.keys()))
            sel_user = st.selectbox("Select User Email to Inspect", all_users, key="inspector_sel_user")
            
            user_sessions = user_session_map[sel_user]
            
            c_insp_d1, c_insp_d2 = st.columns(2)
            with c_insp_d1:
                insp_dates = st.date_input("📅 Filter Sessions by Date Range", value=[], key="inspector_date_filter")
                
            if insp_dates:
                user_sessions = filter_sessions_by_date(user_sessions, insp_dates)
                
            session_options = {}
            for s in user_sessions:
                label = f"🏷️ {s['session_name']} | {s['ts']} ({s['sid'][:8]}...) | {s['preview']}" if s.get('session_name') else f"Session {s['sid'][:8]}... | {s['ts']} | {s['preview']}"
                session_options[label] = s
                
            with c_insp_d2:
                if session_options:
                    sel_key = st.selectbox("Select User Session", list(session_options.keys()), key="inspector_sel_sess")
                else:
                    sel_key = st.selectbox("Select User Session", ["No sessions found for selected date range"], key="inspector_sel_sess")
            
            if sel_key and sel_key in session_options:
                target = session_options[sel_key]
                st.divider()
                col_m1, col_m2 = st.columns(2)
                tag_disp = f" | **Tag:** `{target.get('session_name')}`" if target.get('session_name') else ""
                col_m1.markdown(f"**Session ID:** `{target['sid']}`{tag_disp}")
                col_m2.markdown(f"**Last Updated:** `{target['ts']}`")
                
                if target.get("token_usage"):
                    st.caption(f"Tokens Used in Session: {target['token_usage']}")
                    
                    try:
                        with open(os.path.join(SESSIONS_DIR, target['file']), 'r', encoding='utf-8') as f:
                            full_data = json.load(f)
                            msgs = full_data.get("messages", [])
                            
                            # --- Per-Session File Inspector & Selective ZIP Export ---
                            st.markdown("#### 📂 Session Files & Selective Zip Export")
                            session_files = get_session_files(target['sid'], full_data)
                            
                            if session_files:
                                st.caption(f"Found {len(session_files)} file(s) associated with Session `{target['sid'][:8]}...`")
                                
                                default_sel = [item["name"] for item in session_files]
                                selected_filenames = st.multiselect(
                                    "Choose specific files to package into ZIP:",
                                    options=[item["name"] for item in session_files],
                                    default=default_sel,
                                    key=f"admin_sel_files_{target['sid']}"
                                )
                                
                                chosen_items = [item for item in session_files if item["name"] in selected_filenames]
                                
                                col_z1, col_z2 = st.columns(2)
                                with col_z1:
                                    if st.button("📦 Build Selective ZIP for this Session", key=f"btn_sel_zip_{target['sid']}", use_container_width=True):
                                        with st.spinner("Packaging selected session files..."):
                                            zip_bytes = create_custom_selective_zip(chosen_items, target['sid'], full_data)
                                            st.session_state[f"_admin_zip_{target['sid']}"] = zip_bytes
                                            st.toast(f"✅ Packaged {len(chosen_items)} file(s) for session {target['sid'][:8]}!")
                                    
                                    if f"_admin_zip_{target['sid']}" in st.session_state:
                                        s_tag = target.get("session_name", "")
                                        safe_tag = re.sub(r'[^a-zA-Z0-9_-]', '_', s_tag) if s_tag else ""
                                        prefix = f"{safe_tag}_" if safe_tag else ""
                                        st.download_button(
                                            f"⬇️ Download {len(chosen_items)} Selected File(s) ZIP",
                                            st.session_state[f"_admin_zip_{target['sid']}"],
                                            file_name=f"{prefix}{target['sid'][:8]}_selective_files.zip",
                                            mime="application/zip",
                                            use_container_width=True,
                                            key=f"dl_admin_zip_{target['sid']}"
                                        )
                                
                                with col_z2:
                                    s_tag = target.get("session_name", "")
                                    safe_tag = re.sub(r'[^a-zA-Z0-9_-]', '_', s_tag) if s_tag else ""
                                    prefix = f"{safe_tag}_" if safe_tag else ""
                                    full_zip_bytes = create_session_zip(msgs, target['sid'], session_name=s_tag, include_memory=True, include_data=True, include_notebook=True)
                                    st.download_button(
                                        "📦 Download Full Session ZIP (All Memory + Data)",
                                        full_zip_bytes,
                                        file_name=f"{prefix}{target['sid'][:8]}_full_session.zip",
                                        mime="application/zip",
                                        use_container_width=True,
                                        key=f"dl_full_admin_zip_{target['sid']}"
                                    )
                                
                                with st.expander("📋 View Individual File List & Single Downloads"):
                                    for item in session_files:
                                        fc1, fc2, fc3 = st.columns([3, 1, 1])
                                        fc1.caption(f"📄 `{item['name']}` ({item['size_mb']})")
                                        fc2.caption(f"Type: `{item['type']}`")
                                        if os.path.exists(item['path']):
                                            with open(item['path'], "rb") as fb:
                                                fc3.download_button("⬇️ DL", fb, file_name=item['name'], key=f"indiv_dl_{target['sid']}_{item['name']}")
                            else:
                                st.info("No data files generated in this specific session yet. Full session JSON is available below.")
                                s_tag = target.get("session_name", "")
                                safe_tag = re.sub(r'[^a-zA-Z0-9_-]', '_', s_tag) if s_tag else ""
                                prefix = f"{safe_tag}_" if safe_tag else ""
                                full_zip_bytes = create_session_zip(msgs, target['sid'], session_name=s_tag, include_memory=True, include_data=True, include_notebook=True)
                                st.download_button(
                                    "📦 Download Full Session ZIP",
                                    full_zip_bytes,
                                    file_name=f"{prefix}{target['sid'][:8]}_full_session.zip",
                                    mime="application/zip",
                                    key=f"dl_full_admin_zip_empty_{target['sid']}"
                                )

                            st.divider()
                            st.markdown("#### 💬 Conversation Transcript")
                            with st.container(border=True):
                                for m in msgs:
                                    with st.chat_message(m["role"]):
                                        st.markdown(m["content"])
                    except Exception as ex:
                        st.error(f"Error reading session file: {ex}")


# ==============================================================================
# MAIN ROUTING (Admin vs User Mode)
# ==============================================================================
if st.session_state.get("is_admin"):
    with st.sidebar:
        st.header("👨‍✈️ Admin Portal")
        st.caption(f"Logged in as: {st.session_state.user_email}")
        st.divider()
        
        mode = st.radio(
            "Navigation", 
            ["Dashboard", "Chat Simulator"],
            captions=["Manage Users, Files & Sessions", "Test Agent Capabilities"],
            index=0
        )
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.is_admin = False
            st.query_params.clear()
            st.rerun()
            
    if mode == "Dashboard":
        admin_dashboard()
        st.stop()

# ==============================================================================
# MAIN CHAT APPLICATION (User or Admin Chat Simulator)
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
        pass

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        tool_name = serialized.get("name", "Unknown Tool")
        
        if self.status:
            self.status.update(label=f"✅ Finished: {self.status_label}", state="complete")
        
        self.status_label = f"Using tool: **{tool_name}**"
        self.status = self.container.status(self.status_label, expanded=True)
        
        log_entry = f"**Input:** `{input_str}`\n\n"
        self.status.markdown(log_entry)

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        if self.status:
            clean_output = str(output).strip()
            if len(clean_output) > 500:
                clean_output = clean_output[:500] + "... (truncated)"
            
            self.status.markdown(f"**Output:** {clean_output}")
            self.status.update(label=f"✅ Finished tool execution", state="complete")

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        if self.status:
            self.status.markdown(f"❌ **Error:** {str(error)}")
            self.status.update(label="❌ Tool Execution Failed", state="error")

    def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        tool = getattr(action, "tool", "Unknown")
        tool_input = getattr(action, "tool_input", "")
        
        if self.status:
            self.status.update(label=f"✅ Finished: {self.status_label}", state="complete")
            
        self.status_label = f"Action: **{tool}**"
        self.status = self.container.status(self.status_label, expanded=True)
        self.status.markdown(f"**Thought:** {getattr(action, 'log', '')}\n\n**Input:** `{tool_input}`")

# --- Helper Functions ---
def initialize_agent():
    """Initialize the climate orchestrator agent safely"""
    try:
        session_id = st.session_state.get('session_id')
        try:
            agent = create_climate_research_orchestrator(session_id=session_id)
        except TypeError:
            agent = create_climate_research_orchestrator()
        if agent:
            st.session_state.agent = agent
            return True
        return False
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return False

# Attempt FPDF import for PDF export
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

def create_pdf_report(messages, files):
    if not FPDF:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AutoClimDS Research Discussion Report", ln=1, align='C')
    pdf.ln(10)
    
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, txt=f"{role}:", ln=1)
        pdf.set_font("Arial", size=10)
        
        clean_text = msg["content"].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_text)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

def show_generated_files():
    if "my_files" not in st.session_state:
        st.session_state.my_files = []
        
    start_time = st.session_state.get("file_scan_start_time", 0)
    session_id = st.session_state.get("session_id", "")
    
    current_session_files = []
    search_dirs = [".", "outputs", "era5_data", "us_311_data", "fema_data"]
    
    for d in search_dirs:
        if os.path.exists(d):
            try:
                for f in os.listdir(d):
                    fp = os.path.join(d, f)
                    if os.path.isfile(fp):
                        if (session_id and session_id in f) or (os.path.getmtime(fp) > start_time):
                            if not f.endswith(('.py', '.pyc', '.jsonl', '.db', '.log', '.toml', '.pem', '.json')):
                                current_session_files.append((f, fp))
            except Exception: pass
            
    if current_session_files:
        st.sidebar.divider()
        st.sidebar.subheader("📂 Generated Data & Plots")
        for fname, fpath in current_session_files:
            col_a, col_b = st.sidebar.columns([3, 1])
            col_a.caption(f"📄 {fname}")
            try:
                with open(fpath, "rb") as file_bytes:
                    col_b.download_button("⬇️", file_bytes, file_name=fname, key=f"dl_{fpath}")
            except Exception: pass
            
    return current_session_files

WELCOME_MESSAGE = """👋 **Welcome to AutoClimDS!**

I can help you with:
- 🛰️ **NASA Satellite Data** (MODIS, GOES)
- 🌪️ **FEMA Disaster Records** (Floods, Hurricanes)
- 🏙️ **City 311 Service Requests** (NYC, Chicago, SF)
- 🖥️ **Climate Simulations** (ERA5, CMIP6)

Simply describe what you need, for example:
> *"Find flood disaster declarations in Texas for 2021"*
> *"Download ERA5 temperature data for NYC in July 2023"*
"""

# --- Main App State Setup ---
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]
if "agent" not in st.session_state:
    st.session_state.agent = None

# --- Sidebar Controls ---
with st.sidebar:
    st.title("🌍 AutoClimDS")
    st.caption("AI-Powered Climate Data Science Assistant")
    
    if st.button("🚪 Logout", key="user_logout_btn"):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.query_params.clear()
        st.rerun()

    st.divider()
    st.subheader("⚙️ Configuration")
    _jupyter_on = st.toggle("LAMBDA", value=False, key="jupyter_kernel_toggle")
    if _jupyter_on:
        os.environ["AUTOCLIMDS_JUPYTER_MODE"] = "1"
    else:
        os.environ.pop("AUTOCLIMDS_JUPYTER_MODE", None)

    st.divider()
    st.subheader("📚 Semantic Scholar Options")
    with st.expander("🔍 Search Settings"):
        _top_k = st.slider("Max papers to fetch", 1, 15, 5, key="scholar_top_k_sl")
        _y_col1, _y_col2 = st.columns(2)
        _year_from = _y_col1.number_input("From year", 1900, 2030, 2010, key="scholar_yf")
        _year_to   = _y_col2.number_input("To year",   1900, 2030, 2026, key="scholar_yt")
        _depth_label = st.radio("Summary Depth", ["Quick", "Standard", "Detailed"], index=1, key="scholar_dep")

        os.environ["SCHOLAR_TOP_K"]         = str(int(_top_k))
        os.environ["SCHOLAR_YEAR_FROM"]     = str(int(_year_from))
        os.environ["SCHOLAR_YEAR_TO"]       = str(int(_year_to))
        os.environ["SCHOLAR_SUMMARY_DEPTH"] = _depth_label.lower()

    with st.expander("🔑 API Credentials & Setup Guide"):
        st.caption("If not set in `.env`, enter keys here.")
        st.session_state['auth_earthdata_username'] = st.text_input("Earthdata Username")
        st.session_state['auth_earthdata_password'] = st.text_input("Earthdata Password", type="password")
        st.session_state['auth_noaa_token'] = st.text_input("NOAA CDO Token", type="password")
        st.markdown("---")
        st.markdown("""
        **Token & Local Setup Help:**
        - **NOAA Token**: [Get Free NOAA CDO Token](https://www.ncdc.noaa.gov/cdo-web/token)
        - **NASA Earthdata**: [Register Earthdata Account](https://urs.earthdata.nasa.gov)
        - **Copernicus CDS**: [Copernicus Climate Portal](https://cds.climate.copernicus.eu)
        - **Local Admin Email**: Change `"admin_email"` in `user_config.json` to set your email as local Admin.
        """)
    
    if st.button("➕ Start New Fresh Session", key="btn_reset_conv_sidebar", use_container_width=True):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["session_name"] = ""
        st.session_state["save_session_name_input"] = ""
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]
        st.session_state.agent = None
        st.session_state.session_tokens = {'input': 0, 'output': 0, 'total': 0, 'cost': 0.0}
        st.session_state.file_scan_start_time = time.time()
        st.toast("✨ Started a fresh new session!", icon="🌱")
        time.sleep(0.3)
        st.rerun()
    
    recent_files = show_generated_files()
    
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

    st.divider()
    st.subheader("💾 Session Memory")

    with st.expander("📜 My Previous Sessions", expanded=False):
        curr_user_email = st.session_state.get("user_email", "")
        user_session_tree = get_user_session_tree()
        my_sessions = user_session_tree.get(curr_user_email, [])
        
        if not my_sessions:
            st.caption("No previous saved sessions found for your account.")
        else:
            my_dates = st.date_input("📅 Filter by Date Range", value=[], key="my_prev_date_filter")
            if my_dates:
                my_sessions = filter_sessions_by_date(my_sessions, my_dates)
                
            if not my_sessions:
                st.caption("No sessions found for the selected date range.")
            else:
                sess_map = {}
                for s in my_sessions:
                    s_tag = s.get("session_name", "")
                    if s_tag:
                        lbl = f"🏷️ {s_tag} | {s['ts']} ({s['sid'][:8]}...)"
                    else:
                        lbl = f"Session {s['sid'][:8]}... | {s['ts']}"
                    sess_map[lbl] = s
                    
                selected_prev_lbl = st.selectbox("Select Previous Session", list(sess_map.keys()), key="my_prev_sess_sel")
                if selected_prev_lbl:
                    chosen_sess = sess_map[selected_prev_lbl]
                    st.caption(f"Last updated: `{chosen_sess['ts']}`")
                    
                    c_load1, c_load2 = st.columns(2)
                    with c_load1:
                        if st.button("🔄 Resume Session", use_container_width=True, key=f"btn_resume_{chosen_sess['sid']}"):
                            sess_fp = os.path.join(SESSIONS_DIR, f"{chosen_sess['sid']}.json")
                            if os.path.exists(sess_fp):
                                try:
                                    with open(sess_fp, 'r', encoding='utf-8') as sf:
                                        f_data = json.load(sf)
                                        loaded_messages = f_data.get("messages", [])
                                        if loaded_messages:
                                            st.session_state["messages"] = loaded_messages
                                            st.session_state["session_id"] = chosen_sess["sid"]
                                            st.session_state["session_name"] = f_data.get("session_name", "")
                                            st.session_state["save_session_name_input"] = f_data.get("session_name", "")
                                            st.session_state["session_tokens"] = f_data.get("token_usage", {})
                                            st.session_state.agent = None
                                            st.toast(f"✅ Loaded {len(loaded_messages)} message(s) from session!")
                                            time.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.warning("Session file exists but contains no messages.")
                                except Exception as ex:
                                    st.error(f"Error loading session: {ex}")
                            else:
                                st.error("Session file not found on disk.")
                    with c_load2:
                        s_tag = chosen_sess.get("session_name", "")
                        safe_tag = re.sub(r'[^a-zA-Z0-9_-]', '_', s_tag) if s_tag else ""
                        prefix = f"{safe_tag}_" if safe_tag else ""
                        prev_zip_b = create_session_zip(
                            chosen_sess.get("full_data", {}).get("messages", []),
                            chosen_sess["sid"],
                            session_name=s_tag,
                            include_memory=True, include_data=True, include_notebook=True
                        )
                        st.download_button(
                            "📦 Download ZIP",
                            prev_zip_b,
                            file_name=f"{prefix}{chosen_sess['sid'][:8]}_session.zip",
                            mime="application/zip",
                            use_container_width=True,
                            key=f"dl_my_prev_zip_{chosen_sess['sid']}"
                        )

    with st.expander("📦 Save Session", expanded=False):
        _s_name = st.text_input("🏷️ Session Tag / Name (Optional):", value=st.session_state.get("session_name", ""), key="save_session_name_input").strip()
        if _s_name != st.session_state.get("session_name", ""):
            st.session_state["session_name"] = _s_name
            save_session_snapshot()
            
        _inc_mem  = st.checkbox("Memory summary (.md)",       value=True, key="save_inc_mem")
        _inc_data = st.checkbox("Downloaded data files",       value=True, key="save_inc_data")
        _inc_nb   = st.checkbox("Jupyter notebook (.ipynb)",   value=True, key="save_inc_nb")
        if st.button("Build ZIP", use_container_width=True, key="save_session_zip_btn"):
            _sid = st.session_state.get("session_id", "session")
            _s_tag = st.session_state.get("session_name", "")
            with st.spinner("Packaging session..."):
                try:
                    _zip = create_session_zip(st.session_state.messages, _sid,
                                              session_name=_s_tag,
                                              include_memory=_inc_mem,
                                              include_data=_inc_data,
                                              include_notebook=_inc_nb)
                    st.session_state["_session_zip_bytes"] = _zip
                    
                    safe_tag = re.sub(r'[^a-zA-Z0-9_-]', '_', _s_tag) if _s_tag else ""
                    prefix = f"{safe_tag}_" if safe_tag else ""
                    st.session_state["_session_zip_name"] = f"{prefix}{_sid[:8]}.zip"
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
        _uploaded = st.file_uploader(
            "Upload files",
            type=["zip", "csv", "xlsx", "json", "png", "jpg", "jpeg",
                  "pdf", "nc", "grib", "txt", "md", "geojson", "tif", "tiff"],
            accept_multiple_files=True,
            key="unified_uploader",
        )
        if _uploaded and st.button("Load", use_container_width=True, key="unified_load_btn"):
            sid_now    = st.session_state.get("session_id", "unknown")
            upload_dir = os.path.join("uploads", sid_now)
            os.makedirs(upload_dir, exist_ok=True)

            session_restored = False
            external_files   = []

            with st.spinner("Loading uploads..."):
                for uf in _uploaded:
                    raw = uf.read()
                    if uf.name.lower().endswith(".zip"):
                        try:
                            zf = zipfile.ZipFile(_io.BytesIO(raw))
                            json_files = [n for n in zf.namelist() if n.endswith("_session.json")]
                            if json_files:
                                data = json.loads(zf.read(json_files[0]))
                                st.session_state.messages = data.get("messages", st.session_state.messages)
                                st.session_state["session_tokens"] = data.get("metrics", st.session_state.get("session_tokens", {}))
                                if data.get("session_id"):
                                    st.session_state["session_id"] = data["session_id"]
                                if data.get("session_name"):
                                    st.session_state["session_name"] = data["session_name"]
                                session_restored = True
                            else:
                                for name in zf.namelist():
                                    if name.endswith("/"): continue
                                    target = os.path.join(upload_dir, os.path.basename(name))
                                    with open(target, "wb") as out:
                                        out.write(zf.read(name))
                                    external_files.append(os.path.basename(name))
                        except zipfile.BadZipFile:
                            st.error(f"{uf.name}: not a valid ZIP.")
                    else:
                        target = os.path.join(upload_dir, uf.name)
                        with open(target, "wb") as out:
                            out.write(raw)
                        external_files.append(uf.name)

            if session_restored:
                st.success("✅ Session restored. Scroll up to see history.")
            if external_files:
                files_list = "\n".join(f"- `{f}`" for f in external_files)
                note = (
                    "📎 **User uploaded external files for analysis.**\n\n"
                    f"Location: `{upload_dir}`\n\n"
                    f"Files:\n{files_list}\n\n"
                    "You may load them with pandas / xarray / PIL through "
                    "`execute_analysis_code` when the user's next request requires them."
                )
                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": note,
                    "files":   [os.path.join(upload_dir, f) for f in external_files],
                })
                st.success(f"📎 {len(external_files)} file(s) attached.")
            if not session_restored and not external_files:
                st.warning("Nothing to load.")
            st.rerun()

# --- Main Chat Interface ---
current_tag = st.session_state.get("session_name", "")
current_sid = st.session_state.get("session_id", "")[:8]

col_top_b1, col_top_b2 = st.columns([3.2, 1.2])
with col_top_b1:
    if current_tag:
        st.info(f"🏷️ **Active Session Tag:** `{current_tag}` | **Session ID:** `{current_sid}...` ({len(st.session_state.messages)} msgs)")
    elif current_sid:
        st.caption(f"Session ID: `{current_sid}...` ({len(st.session_state.messages)} msgs)")
with col_top_b2:
    if st.button("➕ Start New Fresh Session", key="btn_top_fresh_sess", use_container_width=True):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["session_name"] = ""
        st.session_state["save_session_name_input"] = ""
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]
        st.session_state.agent = None
        st.session_state.session_tokens = {'input': 0, 'output': 0, 'total': 0, 'cost': 0.0}
        st.session_state.file_scan_start_time = time.time()
        st.toast("✨ Started a fresh new session!", icon="🌱")
        time.sleep(0.3)
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What is your research question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_session_snapshot()
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not st.session_state.agent:
            if not initialize_agent():
                st.error("Agent initialization failed. Please check logs.")
                st.stop()
        
        tool_container = st.container()
        callback = SafeStreamlitCallbackHandler(tool_container)
        
        try:
            _orch_module._LAMBDA_CONTEXT = list(st.session_state.messages)

            response = st.session_state.agent.invoke(
                {"input": prompt},
                {"callbacks": [callback]}
            )
            
            output_text = response.get("output") or "I successfully processed your request."
            st.markdown(output_text)
            
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
            # Save session snapshot after every assistant response so Admin can inspect it
            save_session_snapshot()
            tag_newly_created_session_files()
            
        except Exception as e:
            error_msg = f"❌ An error occurred: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            save_session_snapshot()
