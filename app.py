import streamlit as st
from pathlib import Path
from pdf_processor import extract_pages
from retriever import retrieve_chunks
from answer_generator import generate_answer, rewrite_question
from document_ingestor import index_documents, delete_document_from_index
from document_manager import (
    register_document,
    get_documents,
    remove_document_record
)
st.set_page_config(
    page_title="ResearchPilot AI",
    page_icon="🔬",
    layout="wide"
)
# ---------- Chat History ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🔬 ResearchPilot AI")
st.subheader("Your AI-powered research assistant")
st.write("Upload research papers and explore their contents using AI.")

# ---------- Storage folders ----------
documents_folder = Path("data/documents")
documents_folder.mkdir(parents=True, exist_ok=True)



# ---------- Chat Interface ----------
st.divider()
st.header("💬 Ask ResearchPilot")

RELEVANCE_THRESHOLD = 1.2

# Display previous conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask something about your research papers...")

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("ResearchPilot is thinking..."):

            try:
                # Rewrite follow-up using previous conversation
                search_query = rewrite_question(
                    question,
                    st.session_state.messages[:-1]
                )

                # Search ChromaDB
                retrieved_chunks = retrieve_chunks(search_query)


                if (
                    not retrieved_chunks
                    or retrieved_chunks[0]["distance"] > RELEVANCE_THRESHOLD
                ):
                    answer = (
                        "I couldn't find sufficiently relevant information "
                        "in your indexed documents."
                    )
                else:
                    answer = generate_answer(
                        search_query,
                        retrieved_chunks,
                        st.session_state.messages[:-1]
                    )

            except Exception as error:
                answer = f"Something went wrong: {error}"

            st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

# ---------- Upload section ----------
st.divider()
st.header("📄 Upload papers")

uploaded_files = st.file_uploader(
    "Upload your research papers (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        filename = Path(uploaded_file.name).name

        # Check the persistent registry
        if filename in get_documents():
            st.info(f"Already indexed: {filename}")
            continue

        try:
            with st.spinner(f"Processing {filename}..."):
                pdf_bytes = uploaded_file.getvalue()

                # Save original PDF
                (documents_folder / filename).write_bytes(pdf_bytes)

                # Extract pages
                pages = extract_pages(pdf_bytes, filename)

                # Index into ChromaDB
                total_chunks = index_documents(pages)

                # Register permanently
                register_document(
                    filename=filename,
                    page_count=len(pages),
                    chunk_count=total_chunks
                )

            st.success(
                f"Successfully indexed {filename}! "
                f"({len(pages)} pages, {total_chunks} chunks)"
            )

        except Exception as error:
            st.error(f"Could not process {filename}: {error}")


# ---------- My Documents ----------
st.divider()
st.header("📚 My Documents")

documents = get_documents()

if documents:

    for filename, details in documents.items():

        with st.expander(filename):

            st.write(f"Pages: {details['pages']}")
            st.write(f"Chunks: {details['chunks']}")
            st.write(f"Indexed at: {details['indexed_at']}")

            if st.button(
                f"🗑️ Delete {filename}",
                key=f"delete_{filename}"
            ):

                try:
                    # Step 1: Delete chunks from ChromaDB
                    deleted_chunks = delete_document_from_index(filename)

                    # Step 2: Delete registry record and original PDF
                    remove_document_record(filename)

                    st.success(
                        f"Deleted {filename} "
                        f"({deleted_chunks} chunks removed)."
                    )

                    st.rerun()

                except Exception as error:
                    st.error(f"Deletion failed: {error}")

else:
    st.info("No documents have been indexed yet.")
