import streamlit as st
from pypdf import PdfReader
from gtts import gTTS
import os
import tempfile
import re
import time

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PragyanAI PDF to Audiobook",
    page_icon="🎧",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #777;
        margin-bottom: 30px;
    }

    .info-box {
        padding: 18px;
        border-radius: 12px;
        background-color: #f5f7fb;
        border: 1px solid #e5e7eb;
        margin-bottom: 20px;
    }

    .success-box {
        padding: 18px;
        border-radius: 12px;
        background-color: #ecfdf5;
        border: 1px solid #10b981;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🎧 PragyanAI PDF to Audiobook</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Convert your PDF documents into MP3 audiobooks</div>',
    unsafe_allow_html=True
)

st.divider()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Options")

    language = st.selectbox(
        "🎙️ Voice Language",
        options=[
            ("English", "en"),
            ("Hindi", "hi"),
            ("Kannada", "kn"),
            ("Tamil", "ta"),
            ("Telugu", "te"),
            ("Malayalam", "ml"),
            ("French", "fr"),
            ("German", "de"),
            ("Spanish", "es"),
            ("Italian", "it")
        ],
        format_func=lambda x: x[0]
    )

    language_code = language[1]

    st.markdown("---")

    st.info(
        """
        **How it works**

        1. Upload PDF
        2. Extract text
        3. Convert text to speech
        4. Generate MP3 audiobook
        5. Download audiobook
        """
    )

# ============================================================
# PDF UPLOAD
# ============================================================

st.subheader("📄 Upload PDF")

uploaded_file = st.file_uploader(
    "Choose a PDF document",
    type=["pdf"],
    help="Upload a text-based PDF document."
)

# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_pdf_text(pdf_file):

    reader = PdfReader(pdf_file)

    pages_text = []

    for page in reader.pages:

        try:
            text = page.extract_text()

            if text:
                pages_text.append(text)

        except Exception:
            continue

    return "\n\n".join(pages_text)


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove strange control characters
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

    return text.strip()


# ============================================================
# SPLIT TEXT
# ============================================================

def split_text(text, max_chars=4000):

    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # If adding paragraph exceeds limit
        if len(current_chunk) + len(paragraph) + 1 <= max_chars:

            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

        else:

            if current_chunk:
                chunks.append(current_chunk)

            # Very long paragraph
            if len(paragraph) > max_chars:

                sentences = re.split(
                    r"(?<=[.!?])\s+",
                    paragraph
                )

                temp = ""

                for sentence in sentences:

                    if len(temp) + len(sentence) + 1 <= max_chars:
                        temp += " " + sentence
                    else:

                        if temp:
                            chunks.append(temp.strip())

                        temp = sentence

                if temp:
                    current_chunk = temp.strip()
                else:
                    current_chunk = ""

            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ============================================================
# GENERATE AUDIO
# ============================================================

def generate_audiobook(text, language_code):

    chunks = split_text(text)

    if not chunks:
        raise ValueError("No readable text found in the PDF.")

    temp_dir = tempfile.mkdtemp()

    audio_files = []

    progress_bar = st.progress(0)

    status_text = st.empty()

    total_chunks = len(chunks)

    for index, chunk in enumerate(chunks):

        status_text.info(
            f"🎙️ Generating audio part {index + 1} of {total_chunks}..."
        )

        output_file = os.path.join(
            temp_dir,
            f"part_{index + 1}.mp3"
        )

        try:

            tts = gTTS(
                text=chunk,
                lang=language_code,
                slow=False
            )

            tts.save(output_file)

            audio_files.append(output_file)

        except Exception as e:

            raise RuntimeError(
                f"Error generating audio part {index + 1}: {e}"
            )

        progress_bar.progress(
            (index + 1) / total_chunks
        )

        # Small delay to avoid aggressive requests
        time.sleep(0.3)

    status_text.info("🔄 Combining audiobook parts...")

    # ========================================================
    # COMBINE MP3 FILES WITHOUT FFMPEG / FFPROBE
    # ========================================================

    final_file = os.path.join(
        temp_dir,
        "PragyanAI_Audiobook.mp3"
    )

    with open(final_file, "wb") as final_audio:

        for audio_file in audio_files:

            with open(audio_file, "rb") as part:

                final_audio.write(part.read())

    status_text.success("✅ Audiobook generated successfully!")

    progress_bar.progress(1.0)

    return final_file


# ============================================================
# MAIN APPLICATION
# ============================================================

if uploaded_file is not None:

    st.success(
        f"📄 Uploaded: **{uploaded_file.name}**"
    )

    # --------------------------------------------------------
    # PDF DETAILS
    # --------------------------------------------------------

    file_size = uploaded_file.size / 1024

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📦 File Size",
            f"{file_size:.1f} KB"
        )

    with col2:
        st.metric(
            "📄 File Type",
            "PDF"
        )

    with col3:
        st.metric(
            "🎙️ Language",
            language[0]
        )

    st.divider()

    # --------------------------------------------------------
    # EXTRACT TEXT BUTTON
    # --------------------------------------------------------

    if st.button(
        "📖 Extract PDF Text",
        use_container_width=True
    ):

        with st.spinner("📖 Reading PDF..."):

            try:

                extracted_text = extract_pdf_text(
                    uploaded_file
                )

                extracted_text = clean_text(
                    extracted_text
                )

                if not extracted_text:

                    st.error(
                        "❌ No readable text found in this PDF."
                    )

                    st.warning(
                        "This may be a scanned/image-only PDF. "
                        "OCR is required for scanned PDFs."
                    )

                else:

                    st.session_state["pdf_text"] = extracted_text

                    st.success(
                        "✅ PDF text extracted successfully!"
                    )

            except Exception as e:

                st.error(
                    f"❌ Error reading PDF: {e}"
                )


# ============================================================
# DISPLAY EXTRACTED TEXT
# ============================================================

if "pdf_text" in st.session_state:

    text = st.session_state["pdf_text"]

    st.subheader("📖 Extracted Text")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Characters",
            f"{len(text):,}"
        )

    with col2:
        st.metric(
            "Words",
            f"{len(text.split()):,}"
        )

    with st.expander(
        "👀 Preview Extracted Text",
        expanded=True
    ):

        preview_text = text[:15000]

        st.text_area(
            "PDF Content",
            preview_text,
            height=350
        )

        if len(text) > 15000:

            st.info(
                f"Showing first 15,000 characters "
                f"out of {len(text):,} characters."
            )

    st.divider()

    # ========================================================
    # GENERATE AUDIO BUTTON
    # ========================================================

    st.subheader("🎧 Create Audiobook")

    st.write(
        "Convert the extracted PDF text into an MP3 audiobook."
    )

    if st.button(
        "🎙️ Generate Audiobook",
        type="primary",
        use_container_width=True
    ):

        try:

            final_audio = generate_audiobook(
                text,
                language_code
            )

            # Store path
            st.session_state["audio_file"] = final_audio

        except Exception as e:

            st.error(
                f"❌ Audiobook generation error: {e}"
            )


# ============================================================
# AUDIO RESULT
# ============================================================

if "audio_file" in st.session_state:

    audio_file = st.session_state["audio_file"]

    if os.path.exists(audio_file):

        st.divider()

        st.subheader("🎧 Your Audiobook")

        st.success(
            "✅ Your PDF has been converted into an audiobook!"
        )

        # Audio player
        with open(audio_file, "rb") as audio:

            audio_bytes = audio.read()

        st.audio(
            audio_bytes,
            format="audio/mp3"
        )

        st.download_button(
            label="⬇️ Download MP3 Audiobook",
            data=audio_bytes,
            file_name="PragyanAI_Audiobook.mp3",
            mime="audio/mpeg",
            use_container_width=True
        )

        st.markdown(
            """
            <div class="success-box">
            <b>🎉 Audiobook Ready!</b><br>
            You can listen to it above or download the MP3 file.
            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎧 PragyanAI PDF to Audiobook Creator | "
    "PDF → Text → Speech → MP3"
)
