import streamlit as st
import tempfile
import os
import google.generativeai as genai
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

from dotenv import load_dotenv

load_dotenv()

# Configure Google API for audio summarization
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/phitt/OneDrive/Documents/GitHub/GeminiAPI_SummarizeMeeting/gemini-api-424003-6ac26a951d8e.json"

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary file and return the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None

def transcribe_audio(audio_file_path):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(audio_file_path)
    with audio_file as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data)

def segment_audio(audio_file_path, start_keyword, end_keyword):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(audio_file_path)
    audio_file = sr.AudioFile(audio_file_path)
    
    with audio_file as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    
    # Finding start and end keywords
    start_index = text.find(start_keyword)
    end_index = text.find(end_keyword, start_index) if end_keyword else len(text)

    if start_index == -1:
        st.error(f"Start keyword '{start_keyword}' not found in the audio.")
        return None

    if end_index == -1:
        st.error(f"End keyword '{end_keyword}' not found in the audio.")
        return None

    # Convert text indices to time (assuming average speaking rate)
    words = text.split()
    start_time = len(" ".join(words[:start_index]).split()) / 150 * 60 * 1000  # milliseconds
    end_time = len(" ".join(words[:end_index]).split()) / 150 * 60 * 1000  # milliseconds

    return audio[start_time:end_time]

def summarize_audio(audio_file_path):
    """Summarize the audio using Google's Generative API."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content(
        [
            "- Please summarize the following audio in bullet points:",
            audio_file
        ]
    )
    token = model.count_tokens(response.text)
    formatted_text = response.text.replace("\n", "<br>")
    return formatted_text, token

# Streamlit app interface
st.title('Audio Summarization App')

with st.expander("About this app"):
    st.write("""
        This app uses Google's generative AI to summarize audio files. 
        Upload your audio file in WAV or MP3 format and get a concise summary of its content.
    """)

audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])
start_keyword = st.text_input("Start Keyword/Phrase")
end_keyword = st.text_input("End Keyword/Phrase (optional)")

if st.button('Summarize Audio'):
    if not start_keyword:
        st.error("Please provide a start keyword/phrase.")
    else:
        audio_path = save_uploaded_file(audio_file)
        with st.spinner('Transcribing and segmenting audio...'):
            segment = segment_audio(audio_path, start_keyword, end_keyword)
            if segment:
                segment_path = tempfile.mktemp(suffix=".wav")
                segment.export(segment_path, format="wav")
                with st.spinner('Summarizing...'):
                    summary_text, token_count = summarize_audio(segment_path)
                    st.markdown(summary_text, unsafe_allow_html=True)
                    st.info(f"Token count: {token_count}")
