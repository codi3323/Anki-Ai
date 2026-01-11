"""
Standalone Chat component with full-screen view, model selector, and file upload.
"""
import streamlit as st
from utils.llm_handler import get_chat_response, configure_gemini, configure_openrouter, configure_zai
from utils.pdf_processor import extract_text_from_pdf
import os


def render_standalone_chat():
    """Renders the full standalone chat interface with model selector and upload."""
    
    # Chat header
    st.markdown("""
    <style>
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
        border-radius: 16px;
        margin-bottom: 1rem;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    .chat-title {
        font-size: 1.5rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .file-upload-zone {
        border: 2px dashed rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        background: rgba(139, 92, 246, 0.05);
        transition: all 0.3s ease;
    }
    
    .file-upload-zone:hover {
        border-color: rgba(139, 92, 246, 0.6);
        background: rgba(139, 92, 246, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 💬 AI Chat")
    
    # Back button
    if st.button("← Back to Generator", key="chat_back_btn"):
        st.session_state.current_view = 'generator'
        st.rerun()
    
    st.divider()
    
    # Sidebar for model selection and file upload
    col_sidebar, col_chat = st.columns([1, 3])
    
    with col_sidebar:
        st.markdown("### 🎛️ Chat Settings")
        
        # Provider Selection
        st.markdown("##### AI Provider")
        chat_provider = st.radio(
            "Provider",
            ["Google Gemini", "OpenRouter", "Z.AI"],
            key="chat_provider_select",
            label_visibility="collapsed"
        )
        
        # Model Selection based on provider
        if chat_provider == "Google Gemini":
            model_options = {
                "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite (Fastest)",
                "gemini-2.5-flash": "Gemini 2.5 Flash (Standard)",
                "gemini-3-flash": "Gemini 3.0 Flash (Smarter)",
                "gemma-3-27b-it": "Gemma 3 27B (High Throughput)"
            }
        elif chat_provider == "OpenRouter":
            model_options = {
                "xiaomi/mimo-v2-flash:free": "Xiaomi Mimo V2 Flash",
                "google/gemini-2.0-flash-exp:free": "Gemini 2.0 Flash Exp",
                "mistralai/devstral-2512:free": "Mistral Devstral",
                "qwen/qwen3-coder:free": "Qwen 3 Coder",
                "google/gemma-3-27b-it:free": "Gemma 3 27B IT"
            }
        else:  # Z.AI
            model_options = {
                "GLM-4.7": "GLM-4.7 (Standard)",
                "GLM-4.5-air": "GLM-4.5 Air (Lightweight)"
            }
        
        st.markdown("##### Model")
        chat_model = st.selectbox(
            "Select Model",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            key="chat_model_select",
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # File Upload Section
        st.markdown("### 📁 Context Files")
        st.caption("Upload files to chat with them")
        
        uploaded_files = st.file_uploader(
            "Upload files",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            key="chat_file_upload",
            label_visibility="collapsed"
        )
        
        # Initialize chat context
        if 'chat_context' not in st.session_state:
            st.session_state.chat_context = ""
        
        if uploaded_files:
            context_texts = []
            for file in uploaded_files:
                file.seek(0)
                if file.name.endswith('.pdf'):
                    try:
                        pdf_text = extract_text_from_pdf(file)
                        context_texts.append(f"[{file.name}]\n{pdf_text}")
                        st.success(f"✅ {file.name}")
                    except Exception as e:
                        st.error(f"❌ {file.name}: {str(e)}")
                else:
                    try:
                        text = file.read().decode('utf-8')
                        context_texts.append(f"[{file.name}]\n{text}")
                        st.success(f"✅ {file.name}")
                    except Exception as e:
                        st.error(f"❌ {file.name}: {str(e)}")
            
            if context_texts:
                st.session_state.chat_context = "\n\n---\n\n".join(context_texts)
                st.info(f"📄 {len(context_texts)} file(s) loaded as context")
        
        if st.session_state.chat_context:
            if st.button("🗑️ Clear Context", key="clear_chat_context"):
                st.session_state.chat_context = ""
                st.rerun()
        
        st.divider()
        
        # Clear chat history
        if st.button("🔄 New Chat", key="new_chat_btn", use_container_width=True):
            st.session_state.standalone_messages = []
            st.rerun()
    
    with col_chat:
        # Initialize messages
        if "standalone_messages" not in st.session_state:
            st.session_state.standalone_messages = []
        
        # Chat container
        chat_container = st.container(height=500)
        
        with chat_container:
            if not st.session_state.standalone_messages:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; color: rgba(255,255,255,0.5);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
                    <h3>Start a conversation</h3>
                    <p>Upload files on the left to chat with them, or just start typing!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for message in st.session_state.standalone_messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message...", key="standalone_chat_input"):
            # Add user message
            st.session_state.standalone_messages.append({"role": "user", "content": prompt})
            
            # Get provider code
            provider_code = "google" if chat_provider == "Google Gemini" else ("zai" if chat_provider == "Z.AI" else "openrouter")
            
            # Configure client if needed
            user_keys = st.session_state.get('user_keys', {})
            
            if provider_code == "google":
                key = user_keys.get("google") or os.getenv("GOOGLE_API_KEY")
                if key and not st.session_state.get('google_client'):
                    st.session_state.google_client = configure_gemini(key)
            elif provider_code == "openrouter":
                key = user_keys.get("openrouter") or os.getenv("OPENROUTER_API_KEY")
                if key and not st.session_state.get('openrouter_client'):
                    st.session_state.openrouter_client = configure_openrouter(key)
            else:  # zai
                key = user_keys.get("zai") or os.getenv("ZAI_API_KEY")
                if key and not st.session_state.get('zai_client'):
                    st.session_state.zai_client = configure_zai(key)
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Prepare context
                        context = st.session_state.chat_context if st.session_state.chat_context else ""
                        
                        response = get_chat_response(
                            st.session_state.standalone_messages,
                            context,
                            provider_code,
                            chat_model,
                            google_client=st.session_state.get('google_client'),
                            openrouter_client=st.session_state.get('openrouter_client'),
                            zai_client=st.session_state.get('zai_client'),
                            direct_chat=not bool(context)
                        )
                    st.markdown(response)
            
            st.session_state.standalone_messages.append({"role": "assistant", "content": response})
            st.rerun()
