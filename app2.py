import streamlit as st
#from pydub import AudioSegment
import tempfile
import os
import google.generativeai as genai
from moviepy.editor import VideoFileClip
from dotenv import load_dotenv

load_dotenv()

# Configure Google API for audio summarization
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/phitt/OneDrive/Documents/GitHub/GeminiAPI_SummarizeMeeting/gemini-api-424003-6ac26a951d8e.json"

def summarize_video(video_path):
    """Extract audio from video, summarize it, and return text and token count."""

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(temp_audio.name)
        summary, tokens = summarize_audio(temp_audio.name) 

    return summary, tokens

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary file and return the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None


# Streamlit app interface
st.title('Audio Summarization App')

with st.expander("About this app"):
    st.write("""
        This app uses Google's generative AI to summarize audio files. 
        Upload your audio file in WAV or MP3 format and get a concise summary of its content.
    """)

video_file = st.file_uploader("Upload Video File", type=['mp4'])

if video_file is not None:
    # Use a context manager to automatically handle file deletion
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(video_file.read())
        st.video(temp_video.name)  # Display the uploaded video

        if st.button('Summarize Video'):
            with st.spinner('Summarizing...'):
                summary_text, token_count = summarize_video(temp_video.name)
                st.info(summary_text)
                st.info(f"Token Count: {token_count}")
            
            