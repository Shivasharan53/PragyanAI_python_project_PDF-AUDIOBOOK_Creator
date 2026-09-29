import streamlit as st
from pypdf import PdfReader
from gtts import gTTS
from langdetect import detect, LangDetectException
import tempfile
import os
import re
import time


# ============================================================
# PAGE CONFIGURATION
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

    .success-box {
        padding: 18px;
        border-radius: 12px;
        margin-top: 20px;
        border: 1px solid #10b981;
        background-color: #ecfdf5;
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
    '<div class="subtitle">'
    'Convert PDF documents into MP3 audiobooks automatically'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# LANGUAGE MAP
# ============================================================

LANGUAGE_MAP = {

    "kn": {
        "name": "Kannada",
        "tts": "kn"
    },

    "en": {
        "name": "English",
        "tts": "en"
    },

    "hi": {
        "name": "Hindi",
        "tts": "hi"
    },

    "ta": {
        "name": "Tamil",
        "tts": "ta"
    },

    "te": {
        "name": "Telugu",
        "tts": "te"
    },

    "ml": {
        "name": "Malayalam",
        "tts": "ml"
    },

    "mr": {
        "name": "Marathi",
        "tts": "mr"
    },

    "bn": {
        "name": "Bengali",
        "tts": "bn"
    },

    "gu": {
        "name": "Gujarati",
        "tts": "gu"
    },

    "pa": {
        "name": "Punjabi",
        "tts": "pa"
    },

    "fr": {
        "name": "French",
        "tts": "fr"
    },

    "de": {
        "name": "German",
        "tts": "de"
    },

    "es": {
        "name": "Spanish",
        "tts": "es"
    },

    "it": {
        "name": "Italian",
        "tts": "it"
    },

    "pt": {
        "name": "Portuguese",
        "tts": "pt"
    },

    "ja": {
        "name": "Japanese",
        "tts": "ja"
    },

    "ko": {
        "name": "Korean",
        "tts": "ko"
    },

    "zh-cn": {
        "name": "Chinese",
        "tts": "zh-CN"
    }
}


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text):

    """
    Detect the language of extracted PDF text.

    Returns:
        language name
        language code
        TTS language code
    """

    if not text or len(text.strip()) < 20:

        return (
            "Unknown",
            "unknown",
            "en"
        )

    try:

        detected_code = detect(text)

        if detected_code in LANGUAGE_MAP:

            language_info = LANGUAGE_MAP[
                detected_code
            ]

            return (
                language_info["name"],
                detected_code,
                language_info["tts"]
            )

        return (
            detected_code.upper(),
            detected_code,
            detected_code
        )

    except LangDetectException:

        return (
            "Unknown",
            "unknown",
            "en"
        )


# ============================================================
# EXTRACT TEXT FROM PDF
# ============================================================

def extract_pdf_text(pdf_file):

    reader = PdfReader(pdf_file)

    all_text = []

    for page_number, page in enumerate(reader.pages):

        try:

            text = page.extract_text()

            if text:

                all_text.append(text)

        except Exception:

            continue

    return "\n\n".join(all_text)


# ============================================================
# CLEAN PDF TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    # Remove control characters
    text = re.sub(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F]",
        "",
        text
    )

    # Remove excessive spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# SPLIT TEXT INTO AUDIO CHUNKS
# ============================================================

def split_text(text, max_chars=3500):

    paragraphs = text.split("\n\n")

    chunks = []

    current_chunk = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:

            continue

        # Normal paragraph
        if len(current_chunk) + len(paragraph) + 2 <= max_chars:

            if current_chunk:

                current_chunk += "\n\n" + paragraph

            else:

                current_chunk = paragraph

        else:

            if current_chunk:

                chunks.append(
                    current_chunk
                )

            # Paragraph is too large
            if len(paragraph) > max_chars:

                sentences = re.split(
                    r"(?<=[.!?।])\s+",
                    paragraph
                )

                temporary = ""

                for sentence in sentences:

                    sentence = sentence.strip()

                    if not sentence:

                        continue

                    if (
                        len(temporary)
                        + len(sentence)
                        + 1
                        <= max_chars
                    ):

                        if temporary:

                            temporary += " " + sentence

                        else:

                            temporary = sentence

                    else:

                        if temporary:

                            chunks.append(
                                temporary
                            )

                        temporary = sentence

                current_chunk = temporary

            else:

                current_chunk = paragraph

    if current_chunk:

        chunks.append(
            current_chunk
        )

    return chunks


# ============================================================
# GENERATE AUDIO
# ============================================================

def generate_audiobook(
    text,
    language_code
):

    chunks = split_text(
        text,
        max_chars=3500
    )

    if not chunks:

        raise ValueError(
            "No readable text found."
        )

    temp_dir = tempfile.mkdtemp()

    audio_files = []

    progress = st.progress(0)

    status = st.empty()

    total = len(chunks)

    for index, chunk in enumerate(chunks):

        part_number = index + 1

        status.info(
            f"🎙️ Generating audio "
            f"part {part_number} of {total}..."
        )

        output_file = os.path.join(
            temp_dir,
            f"part_{part_number}.mp3"
        )

        try:

            tts = gTTS(
                text=chunk,
                lang=language_code,
                slow=False
            )

            tts.save(
                output_file
            )

            audio_files.append(
                output_file
            )

        except Exception as error:

            raise RuntimeError(
                f"Could not generate audio "
                f"part {part_number}: {error}"
            )

        progress.progress(
            part_number / total
        )

        time.sleep(0.3)

    # ========================================================
    # COMBINE MP3 FILES
    # ========================================================

    status.info(
        "🔄 Combining audio parts..."
    )

    final_file = os.path.join(
        temp_dir,
        "PragyanAI_Audiobook.mp3"
    )

    with open(
        final_file,
        "wb"
    ) as final_audio:

        for audio_file in audio_files:

            with open(
                audio_file,
                "rb"
            ) as part:

                final_audio.write(
                    part.read()
                )

    status.success(
        "✅ Audiobook generated successfully!"
    )

    progress.progress(1.0)

    return final_file


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Options")

    st.markdown(
        """
        ### 🎧 PDF → Audiobook

        Upload a PDF and the application will:

        **PDF**
        ↓
        
        **Extract Text**
        ↓
        
        **Detect Language**
        ↓
        
        **Convert to Speech**
        ↓
        
        **MP3 Audiobook**
        """
    )

    st.divider()

    st.info(
        "The PDF language is detected automatically "
        "from its extracted text."
    )


# ============================================================
# UPLOAD PDF
# ============================================================

st.subheader("📄 Upload PDF")

uploaded_file = st.file_uploader(
    "Choose a PDF document",
    type=["pdf"]
)


# ============================================================
# RESET OLD RESULTS WHEN NEW PDF IS UPLOADED
# ============================================================

if uploaded_file is not None:

    current_file_name = uploaded_file.name

    if (
        "last_file_name"
        not in st.session_state
        or
        st.session_state[
            "last_file_name"
        ] != current_file_name
    ):

        st.session_state[
            "last_file_name"
        ] = current_file_name

        st.session_state.pop(
            "pdf_text",
            None
        )

        st.session_state.pop(
            "detected_language",
            None
        )

        st.session_state.pop(
            "audio_file",
            None
        )


# ============================================================
# PROCESS PDF
# ============================================================

if uploaded_file is not None:

    st.success(
        f"📄 Uploaded: **{uploaded_file.name}**"
    )

    file_size = (
        uploaded_file.size / 1024
    )

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

        if (
            "detected_language"
            in st.session_state
        ):

            st.metric(
                "🎙️ Detected Language",
                st.session_state[
                    "detected_language"
                ][0]
            )

        else:

            st.metric(
                "🎙️ Detected Language",
                "Not detected"
            )

    st.divider()

    # ========================================================
    # EXTRACT TEXT
    # ========================================================

    if st.button(
        "📖 Extract Text & Detect Language",
        use_container_width=True
    ):

        with st.spinner(
            "📖 Reading PDF and detecting language..."
        ):

            try:

                extracted_text = extract_pdf_text(
                    uploaded_file
                )

                extracted_text = clean_text(
                    extracted_text
                )

                if not extracted_text:

                    st.error(
                        "❌ No readable text found "
                        "in this PDF."
                    )

                    st.warning(
                        "This appears to be a scanned "
                        "or image-only PDF. OCR is "
                        "required for scanned PDFs."
                    )

                    st.stop()

                # Store text
                st.session_state[
                    "pdf_text"
                ] = extracted_text

                # Detect language
                (
                    language_name,
                    language_code,
                    tts_code
                ) = detect_language(
                    extracted_text
                )

                st.session_state[
                    "detected_language"
                ] = (
                    language_name,
                    language_code,
                    tts_code
                )

                st.success(
                    "✅ Text extracted successfully!"
                )

            except Exception as error:

                st.error(
                    f"❌ Error processing PDF: {error}"
                )


# ============================================================
# SHOW EXTRACTED TEXT
# ============================================================

if "pdf_text" in st.session_state:

    text = st.session_state[
        "pdf_text"
    ]

    st.subheader(
        "📖 Extracted Text"
    )

    # ========================================================
    # LANGUAGE RESULT
    # ========================================================

    if (
        "detected_language"
        in st.session_state
    ):

        (
            language_name,
            language_code,
            tts_code
        ) = st.session_state[
            "detected_language"
        ]

        st.success(
            f"🌐 **Detected Language: "
            f"{language_name}**  \n"
            f"Language code: `{language_code}`  \n"
            f"TTS code: `{tts_code}`"
        )

    # ========================================================
    # TEXT STATISTICS
    # ========================================================

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

    # ========================================================
    # TEXT PREVIEW
    # ========================================================

    with st.expander(
        "👀 Preview Extracted Text",
        expanded=True
    ):

        st.text_area(
            "PDF Content",
            text[:15000],
            height=350
        )

        if len(text) > 15000:

            st.info(
                f"Showing first 15,000 characters "
                f"of {len(text):,} characters."
            )

    st.divider()

    # ========================================================
    # AUDIOBOOK
    # ========================================================

    st.subheader(
        "🎧 Create Audiobook"
    )

    if (
        "detected_language"
        in st.session_state
    ):

        (
            language_name,
            language_code,
            tts_code
        ) = st.session_state[
            "detected_language"
        ]

        st.write(
            f"🎙️ Voice language: **{language_name}**"
        )

        if st.button(
            "🎙️ Generate Audiobook",
            type="primary",
            use_container_width=True
        ):

            try:

                final_audio = generate_audiobook(
                    text,
                    tts_code
                )

                st.session_state[
                    "audio_file"
                ] = final_audio

            except Exception as error:

                st.error(
                    f"❌ Audiobook generation error: "
                    f"{error}"
                )

    else:

        st.warning(
            "Please extract the PDF text first."
        )


# ============================================================
# AUDIO PLAYER + DOWNLOAD
# ============================================================

if (
    "audio_file"
    in st.session_state
):

    audio_file = st.session_state[
        "audio_file"
    ]

    if os.path.exists(audio_file):

        st.divider()

        st.subheader(
            "🎧 Your Audiobook"
        )

        st.success(
            "✅ Your PDF has been converted "
            "into an audiobook!"
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

        st.download_button(
            label="⬇️ Download MP3 Audiobook",
            data=audio_bytes,
            file_name=(
                "PragyanAI_Audiobook.mp3"
            ),
            mime="audio/mpeg",
            use_container_width=True
        )

        st.markdown(
            """
            <div class="success-box">
                <b>🎉 Audiobook Ready!</b><br>
                Listen to the audiobook above or
                download the MP3 file.
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
    "PDF → Text → Language Detection → Speech → MP3"
)
