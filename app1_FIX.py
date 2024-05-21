import streamlit as st
import tempfile
import os
import io
import time
import google.generativeai as genai
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()

# Configure Google API
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/phitt/OneDrive/Documents/GitHub/GeminiAPI_SummarizeMeeting/gemini-api-424003-6ac26a951d8e.json"


def split_audio(audio_file, max_duration_seconds=300):
    """Splits audio file object (not path) into chunks."""
    audio = AudioSegment.from_file(audio_file)  # Directly use file object
    if audio.duration_seconds <= max_duration_seconds:
        return [(audio, audio_file.name)]  # No splitting, return (audio, filename) tuple
    else:
        chunks = []
        for i, chunk in enumerate(audio[::max_duration_seconds * 1000]):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"-part{i}.mp4") as tmp_file:
                chunk.export(tmp_file.name, format="mp4")
                chunks.append((chunk, tmp_file.name))  # Store (audio, filename)
        return chunks


def summarize_audio(audio_chunk_tuple, max_retries=3, retry_delay=2):
    """Summarize audio, handling errors and retries."""
    audio_chunk, chunk_filename = audio_chunk_tuple
    retries = 0
    while retries < max_retries:
        try:
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

            # Create in-memory file-like object
            with io.BytesIO(audio_chunk.raw_data) as audio_stream:
                audio_file = genai.upload_stream(audio_stream, content_type="audio/mp4")

            response = model.generate_content(
                [
                    "Please summarize the following audio.",
                    audio_file
                ]
            )

            token = model.count_tokens(response.text)
            return response.text, token
        except Exception as e:
            if "not in an ACTIVE state" in str(e):
                retries += 1
                st.warning(f"File not ready yet, retrying ({retries}/{max_retries})...")
                time.sleep(retry_delay)
            else:
                st.error(f"Error summarizing audio chunk '{chunk_filename}': {e}")
                return f"Error summarizing this chunk ({chunk_filename})", 0  # Return error message and 0 tokens


def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary file and return the path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
        tmp_file.write(uploaded_file.read())  # Use read() instead of getvalue()
        return tmp_file.name


# Streamlit app interface
st.title('Audio Summarization App')

with st.expander("About this app"):
    st.write("""
        This app uses Google's generative AI to summarize audio files. 
        Upload your audio file in WAV or MP4 format and get a concise summary of its content.
    """)

audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp4'])

if audio_file is not None:
    audio_path = save_uploaded_file(audio_file)  # Save the uploaded file and get the path
    st.audio(audio_path)  

    if st.button('Summarize Audio'):
        with st.spinner('Summarizing...'):
            audio_chunks = split_audio(audio_path)
            summaries = []
            total_tokens = 0
            for audio_chunk_tuple in audio_chunks:
                summary, tokens = summarize_audio(audio_chunk_tuple)
                if summary:
                    summaries.append(summary)
                    total_tokens += tokens

            st.info(" ".join(summaries))  # Combine summaries
            st.write(f"Total Token count: {total_tokens}") 
