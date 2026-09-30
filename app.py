import streamlit as st
from pypdf import PdfReader
from langdetect import detect, detect_langs, LangDetectException
from gtts import gTTS
from io import BytesIO
import re


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PragyanAI PDF Audiobook Creator",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */
    .stApp {
        background: linear-gradient(
            135deg,
            #f5f7ff 0%,
            #eef2ff 45%,
            #f8fafc 100%
        );
    }

    /* Main container */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Header */
    .main-header {
        background: linear-gradient(
            135deg,
            #4f46e5,
            #7c3aed
        );
        padding: 30px 35px;
        border-radius: 22px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.20);
    }

    .main-header h1 {
        margin: 0;
        font-size: 34px;
        font-weight: 800;
    }

    .main-header p {
        margin-top: 8px;
        margin-bottom: 0;
        font-size: 16px;
        opacity: 0.92;
    }

    /* Step cards */
    .step-card {
        background: white;
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        min-height: 125px;
    }

    .step-number {
        font-size: 13px;
        font-weight: 800;
        color: #6366f1;
        letter-spacing: 1px;
    }

    .step-icon {
        font-size: 28px;
        margin: 6px 0;
    }

    .step-title {
        font-size: 15px;
        font-weight: 700;
        color: #111827;
    }

    /* Section cards */
    .section-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06);
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 8px;
    }

    .section-description {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 18px;
    }

    /* Information cards */
    .info-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 18px;
        margin-top: 10px;
    }

    .info-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
    }

    .info-value {
        color: #111827;
        font-size: 18px;
        font-weight: 800;
        margin-top: 4px;
    }

    /* Text preview */
    .text-preview {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 18px;
        max-height: 350px;
        overflow-y: auto;
        color: #334155;
        line-height: 1.7;
        font-size: 14px;
    }

    /* Success box */
    .success-card {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 16px;
        padding: 20px;
        color: #065f46;
        margin-top: 15px;
    }

    /* Upload box */
    [data-testid="stFileUploader"] {
        background: #f8fafc;
        border: 2px dashed #a5b4fc;
        border-radius: 18px;
        padding: 15px;
    }

    /* Buttons */
    .stDownloadButton button {
        width: 100%;
        border-radius: 12px;
        font-weight: 700;
        padding: 12px;
    }

    /* Hide Streamlit menu/footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-header">
        <h1>🎧 PragyanAI PDF Audiobook Creator</h1>
        <p>
            Convert your PDF document into a downloadable MP3 audiobook
            with automatic language detection.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PROCESS STEPS
# ============================================================

step1, step2, step3, step4 = st.columns(4)

with step1:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">01</div>
            <div class="step-icon">📄</div>
            <div class="step-title">Upload PDF</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with step2:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">02</div>
            <div class="step-icon">📝</div>
            <div class="step-title">Extract Text</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with step3:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">03</div>
            <div class="step-icon">🌐</div>
            <div class="step-title">Detect Language</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with step4:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">04</div>
            <div class="step-icon">🎧</div>
            <div class="step-title">Create MP3</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# PDF UPLOAD
# ============================================================

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">📄 Upload Your PDF</div>
        <div class="section-description">
            Select a text-based PDF document to create your audiobook.
        </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text):
    """
    Detect language automatically from extracted PDF text.
    No manual language selection.
    """

    if not text or len(text.strip()) < 20:
        return None, 0.0

    try:
        results = detect_langs(text)

        if not results:
            return None, 0.0

        best = results[0]

        language_code = best.lang
        probability = best.prob

        return language_code, probability

    except LangDetectException:
        return None, 0.0

    except Exception:
        return None, 0.0


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Clean extracted PDF text before sending it to gTTS.
    """

    if not text:
        return ""

    # Replace multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    return text.strip()


# ============================================================
# CREATE AUDIO
# ============================================================

def create_audiobook(text, language_code):
    """
    Convert the complete extracted PDF text directly to MP3.

    No pydub.
    No PyAudio.
    No FFmpeg.
    """

    audio_buffer = BytesIO()

    tts = gTTS(
        text=text,
        lang=language_code,
        slow=False
    )

    tts.write_to_fp(audio_buffer)

    audio_buffer.seek(0)

    return audio_buffer.getvalue()


# ============================================================
# MAIN PROCESS
# ============================================================

if uploaded_file is not None:

    # --------------------------------------------------------
    # FILE INFORMATION
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">📦 PDF Information</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    file_size_kb = uploaded_file.size / 1024

    with col1:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">FILE NAME</div>
                <div class="info-value">📄 {uploaded_file.name}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">FILE SIZE</div>
                <div class="info-value">{file_size_kb:.1f} KB</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="info-card">
                <div class="info-label">FILE TYPE</div>
                <div class="info-value">PDF</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # EXTRACT TEXT
    # --------------------------------------------------------

    with st.spinner("📖 Extracting text from PDF..."):

        try:
            reader = PdfReader(uploaded_file)

            extracted_pages = []

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_pages.append(page_text)

            extracted_text = "\n\n".join(extracted_pages)

            extracted_text = clean_text(extracted_text)

        except Exception as e:
            st.error(f"❌ Error extracting PDF text: {e}")
            st.stop()


    # --------------------------------------------------------
    # CHECK TEXT
    # --------------------------------------------------------

    if not extracted_text:

        st.error(
            "❌ No readable text was found in this PDF. "
            "Please upload a text-based PDF."
        )

        st.stop()


    # --------------------------------------------------------
    # TEXT INFORMATION
    # --------------------------------------------------------

    character_count = len(extracted_text)
    word_count = len(extracted_text.split())

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">📝 Extracted Text</div>
            <div class="section-description">
                Text successfully extracted from your PDF.
            </div>
        """,
        unsafe_allow_html=True
    )

    info1, info2 = st.columns(2)

    with info1:
        st.metric(
            "Characters",
            f"{character_count:,}"
        )

    with info2:
        st.metric(
            "Words",
            f"{word_count:,}"
        )

    st.text_area(
        "Extracted PDF Text",
        extracted_text,
        height=300,
        label_visibility="collapsed"
    )

    st.markdown("</div>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # DETECT LANGUAGE
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">🌐 Language Detection</div>
            <div class="section-description">
                The application detects the language automatically
                from the extracted PDF text.
            </div>
        """,
        unsafe_allow_html=True
    )

    language_code, confidence = detect_language(extracted_text)

    if language_code:

        confidence_percent = confidence * 100

        st.success(
            f"Detected language: **{language_code.upper()}** "
            f"({confidence_percent:.1f}% confidence)"
        )

        st.caption(
            "The detected language will be used automatically for speech generation."
        )

    else:

        st.warning(
            "⚠️ Language could not be detected reliably from this PDF."
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # GENERATE AUDIO
    # --------------------------------------------------------

    if language_code:

        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">🎧 Create MP3 Audiobook</div>
                <div class="section-description">
                    Convert the extracted PDF text into speech.
                </div>
            """,
            unsafe_allow_html=True
        )

        generate_button = st.button(
            "🎙️ Generate MP3 Audiobook",
            use_container_width=True,
            type="primary"
        )

        if generate_button:

            try:

                with st.spinner(
                    "🎧 Converting PDF text into audiobook..."
                ):

                    audio_data = create_audiobook(
                        extracted_text,
                        language_code
                    )

                st.success(
                    "✅ Audiobook created successfully!"
                )

                st.audio(
                    audio_data,
                    format="audio/mp3"
                )

                # Create output filename
                original_name = uploaded_file.name.rsplit(
                    ".",
                    1
                )[0]

                output_filename = (
                    f"{original_name}_audiobook.mp3"
                )

                st.download_button(
                    label="⬇️ Download MP3 Audiobook",
                    data=audio_data,
                    file_name=output_filename,
                    mime="audio/mpeg",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"❌ Audiobook generation failed: {e}"
                )

                st.info(
                    "Please check your internet connection and "
                    "try again."
                )

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.markdown(
        """
        <div class="section-card" style="text-align:center; padding:45px;">
            <div style="font-size:55px;">📄</div>
            <div class="section-title">
                Upload Your PDF to Get Started
            </div>
            <div class="section-description">
                Your PDF will be processed automatically:
                Extract Text → Detect Language → Speech → MP3
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
