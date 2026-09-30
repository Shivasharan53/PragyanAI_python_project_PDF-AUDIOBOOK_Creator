import streamlit as st
import fitz  # PyMuPDF
from gtts import gTTS
from langdetect import detect, LangDetectException
from pydub import AudioSegment
import tempfile
import os


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PragyanAI PDF to Audiobook",
    page_icon="🎧",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🎧 PragyanAI PDF to Audiobook Creator")

st.write(
    "PDF → Extract Text → Detect Language → Convert to Speech → MP3 Audiobook"
)

st.divider()


# ============================================================
# EXTRACT TEXT FROM PDF
# ============================================================

def extract_text_from_pdf(uploaded_file):

    pdf_bytes = uploaded_file.read()

    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = ""

    for page in pdf:
        page_text = page.get_text("text")

        if page_text:
            text += page_text + "\n"

    pdf.close()

    return text.strip()


# ============================================================
# DETECT LANGUAGE
# ============================================================

def detect_pdf_language(text):

    if not text or len(text.strip()) < 20:
        return None

    try:
        # Use enough text for more reliable detection
        sample = text[:10000]

        detected_language = detect(sample)

        return detected_language

    except LangDetectException:
        return None

    except Exception:
        return None


# ============================================================
# SPLIT TEXT
# ============================================================

def split_text(text, max_chars=4000):

    words = text.split()

    chunks = []
    current_chunk = ""

    for word in words:

        if len(current_chunk) + len(word) + 1 <= max_chars:

            current_chunk += word + " "

        else:

            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            current_chunk = word + " "

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# ============================================================
# CREATE MP3 AUDIOBOOK
# ============================================================

def create_audiobook(text, language_code):

    chunks = split_text(
        text,
        max_chars=4000
    )

    audio_files = []

    progress = st.progress(0)

    status = st.empty()

    total = len(chunks)

    for index, chunk in enumerate(chunks):

        status.info(
            f"🎙️ Generating audio part {index + 1} of {total}..."
        )

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        temp_file.close()

        try:

            tts = gTTS(
                text=chunk,
                lang=language_code,
                slow=False
            )

            tts.save(temp_file.name)

            audio_files.append(temp_file.name)

        except Exception as e:

            status.error(
                f"❌ Audio generation failed: {e}"
            )

            # Delete files already created
            for file in audio_files:

                try:
                    os.remove(file)
                except:
                    pass

            return None

        progress.progress(
            (index + 1) / total
        )

    status.success(
        "✅ Speech generation completed!"
    )

    # --------------------------------------------------------
    # MERGE AUDIO FILES
    # --------------------------------------------------------

    combined_audio = AudioSegment.empty()

    for file in audio_files:

        audio = AudioSegment.from_mp3(file)

        combined_audio += audio

    # --------------------------------------------------------
    # SAVE FINAL MP3
    # --------------------------------------------------------

    final_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    final_file.close()

    combined_audio.export(
        final_file.name,
        format="mp3"
    )

    # --------------------------------------------------------
    # REMOVE TEMPORARY PARTS
    # --------------------------------------------------------

    for file in audio_files:

        try:
            os.remove(file)
        except:
            pass

    return final_file.name


# ============================================================
# UPLOAD PDF
# ============================================================

uploaded_file = st.file_uploader(
    "📄 Upload PDF",
    type=["pdf"]
)


# ============================================================
# MAIN PROCESS
# ============================================================

if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    st.write(
        f"📦 File size: {uploaded_file.size / 1024:.2f} KB"
    )

    st.divider()

    # ========================================================
    # STEP 1 - EXTRACT TEXT
    # ========================================================

    st.subheader("1️⃣ Extract Text")

    with st.spinner("📖 Extracting text from PDF..."):

        extracted_text = extract_text_from_pdf(
            uploaded_file
        )

    if not extracted_text:

        st.error(
            "❌ No text could be extracted from this PDF."
        )

        st.info(
            "The PDF may contain scanned images instead of selectable text."
        )

        st.stop()

    st.success(
        f"✅ Text extracted successfully — "
        f"{len(extracted_text):,} characters"
    )

    # ========================================================
    # TEXT PREVIEW
    # ========================================================

    with st.expander("📖 View Extracted Text"):

        st.text_area(
            "Extracted Text",
            extracted_text,
            height=300
        )

    st.divider()

    # ========================================================
    # STEP 2 - DETECT LANGUAGE
    # ========================================================

    st.subheader("2️⃣ Detect Language")

    with st.spinner("🔍 Detecting language from PDF text..."):

        detected_language = detect_pdf_language(
            extracted_text
        )

    if not detected_language:

        st.error(
            "❌ Language could not be detected."
        )

        st.info(
            "Please make sure the PDF contains enough readable text."
        )

        st.stop()

    st.success(
        f"🌐 Detected language code: **{detected_language}**"
    )

    st.divider()

    # ========================================================
    # STEP 3 - CONVERT TO SPEECH
    # ========================================================

    st.subheader("3️⃣ Convert Text to Speech")

    st.write(
        "The detected language will automatically be used for speech generation."
    )

    # ========================================================
    # STEP 4 - GENERATE AUDIOBOOK
    # ========================================================

    st.subheader("4️⃣ Generate MP3 Audiobook")

    if st.button(
        "🎧 Convert PDF to MP3 Audiobook",
        type="primary",
        use_container_width=True
    ):

        audiobook_file = create_audiobook(
            extracted_text,
            detected_language
        )

        if audiobook_file:

            st.success(
                "🎉 Audiobook created successfully!"
            )

            # =================================================
            # AUDIO PLAYER
            # =================================================

            st.audio(
                audiobook_file,
                format="audio/mp3"
            )

            # =================================================
            # DOWNLOAD
            # =================================================

            with open(
                audiobook_file,
                "rb"
            ) as audio:

                audio_data = audio.read()

            st.download_button(
                label="⬇️ Download MP3 Audiobook",
                data=audio_data,
                file_name="PragyanAI_Audiobook.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )
