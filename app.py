import streamlit as st
import requests
import PyPDF2
import docx
import io

# LM Studio API URL (Check LM Studio settings for the correct URL)
LM_STUDIO_API_URL = "http://localhost:1234/v1/completions"

st.set_page_config(page_title="Document Summarizer", layout="wide")
st.title("📄 Document Summarizer using LM Studio & Streamlit")

# Initialize session state for conversation history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to call LM Studio API
def query_lm(prompt):
    payload = {
        "model": "llama-3.2-1b-instruct",  # Replace with the model name in LM Studio
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.5
    }
    
    try:
        response = requests.post(LM_STUDIO_API_URL, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        return f"❌ Error: {e}"

# Function to extract text from documents
def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()
    text = ""

    if file_type == "pdf":
        with io.BytesIO(uploaded_file.read()) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"

    elif file_type == "txt":
        text = uploaded_file.read().decode("utf-8")

    elif file_type == "docx":
        doc = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])

    return text.strip()

# File upload section
uploaded_file = st.file_uploader("Upload a PDF, TXT, or DOCX file", type=["pdf", "txt", "docx"])

if uploaded_file:
    extracted_text = extract_text_from_file(uploaded_file)
    
    # Display extracted text (optional)
    st.subheader("📃 Extracted Text Preview")
    st.text_area("Extracted Text", extracted_text[:2000], height=300)

    # Summarization button
    if st.button("Summarize Document"):
        with st.spinner("Summarizing..."):
            summary = query_lm(f"Summarize this document:\n\n{extracted_text}")
            
            # Save history
            st.session_state.chat_history.append({"user": "Summarize document", "assistant": summary})

            # Display summary
            st.subheader("📜 Summary")
            st.markdown(summary)

# Conversation history display
st.subheader("📜 Conversation History")
for entry in st.session_state.chat_history:
    with st.expander(f"🧑‍💻 {entry['user'][:50]}..."):
        st.markdown(f"**You:** {entry['user']}")
        st.markdown(f"**LM:** {entry['assistant']}")

# Clear button
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.success("Chat history cleared!")
