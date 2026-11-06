
import streamlit as st

st.set_page_config(
    page_title="ResearchPilot AI",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 ResearchPilot AI")

st.subheader("Your AI-powered research assistant")

st.write(
    "Upload research papers, ask questions, "
    "and explore your documents using AI."
)

st.info("Welcome! Your ResearchPilot journey starts here.")

uploaded_files = st.file_uploader(
    "Upload your research papers (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} PDF(s) uploaded successfully!")
