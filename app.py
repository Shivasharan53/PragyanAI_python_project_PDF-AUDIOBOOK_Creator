import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
from PyPDF2 import PdfReader
import tempfile
import os
import io


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PragyanAI - Speech & Audiobook Creator",
    page_icon="🎙️",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
}

.card {
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #ddd;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="title">🎙️ PragyanAI Speech & Audiobook Creator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Convert audio to text and PDF documents into audiobooks</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Options")

mode = st.sidebar.radio(
    "Select Operation",
    [
        "🎙️ Audio to Text",
        "📄 PDF to Audiobook"
    ]
)


# ============================================================
# AUDIO TO TEXT
# ============================================================

if mode == "🎙️ Audio to Text":

    st.header("🎙️ Audio to Text")

    st.info(
        "Upload an audio file. Microphone recording is not used because "
        "Streamlit Cloud does not provide a system microphone."
    )

    uploaded_audio = st.file_uploader(
        "Upload Audio File",
        type=[
            "wav",
            "mp3",
            "m4a",
            "flac",
            "ogg",
            "aiff"
        ]
    )

    language = st.selectbox(
        "Recognition Language",
        [
            ("English (US)", "en-US"),
            ("English (UK)", "en-GB"),
            ("Hindi", "hi-IN"),
            ("Kannada", "kn-IN"),
            ("Tamil", "ta-IN"),
            ("Telugu", "te-IN"),
            ("Spanish", "es-ES"),
            ("French", "fr-FR"),
            ("German", "de-DE")
        ],
        format_func=lambda x: x[0]
    )

    if uploaded_audio:

        st.audio(
            uploaded_audio,
            format=f"audio/{uploaded_audio.name.split('.')[-1]}"
        )

        if st.button(
            "📝 Convert Audio to Text",
            use_container_width=True
        ):

            try:

                with st.spinner("Processing audio..."):

                    # Save uploaded file temporarily
                    input_suffix = os.path.splitext(
                        uploaded_audio.name
                    )[1]

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=input_suffix
                    ) as temp_input:

                        temp_input.write(
                            uploaded_audio.read()
                        )

                        input_path = temp_input.name


                    # Convert to WAV
                    wav_path = input_path + ".wav"

                    audio = AudioSegment.from_file(
                        input_path
                    )

                    audio.export(
                        wav_path,
                        format="wav"
                    )


                    # Speech Recognition
                    recognizer = sr.Recognizer()

                    with sr.AudioFile(wav_path) as source:

                        audio_data = recognizer.record(
                            source
                        )


                    try:

                        text = recognizer.recognize_google(
                            audio_data,
                            language=language[1]
                        )

                    except sr.UnknownValueError:

                        text = (
                            "Sorry, the audio could not be "
                            "understood."
                        )

                    except sr.RequestError as e:

                        text = (
                            f"Google Speech Recognition error: {e}"
                        )


                st.success("Audio transcription completed!")

                st.subheader("📝 Transcription")

                st.text_area(
                    "Recognized Text",
                    text,
                    height=300
                )


                # Download text
                st.download_button(
                    label="⬇️ Download Transcript",
                    data=text,
                    file_name="transcript.txt",
                    mime="text/plain",
                    use_container_width=True
                )


                # Cleanup
                try:
                    os.remove(input_path)
                    os.remove(wav_path)
                except:
                    pass


            except Exception as e:

                st.error(
                    f"Error processing audio: {e}"
                )


# ============================================================
# PDF TO AUDIOBOOK
# ============================================================

elif mode == "📄 PDF to Audiobook":

    st.header("📄 PDF to Audiobook")

    st.write(
        "Upload a PDF document and convert its text into an MP3 audiobook."
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    language = st.selectbox(
        "Audio Language",
        [
            ("English", "en"),
            ("Hindi", "hi"),
            ("Kannada", "kn"),
            ("Tamil", "ta"),
            ("Telugu", "te"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de")
        ],
        format_func=lambda x: x[0]
    )

    if uploaded_pdf:

        st.success(
            f"Uploaded: {uploaded_pdf.name}"
        )

        if st.button(
            "📖 Extract PDF Text",
            use_container_width=True
        ):

            try:

                reader = PdfReader(
                    uploaded_pdf
                )

                pages = []

                for page in reader.pages:

                    text = page.extract_text()

                    if text:
                        pages.append(text)


                full_text = "\n\n".join(
                    pages
                )


                if not full_text.strip():

                    st.error(
                        "No readable text was found in this PDF."
                    )

                else:

                    st.success(
                        "PDF text extracted successfully!"
                    )

                    st.session_state["pdf_text"] = full_text


            except Exception as e:

                st.error(
                    f"PDF extraction error: {e}"
                )


    # --------------------------------------------------------
    # DISPLAY EXTRACTED TEXT
    # --------------------------------------------------------

    if "pdf_text" in st.session_state:

        text = st.session_state["pdf_text"]

        st.subheader("📖 Extracted Text")

        st.text_area(
            "PDF Content",
            text,
            height=400
        )

        st.write(
            f"Characters: {len(text):,}"
        )


        # ----------------------------------------------------
        # CREATE AUDIOBOOK
        # ----------------------------------------------------

        if st.button(
            "🎧 Create Audiobook",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Generating audiobook..."
                ):

                    # gTTS has practical text-size limitations,
                    # so split large documents into chunks.
                    chunk_size = 4000

                    chunks = [
                        text[i:i + chunk_size]
                        for i in range(
                            0,
                            len(text),
                            chunk_size
                        )
                    ]


                    audio_parts = []

                    for index, chunk in enumerate(chunks):

                        st.write(
                            f"Generating audio part "
                            f"{index + 1} of {len(chunks)}..."
                        )

                        tts = gTTS(
                            text=chunk,
                            lang=language[1],
                            slow=False
                        )

                        temp_mp3 = tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".mp3"
                        )

                        temp_mp3.close()

                        tts.save(
                            temp_mp3.name
                        )

                        audio_parts.append(
                            temp_mp3.name
                        )


                    # Combine MP3 files
                    combined = AudioSegment.empty()

                    for audio_file in audio_parts:

                        segment = AudioSegment.from_mp3(
                            audio_file
                        )

                        combined += segment


                    output_file = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".mp3"
                    )

                    output_file.close()


                    combined.export(
                        output_file.name,
                        format="mp3"
                    )


                    with open(
                        output_file.name,
                        "rb"
                    ) as f:

                        audiobook_data = f.read()


                st.success(
                    "🎉 Audiobook created successfully!"
                )

                st.audio(
                    audiobook_data,
                    format="audio/mp3"
                )


                st.download_button(
                    label="⬇️ Download Audiobook",
                    data=audiobook_data,
                    file_name="pragyanai_audiobook.mp3",
                    mime="audio/mpeg",
                    use_container_width=True
                )


                # Cleanup
                for audio_file in audio_parts:

                    try:
                        os.remove(audio_file)
                    except:
                        pass


                try:
                    os.remove(output_file.name)
                except:
                    pass


            except Exception as e:

                st.error(
                    f"Audiobook generation error: {e}"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;">
        <b>PragyanAI</b> | Speech & Audiobook Creator<br>
        Built with Python + Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
