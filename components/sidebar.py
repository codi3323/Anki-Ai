"""
Sidebar configuration component - Streamlined version.
"""
import streamlit as st
import os
from utils.llm_handler import configure_gemini, configure_openrouter, configure_zai
from components.session import load_fallback_keys
from utils.auth import UserManager


def render_sidebar():
    """Renders the sidebar and returns configuration."""
    auth_manager = UserManager()
    email = st.session_state.get('user_email')
    user_keys = st.session_state.get('user_keys', {})

    with st.sidebar:
        # User info
        if email:
            st.caption(f"👤 {email}")
        
        st.divider()
        
        # Provider Selection
        st.markdown("##### 🤖 AI Provider")
        provider = st.radio(
            "Provider", 
            ["Google Gemini", "OpenRouter", "Z.AI"], 
            index=0,
            label_visibility="collapsed"
        )
        
        api_key = None
        model_name = None
        summary_model = None
        
        # Helper to check if key exists (saved or in env)
        def has_key(provider_key, env_var):
            return bool(user_keys.get(provider_key)) or bool(os.getenv(env_var))
        
        # --- Google Gemini ---
        if provider == "Google Gemini":
            fallback_keys = load_fallback_keys()
            saved_key = user_keys.get("google", "")
            env_key = os.getenv("GOOGLE_API_KEY", "")
            is_guest = st.session_state.get('is_guest', False)
            
            if saved_key and not is_guest:
                api_key = saved_key
                st.session_state.google_client = configure_gemini(api_key, fallback_keys=fallback_keys)
                st.success("✅ Gemini Ready")
                st.session_state['using_free_tier'] = False
            elif env_key:
                # Guests and users without saved keys use environment key
                api_key = env_key
                st.session_state.google_client = configure_gemini(api_key, fallback_keys=fallback_keys)
                if is_guest:
                    st.info("🆓 Free Tier (Guest) - Limited requests")
                    st.session_state['using_free_tier'] = True
                else:
                    st.info("📦 Using Environment Key")
                    st.session_state['using_free_tier'] = False
            elif fallback_keys:
                api_key = fallback_keys[0]
                st.session_state.google_client = configure_gemini(api_key, fallback_keys=fallback_keys[1:])
                st.info("🆓 Free Tier (Fallback) - Limited requests")
                st.session_state['using_free_tier'] = True
            else:
                st.error("❌ No Gemini Key. Add one in ⚙️ Settings.")
                api_key = None
                st.session_state.google_client = configure_gemini(None, fallback_keys=[])
                st.session_state['using_free_tier'] = False
    
            model_options = {
                "gemini-2.5-flash-lite": "Flash Lite (Fastest)",
                "gemini-2.5-flash": "Flash (Standard)",
                "gemini-3-flash": "Flash 3.0 (Smarter)",
                "gemma-3-27b-it": "Gemma 27B (High TPM)"
            }
            summary_model = "gemma-3-27b-it"

        # --- OpenRouter ---
        elif provider == "OpenRouter": 
            saved_key = user_keys.get("openrouter", "")
            env_key = os.getenv("OPENROUTER_API_KEY", "")
            is_guest = st.session_state.get('is_guest', False)
            
            if saved_key and not is_guest:
                api_key = saved_key
                st.session_state.openrouter_client = configure_openrouter(api_key)
                st.success("✅ OpenRouter Ready")
                st.session_state['using_free_tier'] = False
            elif env_key:
                api_key = env_key
                st.session_state.openrouter_client = configure_openrouter(api_key)
                if is_guest:
                    st.info("🆓 Free Tier (Guest) - Limited requests")
                    st.session_state['using_free_tier'] = True
                else:
                    st.info("📦 Using Environment Key")
                    st.session_state['using_free_tier'] = False
            else:
                st.error("❌ No OpenRouter Key. Add one in ⚙️ Settings.")
                api_key = None
                st.session_state.openrouter_client = configure_openrouter(None)
                st.session_state['using_free_tier'] = False
    
            model_options = {
                "xiaomi/mimo-v2-flash:free": "Mimo V2 Flash",
                "google/gemini-2.0-flash-exp:free": "Gemini 2.0 Flash",
                "mistralai/devstral-2512:free": "Devstral",
                "qwen/qwen3-coder:free": "Qwen 3 Coder",
                "google/gemma-3-27b-it:free": "Gemma 3 27B"
            }
            summary_model = "google/gemini-2.0-flash-exp:free"

        # --- Z.AI ---
        elif provider == "Z.AI":
            saved_key = user_keys.get("zai", "")
            env_key = os.getenv("ZAI_API_KEY", "")
            is_guest = st.session_state.get('is_guest', False)
            
            if saved_key and not is_guest:
                api_key = saved_key
                st.session_state.zai_client = configure_zai(api_key)
                st.success("✅ Z.AI Ready")
                st.session_state['using_free_tier'] = False
            elif env_key:
                api_key = env_key
                st.session_state.zai_client = configure_zai(api_key)
                if is_guest:
                    st.info("🆓 Free Tier (Guest) - Limited requests")
                    st.session_state['using_free_tier'] = True
                else:
                    st.info("📦 Using Environment Key")
                    st.session_state['using_free_tier'] = False
            else:
                st.error("❌ No Z.AI Key. Add one in ⚙️ Settings.")
                api_key = None
                st.session_state.zai_client = configure_zai(None)
                st.session_state['using_free_tier'] = False
            
            model_options = {
                "GLM-4.7": "GLM-4.7 (Standard)",
                "GLM-4.5-air": "GLM-4.5 Air (Light)"
            }
            summary_model = "GLM-4.7"
        
        # --- Model Selection ---
        st.markdown("##### 📦 Model")
        selected_model_key = st.selectbox(
            "Model", 
            options=list(model_options.keys()), 
            format_func=lambda x: model_options[x],
            index=0,
            label_visibility="collapsed"
        )
        model_name = selected_model_key
        
        st.divider()
        
        # Quick access settings (visual only, main settings are in modal)
        is_guest = st.session_state.get('is_guest', False)
        
        if is_guest:
            st.info("⚠️ Guest Mode")
        
        # Get settings from session state (set by settings modal)
        chunk_size = st.session_state.get('chunk_size', 10000)
        developer_mode = st.session_state.get('developer_mode', False)
        anki_url = st.session_state.get('anki_connect_url') or os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
        
        # Legacy toggles for backward compatibility (hidden)
        show_general_chat = False
        show_history = False
        
        st.divider()
        
        # Logout/Reset
        col_logout, col_clear = st.columns(2)
        with col_logout:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        
        with col_clear:
            if st.button("🗑️ Reset", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    return {
        "provider": provider,
        "api_key": api_key,
        "model_name": model_name,
        "summary_model": summary_model,
        "chunk_size": chunk_size,
        "developer_mode": developer_mode,
        "show_general_chat": show_general_chat,
        "anki_url": anki_url,
        "show_history": show_history
    }
