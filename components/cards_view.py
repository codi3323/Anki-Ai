"""
Created Cards view - displays all cards grouped by day.
"""
import streamlit as st
import pandas as pd
from utils.history import CardHistory
from datetime import datetime, timedelta


def render_cards_view():
    """Renders the created cards view with day-based grouping."""
    
    # Styling
    st.markdown("""
    <style>
    .cards-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .day-section {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .day-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .day-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #8b5cf6;
    }
    
    .day-count {
        background: rgba(139, 92, 246, 0.2);
        color: #a78bfa;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .card-item {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.2s ease;
    }
    
    .card-item:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(139, 92, 246, 0.3);
    }
    
    .card-front {
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    .card-back {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
    }
    
    .card-meta {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.4);
    }
    
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: rgba(255, 255, 255, 0.5);
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📋 Created Cards")
    
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
            <div class="empty-state-icon">📋</div>
            <h3>No Cards Yet</h3>
            <p>Start creating Anki cards to see them here!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Cards", len(df))
    
    with col2:
        unique_decks = df['deck'].nunique() if 'deck' in df.columns else 0
        st.metric("🗂️ Decks", unique_decks)
    
    with col3:
        if 'timestamp' in df.columns:
            try:
                today = datetime.now().date()
                df['date'] = pd.to_datetime(df['timestamp']).dt.date
                today_count = len(df[df['date'] == today])
                st.metric("📅 Today", today_count)
            except:
                st.metric("📅 Today", 0)
    
    with col4:
        if 'timestamp' in df.columns:
            try:
                week_ago = (datetime.now() - timedelta(days=7)).date()
                week_count = len(df[df['date'] >= week_ago])
                st.metric("📊 This Week", week_count)
            except:
                st.metric("📊 This Week", 0)
    
    st.divider()
    
    # Filters
    col_filter1, col_filter2, col_filter3 = st.columns([2, 1, 1])
    
    with col_filter1:
        search = st.text_input("🔍 Search cards", placeholder="Search front or back text...", key="cards_search")
    
    with col_filter2:
        if 'deck' in df.columns:
            deck_options = ["All Decks"] + list(df['deck'].unique())
            selected_deck = st.selectbox("Filter by Deck", deck_options, key="cards_deck_filter")
        else:
            selected_deck = "All Decks"
    
    with col_filter3:
        sort_order = st.selectbox("Sort", ["Newest First", "Oldest First"], key="cards_sort")
    
    # Apply filters
    filtered_df = df.copy()
    
    if search:
        mask = (
            filtered_df['front'].str.contains(search, case=False, na=False) |
            filtered_df['back'].str.contains(search, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if selected_deck != "All Decks":
        filtered_df = filtered_df[filtered_df['deck'] == selected_deck]
    
    # Sort by timestamp
    if 'timestamp' in filtered_df.columns:
        ascending = sort_order == "Oldest First"
        filtered_df = filtered_df.sort_values('timestamp', ascending=ascending)
    
    st.caption(f"Showing {len(filtered_df)} of {len(df)} cards")
    
    if filtered_df.empty:
        st.info("No cards match your filters.")
        return
    
    # Group by date
    if 'timestamp' in filtered_df.columns:
        try:
            filtered_df['date'] = pd.to_datetime(filtered_df['timestamp']).dt.date
            grouped = filtered_df.groupby('date')
            
            # Sort groups by date
            sorted_dates = sorted(grouped.groups.keys(), reverse=(sort_order == "Newest First"))
            
            for date in sorted_dates:
                group = grouped.get_group(date)
                
                # Format date label
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                
                if date == today:
                    date_label = "🌟 Today"
                elif date == yesterday:
                    date_label = "📅 Yesterday"
                else:
                    date_label = f"📅 {date.strftime('%A, %B %d, %Y')}"
                
                with st.expander(f"{date_label} ({len(group)} cards)", expanded=(date == today)):
                    for _, row in group.iterrows():
                        with st.container():
                            col_content, col_actions = st.columns([5, 1])
                            
                            with col_content:
                                st.markdown(f"**Q:** {row['front']}")
                                st.markdown(f"**A:** {row['back']}")
                                st.caption(f"Deck: {row.get('deck', 'Unknown')} • {pd.to_datetime(row['timestamp']).strftime('%H:%M')}")
                            
                            with col_actions:
                                # Copy button (placeholder, Streamlit doesn't have clipboard)
                                pass
                            
                            st.divider()
        
        except Exception as e:
            # Fallback to simple list
            st.warning(f"Could not group by date: {e}")
            st.dataframe(filtered_df[['front', 'back', 'deck', 'timestamp']])
    else:
        st.dataframe(filtered_df)
    
    # Export section
    st.divider()
    
    col_export, col_clear = st.columns(2)
    
    with col_export:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 Export as CSV",
            csv,
            file_name=f"anki_cards_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_clear:
        if st.button("🗑️ Clear All History", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_clear'):
                history_manager.clear_history(email)
                st.session_state.confirm_clear = False
                st.success("History cleared!")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing all history.")
