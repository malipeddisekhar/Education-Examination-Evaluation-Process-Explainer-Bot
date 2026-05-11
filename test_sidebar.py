"""
Quick test to verify sidebar is visible
Run: streamlit run test_sidebar.py
"""
import streamlit as st

st.set_page_config(
    page_title="Sidebar Test",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.title("🎓 Sidebar Test")
    st.write("If you can see this, the sidebar is working!")
    st.button("Test Button")
    st.selectbox("Test Select", ["Option 1", "Option 2"])
    st.slider("Test Slider", 0, 100, 50)

# Main area
st.title("Main Area")
st.write("👈 Check if the sidebar is visible on the left")
st.info("If the sidebar is collapsed, click the arrow (>) in the top-left corner to expand it.")

if st.button("Click me in main area"):
    st.success("Button clicked!")
