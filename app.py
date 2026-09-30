import streamlit as st
from pypdf import PdfReader
from gtts import gTTS
import tempfile
import os
import re


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PragyanAI PDF Audiobook",
    page_icon="🎧",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #F1F5F9;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #667085;
        margin-bottom: 30px;
    }

    .feature-card {
        background: Black;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #e4e7ec;
        margin-bottom: 20px;
    }

    .step-card {
        background: Black;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #e4e7ec;
        text-align: center;
    }

    .step-number {
        font-size: 28px;
        font-weight: 800;
    }

    .step-title {
        font-size: 17px;
        font-weight: 700;
        margin-top: 5px;
    }

    .info-box {
        background: #eef4ff;
        border-left: 5px solid #4f46e5;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }

    .success-box {
        background: #ecfdf3;
        border-left: 5px solid #12b76a;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text):
    """
    Detect the dominant language based on Unicode characters.

    Returns a gTTS language code.
    """

    if not text or not text.strip():
        return None

    # Kannada Unicode range
    kannada_count = len(
        re.findall(r"[\u0C80-\u0CFF]", text)
    )

    # Hindi / Devanagari Unicode range
    devanagari_count = len(
        re.findall(r"[\u0900-\u097F]", text)
    )

    # Telugu Unicode range
    telugu_count = len(
        re.findall(r"[\u0C00-\u0C7F]", text)
    )

    # Tamil Unicode range
    tamil_count = len(
        re.findall(r"[\u0B80-\u0BFF]", text)
    )

    # Malayalam Unicode range
    malayalam_count = len(
        re.findall(r"[\u0D00-\u0D7F]", text)
    )

    # Bengali Unicode range
    bengali_count = len(
        re.findall(r"[\u0980-\u09FF]", text)
    )

    counts = {
        "kn": kannada_count,
        "hi": devanagari_count,
        "te": telugu_count,
        "ta": tamil_count,
        "ml": malayalam_count,
        "bn": bengali_count
    }

    detected_language = max(
        counts,
        key=counts.get
    )

    highest_count = counts[detected_language]

    # If no Indian script is detected,
    # use English as the default.
    if highest_count == 0:
        return "en"

    return detected_language


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(uploaded_file):

    reader = PdfReader(uploaded_file)

    pages_text = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages_text.append(text)

    final_text = "\n\n".join(pages_text)

    return final_text.strip()


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# CREATE AUDIO
# ============================================================

def create_audio(text, language):

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    temp_file.close()

    try:

        speech = gTTS(
            text=text,
            lang=language,
            slow=False
        )

        speech.save(temp_file.name)

        return temp_file.name

    except Exception as error:

        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

        raise error


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎧 PragyanAI PDF Audiobook</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Convert any text-based PDF into a downloadable MP3 audiobook'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# PROCESS FLOW
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">01</div>
            <div class="step-title">📄 Upload PDF</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">02</div>
            <div class="step-title">📝 Extract Text</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">03</div>
            <div class="step-title">🌐 Detect Language</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">04</div>
            <div class="step-title">🎧 Create MP3</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# MAIN COLUMNS
# ============================================================

left, right = st.columns(
    [1, 1.5],
    gap="large"
)


# ============================================================
# LEFT PANEL
# ============================================================

with left:

    st.markdown(
        '<div class="feature-card">',
        unsafe_allow_html=True
    )

    st.subheader("📄 Upload Your PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        help="Upload a text-based PDF file."
    )

    if uploaded_file:

        st.success(
            f"Uploaded: {uploaded_file.name}"
        )

        file_size = uploaded_file.size / 1024

        st.write(
            f"**File size:** {file_size:.2f} KB"
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# RIGHT PANEL
# ============================================================

with right:

    if not uploaded_file:

        st.markdown(
            """
            <div class="feature-card">
                <h2>🎙️ PDF → Audiobook</h2>
                <p>
                Upload a PDF from the left to begin.
                The application will automatically extract
                the text, detect the language and generate
                an MP3 audiobook.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="feature-card">',
            unsafe_allow_html=True
        )

        st.subheader("⚙️ Convert PDF")

        convert_button = st.button(
            "🚀 Generate Audiobook",
            type="primary",
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        if convert_button:

            # =================================================
            # STEP 1 - EXTRACT TEXT
            # =================================================

            with st.spinner("📖 Extracting text from PDF..."):

                try:

                    extracted_text = extract_text_from_pdf(
                        uploaded_file
                    )

                    extracted_text = clean_text(
                        extracted_text
                    )

                except Exception as error:

                    st.error(
                        f"PDF extraction failed: {error}"
                    )

                    st.stop()

            if not extracted_text:

                st.error(
                    "No readable text was found in this PDF."
                )

                st.info(
                    "Please upload a text-based PDF. "
                    "Scanned image-only PDFs may require OCR."
                )

                st.stop()


            # =================================================
            # STEP 2 - DETECT LANGUAGE
            # =================================================

            with st.spinner("🌐 Detecting language..."):

                language = detect_language(
                    extracted_text
                )


            # =================================================
            # LANGUAGE NAME
            # =================================================

            language_names = {
                "en": "English",
                "kn": "Kannada",
                "hi": "Hindi",
                "te": "Telugu",
                "ta": "Tamil",
                "ml": "Malayalam",
                "bn": "Bengali"
            }

            language_name = language_names.get(
                language,
                language
            )


            # =================================================
            # DISPLAY INFORMATION
            # =================================================

            st.markdown(
                f"""
                <div class="success-box">
                    <strong>🌐 Detected Language:</strong>
                    {language_name}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.metric(
                "Extracted Characters",
                f"{len(extracted_text):,}"
            )


            # =================================================
            # SHOW TEXT
            # =================================================

            with st.expander(
                "📖 View Extracted Text"
            ):

                st.text_area(
                    "PDF Text",
                    extracted_text,
                    height=300,
                    label_visibility="collapsed"
                )


            # =================================================
            # STEP 3 - TEXT TO SPEECH
            # =================================================

            with st.spinner(
                "🎧 Converting text to speech..."
            ):

                try:

                    audio_file = create_audio(
                        extracted_text,
                        language
                    )

                except Exception as error:

                    st.error(
                        f"Audio generation failed: {error}"
                    )

                    st.stop()


            # =================================================
            # AUDIO PLAYER
            # =================================================

            st.success(
                "✅ Audiobook created successfully!"
            )

            st.subheader(
                "🎧 Your Audiobook"
            )

            with open(
                audio_file,
                "rb"
            ) as audio:

                audio_bytes = audio.read()

            st.audio(
                audio_bytes,
                format="audio/mp3"
            )


            # =================================================
            # DOWNLOAD BUTTON
            # =================================================

            output_name = os.path.splitext(
                uploaded_file.name
            )[0]

            output_name = (
                output_name
                + "_audiobook.mp3"
            )

            st.download_button(
                label="⬇️ Download MP3 Audiobook",
                data=audio_bytes,
                file_name=output_name,
                mime="audio/mpeg",
                use_container_width=True
            )


            # =================================================
            # CLEAN TEMP FILE
            # =================================================

            try:

                os.remove(audio_file)

            except Exception:

                pass


# ============================================================
# FOOTER
# ============================================================

st.write("")

st.markdown(
    """
    <div style="text-align:center; color:#667085; padding:25px;">
        🎧 <b>PragyanAI PDF Audiobook Creator</b>
        <br>
        PDF → Text → Language Detection → Speech → MP3
    </div>
    """,
    unsafe_allow_html=True
)
