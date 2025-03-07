import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
import webbrowser
import gradio as gr
from fastapi import FastAPI
from dotenv import load_dotenv

# Load API key from environment variable
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Function to get AI response
def ask_gemini(prompt):
    response = genai.chat(model="gemini-pro").send_message(prompt)
    return response.text

# Function to convert text to speech using gTTS
def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("response.mp3")
    return "response.mp3"

# Function to listen to voice commands
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        return command
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

# Function to process voice commands
def process_command(command):
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube"
    elif "search google for" in command:
        search_query = command.replace("search google for", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        return f"Searching Google for {search_query}"
    elif "tell me a joke" in command:
        joke = ask_gemini("Tell me a joke.")
        return joke
    else:
        return ask_gemini(command)

# Web UI using FastAPI + Gradio
app = FastAPI()

# API for text-based interaction
@app.get("/")
def home():
    return {"message": "AI Voice Assistant is running"}

def chat_with_assistant(text):
    response = process_command(text)
    return response, speak(response)  # Returns text + audio file

ui = gr.Interface(fn=chat_with_assistant, inputs="text", outputs=["text", "audio"])
app = gr.mount_gradio_app(app, ui, path="/")
