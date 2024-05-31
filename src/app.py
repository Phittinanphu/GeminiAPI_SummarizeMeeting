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

def summarize_audio(audio_file_path):
    """Summarize the audio using Google's Generative API."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content(
        [
            # Encourage bullet points by starting the prompt with them
            """The attached audio file is a presentation or the conversation in the meeting. 
            Your task is to summarize every detail that mentioned in the audio file. 
            If it is a presentation:
            1. Summarize every detail that the speaker mentioned.
            2. If there are many speakers in the presentation, summarize every detail that each speaker mentioned.
            If it is a conversation in the meeting:
            1. Summarize every detail in the meeting.
            2. Summarize what each person plans to do in this week."""
            ,
            audio_file
        ])
    
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

def answer_question(summary_text, question):
    """Generate an answer to the question based on the summary text."""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        response = model.generate_content(
            [
                f"Based on the following summary, please answer the question:\n\n{summary_text}\n\nQuestion: {question}"
            ]
        )
        return response.text
    except Exception as e:
        st.error(f"Error generating answer: {e}")
        return ""

# Streamlit app interface
st.title('Audio Summarization App')

with st.expander("About this app"):
    st.write("""
        This app uses Google's generative AI (Gemini) to summarize presentation or meeting audio files. 
        Upload your audio file in WAV or MP3 format and get a summarization of its content.
    """)

audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])

# Initialize session state variables
if 'summary' not in st.session_state:
    st.session_state['summary'] = ""
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'chat_started' not in st.session_state:
    st.session_state['chat_started'] = False

if st.button('Summarize Audio'):
    if audio_file is not None:
        audio_path = save_uploaded_file(audio_file)  # Save the uploaded file and get the path
        if audio_path:
            with st.spinner('Summarizing...'):
                summary_text, token_count = summarize_audio(audio_path)
                st.session_state['summary'] = summary_text
                st.session_state['chat_history'] = []
                st.session_state['chat_started'] = False
                st.markdown(summary_text, unsafe_allow_html=True)  # Render HTML for newlines
                st.info(f"Token usage: {token_count}")
    else:
        st.warning("Please upload an audio file first.")

# Button to start the chat
if st.session_state['summary'] and not st.session_state['chat_started']:
    if st.button('Start Chat'):
        st.session_state['chat_started'] = True

# Multi-turn chat interface
if st.session_state['summary'] and st.session_state['chat_started']:
    st.subheader("Chat with the Summary")
    st.markdown(st.session_state['summary'], unsafe_allow_html=True)

    user_question = st.text_input("Ask a question about the summary:")

    if st.button('Ask'):
        if user_question:
            with st.spinner('Answering...'):
                answer = answer_question(st.session_state['summary'], user_question)
                st.session_state['chat_history'].append((user_question, answer))

    if st.session_state['chat_history']:
        for question, answer in st.session_state['chat_history']:
            st.markdown(f"**Question:** {question}")
            st.markdown(f"**Answer:** {answer}")
            st.markdown("---------------------------------")

