import streamlit as st
import speech_recognition as sr
import tempfile
import os
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Speech to Text",
    page_icon="🎙️",
    layout="centered"
)

# =========================================================
# TITLE
# =========================================================

st.title("🎙️ Speech-to-Text Transcription Tool")

st.write(
    "Record your voice or upload an audio file "
    "and convert speech into text."
)

# =========================================================
# LANGUAGE
# =========================================================

languages = {
    "English (US)": "en-US",
    "English (UK)": "en-GB",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Italian": "it-IT",
    "Portuguese (Brazil)": "pt-BR",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Chinese (Mandarin)": "zh-CN"
}

language_name = st.selectbox(
    "🌐 Select Language",
    list(languages.keys())
)

language = languages[language_name]

# =========================================================
# FUNCTIONS
# =========================================================

def transcribe_audio(audio_bytes, language):

    recognizer = sr.Recognizer()

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_file:

            temp_file.write(audio_bytes)

            temp_path = temp_file.name

        with sr.AudioFile(temp_path) as source:

            audio = recognizer.record(source)

        # Google Speech Recognition

        try:

            text = recognizer.recognize_google(
                audio,
                language=language
            )

            return text, "Google Speech Recognition"

        except sr.UnknownValueError:

            return (
                "Could not understand the speech.",
                "Google Speech Recognition"
            )

        except sr.RequestError as e:

            return (
                f"Google Speech Recognition error: {e}",
                "Google Speech Recognition"
            )

    except Exception as e:

        return (
            f"Error processing audio: {e}",
            "System"
        )

    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


def save_transcript(text):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return (
        f"transcript_{timestamp}.txt"
    )


# =========================================================
# RECORD FROM BROWSER MICROPHONE
# =========================================================

st.subheader("🎤 Record Your Voice")

audio = st.audio_input(
    "Click here to record your voice"
)

if audio is not None:

    st.success("✅ Audio recorded successfully!")

    st.audio(
        audio,
        format="audio/wav"
    )

    if st.button(
        "🔄 Convert Speech to Text",
        use_container_width=True
    ):

        with st.spinner(
            "Converting speech to text..."
        ):

            text, engine = transcribe_audio(
                audio.getvalue(),
                language
            )

        st.subheader("📝 Transcription")

        if text.startswith("Could not"):

            st.warning(text)

        elif text.startswith("Google Speech"):

            st.error(text)

        elif text.startswith("Error"):

            st.error(text)

        else:

            st.success(
                f"✅ Transcription completed using {engine}"
            )

            st.text_area(
                "Recognized Text",
                text,
                height=200
            )

            filename = save_transcript(text)

            st.download_button(
                "⬇️ Download Transcript",
                data=text,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )


# =========================================================
# UPLOAD AUDIO FILE
# =========================================================

st.divider()

st.subheader("📁 Upload Audio File")

uploaded_file = st.file_uploader(
    "Upload a WAV audio file",
    type=["wav", "flac", "aiff"]
)

if uploaded_file is not None:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    st.audio(
        uploaded_file
    )

    if st.button(
        "📝 Transcribe Uploaded File",
        use_container_width=True
    ):

        with st.spinner(
            "Transcribing audio..."
        ):

            text, engine = transcribe_audio(
                uploaded_file.getvalue(),
                language
            )

        st.subheader("📝 Transcription")

        if text.startswith("Could not"):

            st.warning(text)

        elif text.startswith("Error"):

            st.error(text)

        else:

            st.success(
                f"✅ Transcription completed using {engine}"
            )

            st.text_area(
                "Recognized Text",
                text,
                height=200
            )

            filename = save_transcript(text)

            st.download_button(
                "⬇️ Download Transcript",
                data=text,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )


# =========================================================
# INFORMATION
# =========================================================

st.divider()

st.info(
    """
    **How to use**

    1. Select your language.
    2. Click the microphone button.
    3. Record your speech.
    4. Click Convert Speech to Text.
    5. View the transcription.
    6. Download the transcript as a TXT file.

    You can also upload a WAV, FLAC, or AIFF file.
    """
)
