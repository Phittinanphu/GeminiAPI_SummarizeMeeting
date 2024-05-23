import streamlit as st
import tempfile
import os
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

# Configure Google API for audio summarization
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/phitt/OneDrive/Documents/GitHub/GeminiAPI_SummarizeMeeting/gemini-api-424003-6ac26a951d8e.json"

#start_keyword = "Current week"
#end_keyword = "The end"

def summarize_audio(audio_file_path):
    """Summarize the audio using Google's Generative API."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content(
        [
            # Encourage bullet points by starting the prompt with them
            "Base on this audio, what will each person do in the current week, and please provide the name of the person",
            audio_file
        ]
    )
    token = model.count_tokens(response.text)
    # Convert escaped newlines (\n) to actual newlines
    formatted_text = response.text.replace("\n", "<br>")
    return formatted_text, token

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

audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])

# Displaying the summary
if st.button('Summarize Audio'):
    audio_path = save_uploaded_file(audio_file)  # Save the uploaded file and get the path
    with st.spinner('Summarizing...'):
        summary_text, token_count = summarize_audio(audio_path)
        st.markdown(summary_text, unsafe_allow_html=True)  # Render HTML for newlines
        st.info(f"{token_count}") # Display token usage