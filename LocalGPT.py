import pathlib
import textwrap
import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/phitt/OneDrive/Documents/GitHub/GeminiAPI_SummarizeMeeting/gemini-api-424003-6ac26a951d8e.json"

model = genai.GenerativeModel('gemini-pro')

prompt = st.text_input("Enter your prompt:")
if st.button("Generate"):
    if prompt:
        response = model.generate_content(prompt, stream=True)

        response_container = st.empty()
        
        for chunk in response:
            response.resolve()
            response_container.text_area("Gemini Response:",response.text, key=f"text_area_{chunk}")
                
                

# /Users/phitt/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/site-packages/streamlit