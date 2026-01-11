"""
Created Decks view - displays cards grouped by deck with actions.
"""
import streamlit as st
import pandas as pd
from utils.history import CardHistory
from utils.data_processing import push_notes_to_anki, format_cards_for_ankiconnect, check_ankiconnect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def render_cards_view():
    """Renders the created decks view."""
    
    # Styling
    st.markdown("""
    <style>
    .deck-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.2s ease;
    }
    
    .deck-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(139, 92, 246, 0.3);
    }
    
    .deck-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    .deck-meta {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        gap: 15px;
        align-items: center;
    }
    
    .count-badge {
        background: rgba(139, 92, 246, 0.2);
        color: #a78bfa;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: rgba(255, 255, 255, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🗂️ Created Decks")
    
    # Back button
    if st.button("← Back to Generator", key="cards_back_btn"):
        st.session_state.current_view = 'generator'
        st.rerun()
    
    st.divider()
    
    email = st.session_state.get('user_email', 'Guest')
    history_manager = CardHistory()
    
    # Get history
    df = history_manager.get_history_df(email)
    
    if df.empty:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🗂️</div>
            <h3>No Decks Yet</h3>
            <p>Generate some cards to see your decks here!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Stats row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Cards", len(df))
    with col2:
        unique_decks = df['deck'].nunique() if 'deck' in df.columns else 0
        st.metric("Total Decks", unique_decks)
    with col3:
        # Today's cards
        if 'timestamp' in df.columns:
            try:
                today = datetime.now().date()
                df['date_obj'] = pd.to_datetime(df['timestamp']).dt.date
                today_count = len(df[df['date_obj'] == today])
                st.metric("Cards Created Today", today_count)
            except:
                st.metric("Cards Created Today", 0)
    
    st.divider()
    
    # Controls
    search = st.text_input("🔍 Search Decks", placeholder="Filter by deck name...", key="deck_search")
    
    # Get unique decks and sort by latest timestamp in that deck
    if 'deck' in df.columns:
        # Group by deck to get stats
        deck_stats = []
        for deck_name, group in df.groupby('deck'):
            latest_time = group['timestamp'].max() if 'timestamp' in group.columns else ""
            deck_stats.append({
                "name": deck_name,
                "count": len(group),
                "latest": latest_time,
                "df": group
            })
        
        # Sort by latest activity (newest first)
        deck_stats.sort(key=lambda x: x['latest'], reverse=True)
        
        # Filter if searching
        if search:
            deck_stats = [d for d in deck_stats if search.lower() in d['name'].lower()]
            
        if not deck_stats:
            st.info("No decks found matching your search.")
            return

        # Render Decks
        for deck in deck_stats:
            deck_name = deck['name']
            count = deck['count']
            deck_df = deck['df']
            
            with st.container():
                st.markdown(f"""
                <div class="deck-card">
                    <div class="deck-title">{deck_name}</div>
                    <div class="deck-meta">
                        <span class="count-badge">{count} cards</span>
                        <span>Last updated: {pd.to_datetime(deck['latest']).strftime('%Y-%m-%d %H:%M') if deck['latest'] else 'N/A'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Actions Row
                col_csv, col_push = st.columns([1, 1])
                
                with col_csv:
                    csv = deck_df.to_csv(index=False)
                    st.download_button(
                        f"📥 Download CSV",
                        csv,
                        file_name=f"{deck_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key=f"dl_{deck_name}",
                        use_container_width=True
                    )
                
                with col_push:
                    push_btn_key = f"push_{deck_name}"
                    if st.button(f"📤 Push to Anki", key=push_btn_key, use_container_width=True):
                        # Push logic
                        status_ok, msg = check_ankiconnect()
                        if not status_ok:
                            st.error(f"Cannot connect to Anki: {msg}")
                        else:
                            with st.spinner(f"Pushing {count} cards to '{deck_name}'..."):
                                notes = format_cards_for_ankiconnect(deck_df)
                                success, errors = push_notes_to_anki(notes)
                                
                                if success > 0:
                                    st.toast(f"✅ Successfully pushed {success} cards to Anki!")
                                    if errors:
                                        st.warning(f"Some cards failed ({len(errors)}). Check console logs.")
                                else:
                                    st.error("Failed to push cards.")
                                    if errors:
                                        st.error(f"Error: {errors[0]}")
    
    else:
        st.warning("No deck information found in history.")
    
    st.divider()
    
    # Global Actions
    if st.button("🗑️ Clear All History", type="secondary"):
        if st.session_state.get('confirm_clear'):
            history_manager.clear_history(email)
            st.session_state.confirm_clear = False
            st.success("History cleared!")
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("Click again to confirm clearing all history.")
