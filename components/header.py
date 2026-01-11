"""
Header component with modern navigation bar styling.
"""
import streamlit as st
from utils.auth import UserManager

def render_header():
    """Renders a modern, fixed-style header with navigation."""
    
    # Initialize view state if needed
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'generator'
    if 'show_settings_modal' not in st.session_state:
        st.session_state.show_settings_modal = False
        
    # CSS for the Header
    st.markdown("""
    <style>
    /* Top Navigation Bar Container */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Logo / Title Area */
    .nav-logo {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
    }
    
    /* Navigation Group */
    .nav-items {
        display: flex;
        gap: 15px;
        align-items: center;
    }
    
    /* Hide default Streamlit button styling for nav items to look like links/tabs */
    div[data-testid="stHorizontalBlock"] button {
        border: none !important;
        background: transparent !important;
        color: inherit !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s !important;
    }
    
    div[data-testid="stHorizontalBlock"] button:hover {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="stHorizontalBlock"] button:active, 
    div[data-testid="stHorizontalBlock"] button:focus  {
        background: rgba(255,255,255,0.1) !important;
        color: #4285F4 !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Use columns to simulate the Navbar layout
    col_logo, col_spacer, col_nav = st.columns([3, 1, 4])
    
    with col_logo:
        # We use a button that looks like text to allow resetting to home
        if st.button("🩺 Medical Anki AI", key="nav_logo_btn", help="Go to Home"):
            st.session_state.current_view = 'generator'
            st.rerun()
            
    with col_nav:
        # Right-aligned navigation items
        # We put them in a sub-columns block to push them right visually or just list them
        n_col1, n_col2, n_col3 = st.columns(3)
        
        with n_col1:
            if st.button("✨ Generator", key="nav_gen"):
                st.session_state.current_view = 'generator'
                st.rerun()
                
        with n_col2:
            if st.button("💬 Chat", key="nav_chat"):
                st.session_state.current_view = 'chat'
                st.rerun()

        with n_col3:
            # Settings Icon
            if st.button("⚙️ Settings", key="nav_settings"):
                st.session_state.show_settings_modal = not st.session_state.show_settings_modal
                st.rerun()

def render_settings_modal(config):
    """Renders the settings modal overlay."""
    import os

    if not st.session_state.get('show_settings_modal', False):
        return

    auth_manager = UserManager()
    email = st.session_state.get('user_email')
    is_guest = st.session_state.get('is_guest', False)
    
    # Modal CSS
    st.markdown("""
    <style>
    div[data-testid="stExpander"] {
        background-color: var(--background-color);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # We use a container that acts as a dialog
    with st.expander("⚙️ Application Settings", expanded=True):
        st.caption("Press 'Close' to save and exit.")
        
        tab_gen, tab_api, tab_anki = st.tabs(["General", "API Keys", "AnkiConnect"])
        
        with tab_gen:
            st.markdown("##### Preferences")
            chunk_size = st.slider("Chunk Size", 5000, 20000, st.session_state.get('chunk_size', 10000), 1000)
            st.session_state['chunk_size'] = chunk_size
            
            theme = st.radio("Theme Mode", ["Dark", "Light"], horizontal=True, index=0 if st.session_state.get('theme_mode', 'dark') == 'dark' else 1)
            st.session_state['theme_mode'] = theme.lower()
            
        with tab_api:
            st.markdown("##### Manage Keys")
            if is_guest:
                st.warning("Guest Mode: Keys are temporary.")
            else:
                user_keys = st.session_state.get('user_keys', {})
                
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    google_k = st.text_input("Gemini Key", value=user_keys.get("google", ""), type="password")
                    if st.button("Save Gemini"):
                        auth_manager.save_keys(email, {**user_keys, "google": google_k})
                        st.session_state.user_keys["google"] = google_k
                        st.success("Saved!")
                        
                with col_k2:
                    zai_k = st.text_input("Z.AI Key", value=user_keys.get("zai", ""), type="password")
                    if st.button("Save Z.AI"):
                         auth_manager.save_keys(email, {**user_keys, "zai": zai_k})
                         st.session_state.user_keys["zai"] = zai_k
                         st.success("Saved!")
                         
                st.caption("OpenRouter key can also be updated here.")
        
        with tab_anki:
            current_url = st.session_state.get('anki_connect_url') or os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
            new_url = st.text_input("AnkiConnect URL", value=current_url)
            st.session_state['anki_connect_url'] = new_url

        if st.button("✕ Close Settings", use_container_width=True):
            st.session_state.show_settings_modal = False
            st.rerun()
