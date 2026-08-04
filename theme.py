import streamlit as st

def init_theme():
    """Ensure session_state.theme is initialized to 'dark' by default."""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    return st.session_state.theme == "dark"

def render_theme_toggle():
    """Renders a clean theme toggle button in header or sidebar."""
    is_dark = init_theme()
    button_label = "☀️ Light Mode" if is_dark else "🌙 Dark Mode"
    if st.button(button_label, key="header_theme_toggle_btn"):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()
    return st.session_state.theme == "dark"
