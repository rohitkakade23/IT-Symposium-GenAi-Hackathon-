import streamlit as st
import fitz
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np

# Page settings
st.set_page_config(page_title="AI Notes Assistant", page_icon="📚", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
.main-title{
    font-size:40px;
    font-weight:bold;
    text-align:center;
    color:#4CAF50;
}

.subtitle{
    text-align:center;
    font-size:18px;
    color:gray;
}

.answer-box{
    background-color:#f1f3f6;
    padding:20px;
    border-radius:10px;
    border-left:6px solid #4CAF50;
    font-size:18px;
}

.footer{
    text-align:center;
    color:gray;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

# Initialize OCR
ocr = PaddleOCR(use_angle_cls=True, lang="en")

# Title
st.markdown('<p class="main-title">📚 AI Notes Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your notes and ask questions instantly</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📌 Instructions")
st.sidebar.write("""
1. Upload your **Notes PDF**
2. Wait for extraction
3. Ask questions related to the notes
4. Get instant answers

⚠ If the question is not in the notes,
the system will say:

**"I don't have enough information."**
""")

uploaded_file = st.file_uploader("📄 Upload Notes PDF", type=["pdf"])


def extract_text(pdf_path):

    text = ""

    doc = fitz.open(pdf_path)

    for page in doc:

        page_text = page.get_text()

        if page_text.strip() != "":
            text += page_text + "\n"

        images = page.get_images(full=True)

        for img in images:

            xref = img[0]
            base_image = doc.extract_image(xref)

            image_bytes = base_image["image"]

            image = Image.open(
                fitz.open("pdf", image_bytes).extract_image(0)["image"]
            )

            img_array = np.array(image)

            result = ocr.ocr(img_array)

            if result:
                for line in result[0]:
                    text += line[1][0] + "\n"

    return text


def answer_question(question, notes):

    sentences = notes.split("\n")

    best_answer = ""
    max_score = 0

    for sentence in sentences:

        score = 0

        for word in question.lower().split():
            if word in sentence.lower():
                score += 1

        if score > max_score:
            max_score = score
            best_answer = sentence

    # NEW FEATURE
    if best_answer == "" or max_score < 2:
        return "❗ I don't have enough information."

    return best_answer


if uploaded_file is not None:

    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ PDF uploaded successfully!")

    with st.spinner("🔎 Extracting notes... Please wait"):
        notes_text = extract_text("temp.pdf")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📖 Extracted Notes")
        st.text_area("Notes Content", notes_text, height=400)

    with col2:
        st.subheader("❓ Ask Questions From Your Notes")

        question = st.text_input("Type your question here")

        if st.button("🚀 Get Answer"):

            with st.spinner("Thinking..."):
                answer = answer_question(question, notes_text)

            st.markdown("### 🤖 Answer")

            st.markdown(
                f'<div class="answer-box">{answer}</div>',
                unsafe_allow_html=True
            )

st.markdown('<p class="footer">Built with ❤️ using Streamlit</p>', unsafe_allow_html=True)
