import streamlit as st
import fitz
from gtts import gTTS
from langdetect import detect, LangDetectException
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

        # Use a reasonable amount of extracted text
        sample = text[:15000]

        language = detect(sample)

        return language

    except LangDetectException:

        return None

    except Exception:

        return None


# ============================================================
# SPLIT TEXT INTO CHUNKS
# ============================================================

def split_text(text, max_chars=4500):

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
# GENERATE MP3
# ============================================================

def generate_audiobook(text, language):

    chunks = split_text(
        text,
        max_chars=4500
    )

    if not chunks:

        return None

    progress = st.progress(0)

    status = st.empty()

    audio_parts = []

    total_parts = len(chunks)

    # --------------------------------------------------------
    # GENERATE EACH AUDIO PART
    # --------------------------------------------------------

    for index, chunk in enumerate(chunks):

        status.info(
            f"🎙️ Generating audio part "
            f"{index + 1} of {total_parts}..."
        )

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        temp_file.close()

        try:

            tts = gTTS(
                text=chunk,
                lang=language,
                slow=False
            )

            tts.save(temp_file.name)

            audio_parts.append(temp_file.name)

        except Exception as e:

            status.error(
                f"❌ Error generating audio: {e}"
            )

            # Remove temporary files
            for file in audio_parts:

                try:
                    os.remove(file)
                except:
                    pass

            return None

        progress.progress(
            (index + 1) / total_parts
        )

    status.success(
        "✅ Speech generation completed!"
    )

    # --------------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------------
    # Instead of pydub, combine MP3 files using ffmpeg.
    #
    # Streamlit Cloud has ffmpeg available in many environments,
    # but we also handle failure gracefully.
    # --------------------------------------------------------

    final_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    final_file.close()

    # If there is only one part, simply use it
    if len(audio_parts) == 1:

        with open(
            audio_parts[0],
            "rb"
        ) as source:

            data = source.read()

        with open(
            final_file.name,
            "wb"
        ) as destination:

            destination.write(data)

        os.remove(audio_parts[0])

        return final_file.name

    # --------------------------------------------------------
    # MULTIPLE PARTS
    # --------------------------------------------------------

    concat_file = tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".txt",
        encoding="utf-8"
    )

    for audio_file in audio_parts:

        absolute_path = os.path.abspath(
            audio_file
        )

        concat_file.write(
            f"file '{absolute_path}'\n"
        )

    concat_file.close()

    # --------------------------------------------------------
    # USE FFMPEG WITHOUT PYDUB
    # --------------------------------------------------------

    import subprocess

    try:

        command = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file.name,
            "-c",
            "copy",
            final_file.name
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:

            st.error(
                "❌ FFmpeg could not combine the audio files."
            )

            st.code(
                result.stderr
            )

            return None

    except FileNotFoundError:

        st.error(
            "❌ FFmpeg is not available on this Streamlit environment."
        )

        return None

    finally:

        try:
            os.remove(concat_file.name)
        except:
            pass

        for audio_file in audio_parts:

            try:
                os.remove(audio_file)
            except:
                pass

    return final_file.name


# ============================================================
# UPLOAD PDF
# ============================================================

st.subheader("📄 Upload PDF")

uploaded_file = st.file_uploader(
    "Choose a PDF document",
    type=["pdf"]
)


# ============================================================
# PROCESS PDF
# ============================================================

if uploaded_file:

    st.success(
        f"Uploaded: **{uploaded_file.name}**"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "📦 File Size",
            f"{uploaded_file.size / 1024:.2f} KB"
        )

    with col2:

        st.metric(
            "📄 File Type",
            "PDF"
        )

    st.divider()

    # ========================================================
    # STEP 1
    # ========================================================

    st.subheader("1️⃣ Extract Text")

    with st.spinner(
        "📖 Extracting text from PDF..."
    ):

        extracted_text = extract_text_from_pdf(
            uploaded_file
        )

    if not extracted_text:

        st.error(
            "❌ No text could be extracted from this PDF."
        )

        st.warning(
            "This PDF may contain scanned images instead of selectable text."
        )

        st.stop()

    st.success(
        f"✅ Text extracted successfully — "
        f"{len(extracted_text):,} characters"
    )

    # --------------------------------------------------------
    # TEXT PREVIEW
    # --------------------------------------------------------

    with st.expander(
        "📖 View Extracted Text"
    ):

        st.text_area(
            "Extracted Text",
            extracted_text,
            height=300
        )

    st.divider()

    # ========================================================
    # STEP 2
    # ========================================================

    st.subheader("2️⃣ Detect Language")

    with st.spinner(
        "🔍 Detecting language..."
    ):

        detected_language = detect_pdf_language(
            extracted_text
        )

    if not detected_language:

        st.error(
            "❌ Language could not be detected."
        )

        st.stop()

    st.success(
        f"🌐 Detected language code: **{detected_language}**"
    )

    st.divider()

    # ========================================================
    # STEP 3
    # ========================================================

    st.subheader("3️⃣ Convert to Speech")

    st.info(
        "The detected language will automatically be used for speech generation."
    )

    # ========================================================
    # STEP 4
    # ========================================================

    st.subheader("4️⃣ MP3 Audiobook")

    if st.button(
        "🎧 Generate MP3 Audiobook",
        type="primary",
        use_container_width=True
    ):

        audiobook_file = generate_audiobook(
            extracted_text,
            detected_language
        )

        if audiobook_file:

            st.success(
                "🎉 MP3 Audiobook created successfully!"
            )

            # ------------------------------------------------
            # AUDIO PLAYER
            # ------------------------------------------------

            st.audio(
                audiobook_file,
                format="audio/mp3"
            )

            # ------------------------------------------------
            # DOWNLOAD
            # ------------------------------------------------

            with open(
                audiobook_file,
                "rb"
            ) as audio_file:

                audio_data = audio_file.read()

            st.download_button(
                label="⬇️ Download MP3 Audiobook",
                data=audio_data,
                file_name="PragyanAI_Audiobook.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )

            # Do not delete immediately because
            # Streamlit needs the file for playback/download.
