"""
Card History UI component.
Displays all previously generated Anki cards.
"""
import streamlit as st
import pandas as pd
from utils.history import CardHistory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def render_history():
    """Renders the card history view."""
    st.header("📜 Card History")

    email = st.session_state.get('user_email', 'Guest')
    history_manager = CardHistory()

    # Get history
    df = history_manager.get_history_df(email)

    if df.empty:
        st.info("No cards generated yet. Start creating Anki cards to see them here!")
        return

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cards", len(df))
    with col2:
        unique_decks = df['deck'].nunique() if 'deck' in df.columns else 0
        st.metric("Decks", unique_decks)
    with col3:
        if 'timestamp' in df.columns:
            try:
                latest = pd.to_datetime(df['timestamp']).max()
                st.metric("Last Created", latest.strftime("%Y-%m-%d"))
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing timestamp: {e}")
                st.metric("Last Created", "N/A")

    st.divider()

    # Filters
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        search = st.text_input("🔍 Search cards", placeholder="Search front or back...")
    with col_filter2:
        if 'deck' in df.columns:
            deck_options = ["All Decks"] + list(df['deck'].unique())
            selected_deck = st.selectbox("Filter by Deck", deck_options)
        else:
            selected_deck = "All Decks"

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

    # Sort by timestamp (newest first)
    if 'timestamp' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('timestamp', ascending=False)

    st.caption(f"Showing {len(filtered_df)} of {len(df)} cards")

    # Display cards
    if not filtered_df.empty:
        # Prepare display DataFrame
        display_df = filtered_df[['front', 'back', 'deck', 'timestamp']].copy()
        display_df.columns = ['Front', 'Back', 'Deck', 'Created']

        # Format timestamp
        if 'Created' in display_df.columns:
            try:
                display_df['Created'] = pd.to_datetime(display_df['Created']).dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError) as e:
                logger.warning(f"Error formatting timestamp: {e}")
                pass

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Front": st.column_config.TextColumn("Front", width="medium"),
                "Back": st.column_config.TextColumn("Back", width="large"),
                "Deck": st.column_config.TextColumn("Deck", width="small"),
                "Created": st.column_config.TextColumn("Created", width="small"),
            }
        )

        # Export option
        st.divider()
        col_export, col_clear = st.columns(2)

        with col_export:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download as CSV",
                csv,
                file_name=f"anki_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        with col_clear:
            if st.button("🗑️ Clear History", type="secondary"):
                history_manager.clear_history(email)
                st.success("History cleared!")
                st.rerun()
