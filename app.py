import streamlit as st
import logging
import os
from dotenv import load_dotenv

from components.session import init_session_state
from components.sidebar import render_sidebar
from components.generator import render_generator
from components.chat import render_pdf_chat, render_general_chat
from components.login import render_login
from components.onboarding import render_onboarding
from components.history import render_history
from components.header import render_header, render_settings_modal
from components.standalone_chat import render_standalone_chat
from components.cards_view import render_cards_view

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()

# Versioning
VERSION = "v2.6.0"

# Page Config
st.set_page_config(
    page_title=f"Medical PDF to Anki {VERSION}",
    page_icon="🩺",
    layout="wide"
)

# Custom CSS for the app
st.markdown(f"""
    <style>
    /* Version Badge */
    .version-badge {{
        position: fixed;
        top: 10px;
        left: 10px;
        background-color: rgba(0, 0, 0, 0.05);
        color: rgba(0, 0, 0, 0.5);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        z-index: 999999;
        pointer-events: none;
        font-family: 'Inter', sans-serif;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }}
    [data-theme="dark"] .version-badge {{
        background-color: rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* Hide Streamlit's default menu button (3 dots) */
    #MainMenu {{
        visibility: hidden;
    }}
    
    /* Hide hamburger menu */
    header[data-testid="stHeader"] {{
        display: none;
    }}
    
    /* Main container styling */
    .main .block-container {{
        padding-top: 2rem;
        max-width: 1400px;
    }}
    
    /* Button styling improvements */
    .stButton > button {{
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
    }}
    
    /* Card styling */
    .element-container {{
        transition: all 0.2s ease;
    }}
    
    /* Header styling */
    h1 {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Divider styling */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), transparent);
    }}
    </style>
    <div class="version-badge">{VERSION}</div>
""", unsafe_allow_html=True)

# Initialize Session
init_session_state()

# Get current view
current_view = st.session_state.get('current_view', 'generator')

# --- Render Header (Navigation) ---
# Render header ABOVE the title if logged in
if st.session_state.get('is_logged_in', False):
    render_header()

# Title (Only show on generator/cards)
if current_view != 'chat':
    st.title("🩺 Medical PDF to Anki Converter (AI-Powered)")


# --- Initialize Cookie Manager for Session Persistence ---
import extra_streamlit_components as stx
from utils.auth import UserManager

# Initialize Cookie Manager
cookie_manager = stx.CookieManager()

# Check for existing session cookie if not logged in
if not st.session_state.get('is_logged_in', False):
    # Wait a bit for cookies to load (stx limitation sometimes)
    cookies = cookie_manager.get_all()
    session_token = cookies.get("session_token")
    
    if session_token:
        auth_manager = UserManager()
        # We need to find which user owns this token. 
        # Ideally UserManager should have a method to find user by token.
        # But our current implementation stores sessions inside user dict.
        # We'll need a helper or scan. Scanning is okay for small user base.
        # Let's add a helper to UserManager or just scan here.
        # To be cleaner, let's update UserManager to support 'get_user_by_token'.
        # For now, let's do a quick scan since we didn't add that method yet.
        
        # Actually, let's implement get_user_by_token in auth.py first to be clean.
        # But to avoid context switching too much, we can do:
        
        all_users = auth_manager._load_data()
        found_email = None
        for email, data in all_users.items():
            if "sessions" in data and session_token in data["sessions"]:
                # specific token validation
                if auth_manager.validate_session(email, session_token):
                    found_email = email
                    break
        
        if found_email:
             # Auto-login
            user_data = all_users[found_email]
            st.session_state['is_logged_in'] = True
            st.session_state['user_email'] = found_email
            st.session_state['user_keys'] = auth_manager.get_keys(found_email) # Decrypt keys
            st.session_state['is_guest'] = False
            
            # Init empty defaults if needed
            if 'chapters_data' not in st.session_state: st.session_state['chapters_data'] = []
            
            # Optional: Refresh token expiry?
            # For now, just proceed inside.

# --- Auth Flow ---
if not st.session_state.get('is_logged_in', False):
    render_login(cookie_manager) # Pass cookie manager to login

    st.stop() # Stop execution here until logged in

# --- Onboarding Flow ---
if not st.session_state.get('keys_configured', False):
    user_keys = st.session_state.get('user_keys', {})
    is_guest = st.session_state.get('is_guest', False)
    
    # Check if environment keys are available for guests
    has_env_keys = (
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("OPENROUTER_API_KEY") or 
        os.getenv("ZAI_API_KEY")
    )
    
    if not user_keys:
        if is_guest and has_env_keys:
            # Guests can skip onboarding if environment keys are available
            st.session_state['keys_configured'] = True
            st.session_state['using_free_tier'] = True
            st.rerun()
        else:
            render_onboarding()
            st.stop()
    else:
        st.session_state['keys_configured'] = True
        st.rerun()

# --- Main App ---

# Render Sidebar & Get Config (Skip in Chat Mode to avoid double controls)
config = {}
if current_view != 'chat':
    config = render_sidebar(cookie_manager=cookie_manager)

# Render Settings Modal if open
if st.session_state.get('show_settings_modal', False):
    render_settings_modal(config)

# --- Rate Limit Warning Banner ---
if st.session_state.get('free_tier_rate_limited', False):
    rate_msg = st.session_state.get('rate_limit_message', 'Rate limit reached on free tier.')
    st.warning(f"⚠️ **Free Tier Rate Limited**: {rate_msg}\n\nYou're using the free shared API key. To avoid limits, add your own API key in Settings.")
    # Reset after showing
    st.session_state['free_tier_rate_limited'] = False
    st.session_state['rate_limit_message'] = None

st.divider()

# --- View Routing ---
if current_view == 'chat':
    # Full-screen chat view
    render_standalone_chat()

elif current_view == 'cards':
    # Created cards view
    render_cards_view()

else:
    # Default: Generator view
    render_generator(config)
    
    # PDF Chat if chapters exist
    if 'chapters_data' in st.session_state and st.session_state['chapters_data']:
        st.divider()
        render_pdf_chat(
            st.session_state['chapters_data'], 
            config["provider"], 
            config["model_name"]
        )
