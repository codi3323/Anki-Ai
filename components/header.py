"""
Header component with navigation icons.
"""
import streamlit as st


def render_header():
    """Renders the header with settings, cards, and chat icons."""
    
    # Initialize view state
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'generator'
    if 'show_settings_modal' not in st.session_state:
        st.session_state.show_settings_modal = False
    
    # Header icons CSS
    st.markdown("""
    <style>
    .header-icons {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
        padding: 12px 20px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
        border-radius: 16px;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    .header-icon-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 18px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: inherit;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 14px;
    }
    
    .header-icon-btn:hover {
        background: rgba(139, 92, 246, 0.2);
        border-color: rgba(139, 92, 246, 0.4);
        transform: translateY(-2px);
    }
    
    .header-icon-btn.active {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-color: transparent;
        color: white;
    }
    
    .header-icon-btn svg {
        width: 18px;
        height: 18px;
    }
    
    /* Settings Modal */
    .settings-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 99999;
        backdrop-filter: blur(4px);
    }
    
    .settings-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
        background: var(--background-color, #1a1a2e);
        border-radius: 20px;
        padding: 2rem;
        z-index: 100000;
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .settings-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .settings-title {
        font-size: 1.5rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .settings-section {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .settings-section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #8b5cf6;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create columns for icons
    _, col_icons, _ = st.columns([1, 2, 1])
    
    with col_icons:
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if st.button("⚙️ Settings", key="header_settings", use_container_width=True, type="secondary"):
                st.session_state.show_settings_modal = not st.session_state.show_settings_modal
                st.rerun()
        
        with btn_col2:
            is_cards_active = st.session_state.current_view == 'cards'
            btn_type = "primary" if is_cards_active else "secondary"
            if st.button("📋 Created Cards", key="header_cards", use_container_width=True, type=btn_type):
                st.session_state.current_view = 'cards' if st.session_state.current_view != 'cards' else 'generator'
                st.rerun()
        
        with btn_col3:
            is_chat_active = st.session_state.current_view == 'chat'
            btn_type = "primary" if is_chat_active else "secondary"
            if st.button("💬 Chat", key="header_chat", use_container_width=True, type=btn_type):
                st.session_state.current_view = 'chat' if st.session_state.current_view != 'chat' else 'generator'
                st.rerun()


def render_settings_modal(config):
    """Renders the settings modal overlay."""
    from utils.auth import UserManager
    import os
    
    if not st.session_state.get('show_settings_modal', False):
        return
    
    auth_manager = UserManager()
    email = st.session_state.get('user_email')
    is_guest = st.session_state.get('is_guest', False)
    
    st.markdown("---")
    st.markdown("## ⚙️ Settings")
    
    # Close button
    if st.button("✕ Close Settings", key="close_settings_btn"):
        st.session_state.show_settings_modal = False
        st.rerun()
    
    st.markdown("---")
    
    # Create tabs for different settings sections
    tab_general, tab_api, tab_anki, tab_dev = st.tabs(["🎨 General", "🔑 API Keys", "🔗 AnkiConnect", "🛠️ Developer"])
    
    with tab_general:
        st.subheader("General Settings")
        
        # Chunk Size
        st.markdown("##### 📏 Chunk Size (characters)")
        st.caption("Controls how text is split when processing PDFs. Larger chunks provide more context but may be slower.")
        new_chunk_size = st.slider(
            "Chunk Size", 
            min_value=5000, 
            max_value=20000, 
            value=st.session_state.get('chunk_size', 10000), 
            step=1000,
            key="settings_chunk_size",
            label_visibility="collapsed"
        )
        st.session_state['chunk_size'] = new_chunk_size
        
        st.divider()
        
        # Theme Toggle
        st.markdown("##### 🎨 Theme")
        current_theme = st.session_state.get('theme_mode', 'dark')
        col_dark, col_light = st.columns(2)
        with col_dark:
            if st.button("🌙 Dark Mode", use_container_width=True, 
                        type="primary" if current_theme == 'dark' else "secondary"):
                st.session_state['theme_mode'] = 'dark'
                st.rerun()
        with col_light:
            if st.button("☀️ Light Mode", use_container_width=True,
                        type="primary" if current_theme == 'light' else "secondary"):
                st.session_state['theme_mode'] = 'light'
                st.rerun()
        
        if current_theme == 'light':
            st.info("💡 To fully enable light mode, go to Streamlit's Settings (⋮) → Settings → Theme → Light")
    
    with tab_api:
        st.subheader("API Key Management")
        
        if is_guest:
            st.warning("⚠️ Guest Mode: Keys are temporary and won't be saved. Log in to save keys.")
            return
        
        st.caption("Add or remove API keys. Keys are stored securely and never displayed after saving.")
        
        user_keys = st.session_state.get('user_keys', {})
        
        # Google Gemini
        st.markdown("##### 🌐 Google Gemini")
        has_google = bool(user_keys.get("google"))
        if has_google:
            st.success("✅ Gemini Key Configured")
            if st.button("🗑️ Remove Gemini Key", key="remove_google"):
                user_keys["google"] = ""
                auth_manager.save_keys(email, {"google": ""})
                st.session_state.user_keys = user_keys
                st.success("Gemini Key removed!")
                st.rerun()
        else:
            st.markdown("[Get Gemini API Key](https://aistudio.google.com/app/apikey)")
            new_key = st.text_input("Enter Gemini Key", type="password", key="add_google_key", placeholder="AIza...")
            if new_key and st.button("💾 Save Gemini Key", key="save_google"):
                auth_manager.save_keys(email, {"google": new_key})
                st.session_state.user_keys["google"] = new_key
                st.success("Gemini Key saved!")
                st.rerun()
        
        st.divider()
        
        # OpenRouter
        st.markdown("##### 🔀 OpenRouter")
        has_openrouter = bool(user_keys.get("openrouter"))
        if has_openrouter:
            st.success("✅ OpenRouter Key Configured")
            if st.button("🗑️ Remove OpenRouter Key", key="remove_openrouter"):
                user_keys["openrouter"] = ""
                auth_manager.save_keys(email, {"openrouter": ""})
                st.session_state.user_keys = user_keys
                st.success("OpenRouter Key removed!")
                st.rerun()
        else:
            st.markdown("[Get OpenRouter Key](https://openrouter.ai/keys)")
            new_key = st.text_input("Enter OpenRouter Key", type="password", key="add_openrouter_key", placeholder="sk-or-...")
            if new_key and st.button("💾 Save OpenRouter Key", key="save_openrouter"):
                auth_manager.save_keys(email, {"openrouter": new_key})
                st.session_state.user_keys["openrouter"] = new_key
                st.success("OpenRouter Key saved!")
                st.rerun()
        
        st.divider()
        
        # Z.AI
        st.markdown("##### 🤖 Z.AI")
        has_zai = bool(user_keys.get("zai"))
        if has_zai:
            st.success("✅ Z.AI Key Configured")
            if st.button("🗑️ Remove Z.AI Key", key="remove_zai"):
                user_keys["zai"] = ""
                auth_manager.save_keys(email, {"zai": ""})
                st.session_state.user_keys = user_keys
                st.success("Z.AI Key removed!")
                st.rerun()
        else:
            st.markdown("[Get Z.AI API Key](https://z.ai/)")
            new_key = st.text_input("Enter Z.AI Key", type="password", key="add_zai_key", placeholder="Enter key...")
            if new_key and st.button("💾 Save Z.AI Key", key="save_zai"):
                auth_manager.save_keys(email, {"zai": new_key})
                st.session_state.user_keys["zai"] = new_key
                st.success("Z.AI Key saved!")
                st.rerun()
    
    with tab_anki:
        st.subheader("AnkiConnect Settings")
        st.caption("Configure the connection to AnkiConnect for pushing cards directly to Anki.")
        
        current_url = st.session_state.get('anki_connect_url') or os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
        
        st.markdown("##### 🔗 AnkiConnect URL")
        anki_url = st.text_input(
            "URL",
            value=current_url,
            help="Default: http://localhost:8765. For cloud deployment, use a tunnel URL.",
            key="settings_anki_url",
            label_visibility="collapsed"
        )
        st.session_state['anki_connect_url'] = anki_url
        
        st.info("💡 **Tip:** For local use, keep the default URL. For cloud deployment, you'll need to set up a tunnel to your local Anki.")
    
    with tab_dev:
        st.subheader("Developer Options")
        st.caption("Advanced settings for development and debugging.")
        
        # Developer Mode Toggle
        dev_mode = st.toggle(
            "🔧 Developer Mode",
            value=st.session_state.get('developer_mode', False),
            help="Enables verbose logging and debugging features.",
            key="settings_dev_mode"
        )
        st.session_state['developer_mode'] = dev_mode
        
        if dev_mode:
            st.success("Developer Mode is enabled. Check the console for verbose logs.")
            
            st.divider()
            
            # Debug info
            st.markdown("##### Debug Information")
            with st.expander("Session State", expanded=False):
                debug_state = {k: str(v)[:100] + "..." if len(str(v)) > 100 else str(v) 
                              for k, v in st.session_state.items() 
                              if not k.startswith('_')}
                st.json(debug_state)
    
    st.markdown("---")
