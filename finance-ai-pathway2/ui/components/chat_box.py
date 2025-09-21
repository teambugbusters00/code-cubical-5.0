"""
Chat Box Component for Streamlit
Provides reusable chat interface components
"""

import streamlit as st
from typing import List, Dict, Any, Callable
import time

def display_chat_message(message: Dict[str, Any], avatar: Optional[str] = None):
    """
    Display a single chat message

    Args:
        message: Message dictionary with 'role' and 'content' keys
        avatar: Avatar emoji or path for the message sender
    """
    role = message.get('role', 'unknown')
    content = message.get('content', '')

    if role == 'user':
        avatar = avatar or '👤'
        alignment = 'right'
    elif role == 'assistant':
        avatar = avatar or '🤖'
        alignment = 'left'
    else:
        avatar = avatar or '❓'
        alignment = 'left'

    # Create columns for alignment
    if alignment == 'right':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write(f"**You:** {content}")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.write(f"**Assistant:**")
        with col2:
            st.write(content)

def display_chat_history(messages: List[Dict[str, Any]]):
    """
    Display chat history

    Args:
        messages: List of message dictionaries
    """
    for message in messages:
        display_chat_message(message)

def create_chat_input(placeholder: str = "Type your message here...") -> str:
    """
    Create a chat input field

    Args:
        placeholder: Placeholder text for the input

    Returns:
        User input string
    """
    return st.text_input(
        "",
        placeholder=placeholder,
        key=f"chat_input_{time.time()}"  # Unique key to prevent conflicts
    )

def display_typing_indicator():
    """
    Display a typing indicator
    """
    st.write("🤖 Assistant is typing...")
    with st.empty():
        for _ in range(3):
            st.write("🤖 Assistant is typing...")
            time.sleep(0.5)
            st.write("🤖 Assistant is typing.")
            time.sleep(0.5)
            st.write("🤖 Assistant is typing..")
            time.sleep(0.5)

def display_error_message(error: str):
    """
    Display an error message

    Args:
        error: Error message to display
    """
    st.error(f"❌ Error: {error}")

def display_success_message(message: str):
    """
    Display a success message

    Args:
        message: Success message to display
    """
    st.success(f"✅ {message}")

def display_info_message(message: str):
    """
    Display an info message

    Args:
        message: Info message to display
    """
    st.info(f"ℹ️ {message}")

def create_expanding_section(title: str, content: str, default_expanded: bool = False):
    """
    Create an expanding section

    Args:
        title: Section title
        content: Section content
        default_expanded: Whether section should be expanded by default
    """
    with st.expander(title, expanded=default_expanded):
        st.write(content)

def display_metrics_grid(metrics: Dict[str, Any], columns: int = 3):
    """
    Display metrics in a grid layout

    Args:
        metrics: Dictionary of metric names to values
        columns: Number of columns in the grid
    """
    cols = st.columns(columns)

    for i, (label, value) in enumerate(metrics.items()):
        with cols[i % columns]:
            st.metric(label, value)

def create_progress_bar(label: str, value: float):
    """
    Create a progress bar

    Args:
        label: Progress bar label
        value: Progress value (0.0 to 1.0)
    """
    st.write(f"**{label}:**")
    st.progress(value)

def display_data_table(data: List[Dict[str, Any]], key_column: str = None):
    """
    Display data as a table

    Args:
        data: List of dictionaries to display
        key_column: Column to use as index
    """
    if not data:
        st.info("No data to display")
        return

    df = st.dataframe(data)

    # Add download button
    if st.button("📥 Download Data"):
        import pandas as pd
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="data.csv",
            mime="text/csv"
        )

def create_sidebar_section(title: str, content: Callable):
    """
    Create a sidebar section

    Args:
        title: Section title
        content: Function that renders the section content
    """
    st.sidebar.markdown(f"**{title}**")
    content()

def display_loading_spinner(text: str = "Loading..."):
    """
    Display a loading spinner

    Args:
        text: Loading text to display
    """
    with st.spinner(text):
        time.sleep(0.1)  # Small delay for better UX

# Chat message templates
CHAT_TEMPLATES = {
    "greeting": "Hello! I'm your financial assistant. How can I help you today?",
    "error": "I apologize, but I encountered an error. Please try again.",
    "no_data": "I don't have enough information to answer that question.",
    "thinking": "Let me think about that...",
    "searching": "Searching for relevant information...",
    "analyzing": "Analyzing the data..."
}

def get_chat_template(template_name: str) -> str:
    """
    Get a chat template message

    Args:
        template_name: Name of the template

    Returns:
        Template message string
    """
    return CHAT_TEMPLATES.get(template_name, "I'm here to help!")

def format_currency(amount: float, currency: str = "$") -> str:
    """
    Format currency amount

    Args:
        amount: Amount to format
        currency: Currency symbol

    Returns:
        Formatted currency string
    """
    return f"{currency}{amount:.2f}"

def format_percentage(value: float) -> str:
    """
    Format percentage value

    Args:
        value: Percentage value

    Returns:
        Formatted percentage string
    """
    return f"{value:+.2f}%"

def format_number(value: float) -> str:
    """
    Format large numbers with appropriate suffixes

    Args:
        value: Number to format

    Returns:
        Formatted number string
    """
    if value >= 1e9:
        return f"{value/1e9:.1f}B"
    elif value >= 1e6:
        return f"{value/1e6:.1f}M"
    elif value >= 1e3:
        return f"{value/1e3:.1f}K"
    else:
        return f"{value:.0f}"