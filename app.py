import streamlit as st
from pypdf import PdfReader
from gtts import gTTS
from langdetect import detect, LangDetectException
from io import BytesIO
import re


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PragyanAI PDF Audiobook Creator",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN PAGE ---------- */

    .stApp {
        background: linear-gradient(
            135deg,
            #f8fbff 0%,
            #eef5ff 45%,
            #f7f3ff 100%
        );
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ---------- HEADER ---------- */

    .main-header {
        background: linear-gradient(
            135deg,
            #4f46e5,
            #7c3aed,
            #9333ea
        );

        padding: 32px 38px;
        border-radius: 24px;
        color: white;
        margin-bottom: 28px;

        box-shadow:
            0 12px 35px rgba(79, 70, 229, 0.25);
    }

    .main-header h1 {
        font-size: 38px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }

    .main-header p {
        font-size: 17px;
        margin-top: 10px;
        margin-bottom: 0;
        opacity: 0.92;
    }


    /* ---------- STEP CARDS ---------- */

    .step-card {
        background: white;
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        min-height: 125px;

        border: 1px solid #e5e7eb;

        box-shadow:
            0 6px 18px rgba(15, 23, 42, 0.06);
    }

    .step-number {
        font-size: 13px;
        font-weight: 800;
        color: #6366f1;
        letter-spacing: 1px;
    }

    .step-icon {
        font-size: 27px;
        margin: 8px 0;
    }

    .step-title {
        font-size: 15px;
        font-weight: 700;
        color: #1e293b;
    }


    /* ---------- SECTION TITLE ---------- */

    .section-title {
        color: #172554;
        font-size: 25px;
        font-weight: 800;
        margin-top: 25px;
        margin-bottom: 8px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 18px;
    }


    /* ---------- UPLOAD BOX ---------- */

    .upload-title {
        background: linear-gradient(
            135deg,
            #ffffff,
            #f8faff
        );

        border: 2px dashed #818cf8;
        border-radius: 20px;
        padding: 30px;

        text-align: center;

        box-shadow:
            0 8px 25px rgba(79, 70, 229, 0.08);
    }

    .upload-icon {
        font-size: 48px;
        margin-bottom: 8px;
    }

    .upload-heading {
        color: #312e81;
        font-size: 25px;
        font-weight: 800;
    }

    .upload-text {
        color: #64748b;
        font-size: 15px;
    }


    /* ---------- INFORMATION CARDS ---------- */

    .info-card {
        background: white;
        border-radius: 18px;
        padding: 22px;

        border: 1px solid #e2e8f0;

        box-shadow:
            0 6px 20px rgba(15, 23, 42, 0.06);
    }

    .info-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .info-value {
        color: #172554;
        font-size: 18px;
        font-weight: 800;
    }


    /* ---------- SUCCESS BOX ---------- */

    .success-box {
        background: linear-gradient(
            135deg,
            #ecfdf5,
            #f0fdf4
        );

        border: 1px solid #86efac;
        border-radius: 18px;
        padding: 22px;
        margin-top: 20px;
    }

    .success-title {
        color: #166534;
        font-size: 22px;
        font-weight: 800;
    }

    .success-text {
        color: #15803d;
        font-size: 15px;
    }


    /* ---------- TEXT PREVIEW ---------- */

    .preview-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 20px;
        margin-top: 20px;
    }


    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #111827,
            #1e1b4b
        );
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }


    /* ---------- BUTTON ---------- */

    .stDownloadButton button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(
            135deg,
            #4f46e5,
            #7c3aed
        );
        color: white;
        border: none;
        font-weight: 700;
        padding: 12px;
    }

    .stDownloadButton button:hover {
        background: linear-gradient(
            135deg,
            #4338ca,
            #6d28d9
        );
        color: white;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        margin-top: 45px;
        color: #64748b;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LANGUAGE MAPPING
# ============================================================

LANGUAGE_NAMES = {
    "en": "English",
    "kn": "Kannada",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "pa": "Punjabi",
    "ur": "Urdu",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese"
}


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:10px;">
            <div style="font-size:50px;">🎧</div>
            <h2>PragyanAI</h2>
            <p style="color:#c7d2fe;">
                PDF Audiobook Creator
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 📌 How it works")

    st.markdown(
        """
        **01** 📄 Upload PDF

        **02** 📝 Extract Text

        **03** 🌐 Detect Language

        **04** 🎙️ Generate Speech

        **05** 🎧 Download MP3
        """
    )

    st.markdown("---")

    st.markdown("### ✨ Features")

    st.markdown(
        """
        ✅ Automatic language detection  
        ✅ No translation  
        ✅ PDF text extraction  
        ✅ MP3 audiobook  
        ✅ Kannada support  
        ✅ English support  
        ✅ Simple download
        """
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-header">

        <h1>🎧 PragyanAI PDF Audiobook Creator</h1>

        <p>
            Convert your PDF documents into downloadable MP3 audiobooks
            using automatic language detection.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# WORKFLOW
# ============================================================

step1, step2, step3, step4 = st.columns(4)

with step1:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">STEP 01</div>
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
            <div class="step-number">STEP 02</div>
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
            <div class="step-number">STEP 03</div>
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
            <div class="step-number">STEP 04</div>
            <div class="step-icon">🎧</div>
            <div class="step-title">Create MP3</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📄 Upload Your PDF</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-subtitle">
        Upload a text-based PDF and convert it directly into an audiobook.
        No translation is performed.
    </div>
    """,
    unsafe_allow_html=True
)


uploaded_file = st.file_uploader(
    "Choose your PDF file",
    type=["pdf"],
    help="Upload a PDF document containing selectable text."
)


# ============================================================
# MAIN PROCESS
# ============================================================

if uploaded_file is not None:

    file_size = uploaded_file.size

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">📄 FILE NAME</div>
                <div class="info-value">
                    {uploaded_file.name}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        size_kb = file_size / 1024

        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">📦 FILE SIZE</div>
                <div class="info-value">
                    {size_kb:.1f} KB
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="info-card">
                <div class="info-label">📁 FILE TYPE</div>
                <div class="info-value">
                    PDF
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # EXTRACT TEXT
    # ========================================================

    st.markdown(
        '<div class="section-title">📝 Extract Text</div>',
        unsafe_allow_html=True
    )

    with st.spinner("Extracting text from PDF..."):

        try:

            reader = PdfReader(uploaded_file)

            extracted_text = ""

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

        except Exception as e:

            st.error(f"Unable to read PDF: {e}")
            st.stop()


    extracted_text = extracted_text.strip()


    if not extracted_text:

        st.error(
            "No selectable text was found in this PDF. "
            "Please upload a text-based PDF."
        )

        st.stop()


    # ========================================================
    # CLEAN TEXT
    # ========================================================

    cleaned_text = re.sub(
        r"\s+",
        " ",
        extracted_text
    ).strip()


    # ========================================================
    # TEXT PREVIEW
    # ========================================================

    with st.expander("👁️ Preview Extracted Text", expanded=False):

        st.write(cleaned_text[:5000])

        if len(cleaned_text) > 5000:
            st.caption(
                f"Showing first 5,000 characters "
                f"of {len(cleaned_text):,} characters."
            )


    # ========================================================
    # LANGUAGE DETECTION
    # ========================================================

    st.markdown(
        '<div class="section-title">🌐 Detect Language</div>',
        unsafe_allow_html=True
    )

    try:

        # Use a reasonable sample for detection.
        # Avoid detecting from very small text.
        detection_sample = cleaned_text[:5000]

        detected_code = detect(detection_sample)

        detected_name = LANGUAGE_NAMES.get(
            detected_code.lower(),
            detected_code.upper()
        )

    except LangDetectException:

        detected_code = None
        detected_name = "Not detected"

    except Exception:

        detected_code = None
        detected_name = "Not detected"


    if detected_code:

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"""
                <div class="info-card">
                    <div class="info-label">
                        🌐 DETECTED LANGUAGE
                    </div>

                    <div class="info-value">
                        {detected_name}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="info-card">
                    <div class="info-label">
                        🔤 LANGUAGE CODE
                    </div>

                    <div class="info-value">
                        {detected_code}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.warning(
            "Language could not be detected automatically."
        )


    # ========================================================
    # AUDIO GENERATION
    # ========================================================

    st.markdown(
        '<div class="section-title">🎙️ Create Audiobook</div>',
        unsafe_allow_html=True
    )

    if detected_code:

        st.info(
            f"Speech will be generated using the detected language: "
            f"**{detected_name} ({detected_code})**"
        )

        generate_button = st.button(
            "🎧 Generate MP3 Audiobook",
            use_container_width=True,
            type="primary"
        )

        if generate_button:

            progress = st.progress(0)

            status = st.empty()

            try:

                # ------------------------------------------------
                # Split text into manageable chunks
                # ------------------------------------------------

                max_chars = 4500

                chunks = []

                current_chunk = ""

                sentences = re.split(
                    r"(?<=[.!?।॥])\s+",
                    cleaned_text
                )

                for sentence in sentences:

                    sentence = sentence.strip()

                    if not sentence:
                        continue

                    if len(current_chunk) + len(sentence) + 1 <= max_chars:

                        if current_chunk:
                            current_chunk += " "

                        current_chunk += sentence

                    else:

                        if current_chunk:
                            chunks.append(current_chunk)

                        current_chunk = sentence

                if current_chunk:
                    chunks.append(current_chunk)


                # ------------------------------------------------
                # Generate MP3 chunks
                # ------------------------------------------------

                audio_parts = []

                total_chunks = len(chunks)

                for index, chunk in enumerate(chunks):

                    status.write(
                        f"🎙️ Generating audio "
                        f"part {index + 1} of {total_chunks}..."
                    )

                    audio_buffer = BytesIO()

                    tts = gTTS(
                        text=chunk,
                        lang=detected_code,
                        slow=False
                    )

                    tts.write_to_fp(audio_buffer)

                    audio_parts.append(
                        audio_buffer.getvalue()
                    )

                    progress_value = int(
                        ((index + 1) / total_chunks) * 100
                    )

                    progress.progress(progress_value)


                # ------------------------------------------------
                # Combine MP3 binary data
                # ------------------------------------------------

                final_audio = BytesIO()

                for part in audio_parts:
                    final_audio.write(part)

                final_audio.seek(0)


                # ------------------------------------------------
                # Store result
                # ------------------------------------------------

                st.session_state["audio_data"] = (
                    final_audio.getvalue()
                )

                st.session_state["audio_name"] = (
                    uploaded_file.name.rsplit(
                        ".",
                        1
                    )[0]
                    + "_audiobook.mp3"
                )

                status.success(
                    "🎉 Audiobook generated successfully!"
                )

                progress.progress(100)


            except Exception as e:

                progress.empty()
                status.empty()

                st.error(
                    f"Audio generation failed: {e}"
                )


    else:

        st.warning(
            "Audiobook generation requires a detected language."
        )


# ============================================================
# DOWNLOAD SECTION
# ============================================================

if "audio_data" in st.session_state:

    st.markdown(
        """
        <div class="success-box">

            <div class="success-title">
                🎉 Your Audiobook is Ready!
            </div>

            <div class="success-text">
                The PDF has been converted into an MP3 audiobook.
                You can listen to it online or download it.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🎧 Preview Audio")

    st.audio(
        st.session_state["audio_data"],
        format="audio/mp3"
    )

    st.download_button(
        label="⬇️ Download MP3 Audiobook",
        data=st.session_state["audio_data"],
        file_name=st.session_state["audio_name"],
        mime="audio/mpeg",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        🎧 <b>PragyanAI PDF Audiobook Creator</b>

        <br>

        PDF → Extract Text → Detect Language → Speech → MP3

        <br><br>

        Built with Python + Streamlit + PyPDF + gTTS

    </div>
    """,
    unsafe_allow_html=True
)
