import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import gradio as gr
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check API key availability
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing! Set it in the .env file.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize TTS engine (only if running locally)
try:
    engine = pyttsx3.init()
    tts_enabled = True
except Exception:
    print("Text-to-Speech (TTS) is not supported in this environment.")
    tts_enabled = False

# Function to get AI response
def ask_gemini(prompt):
    try:
        response = genai.chat(model="gemini-pro").send_message(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Function to speak (Only works locally)
def speak(text):
    if tts_enabled:
        engine.say(text)
        engine.runAndWait()

# Function to listen to voice commands
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio).lower()
        print("You:", command)
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
        return ask_gemini("Tell me a joke.")
    else:
        return ask_gemini(command)

# FastAPI App
app = FastAPI()

def chat_with_assistant(text):
    return process_command(text)

# Web UI using Gradio
ui = gr.Interface(fn=chat_with_assistant, inputs="text", outputs="text")

# Mount Gradio app properly
app = gr.mount_gradio_app(app, ui, path="/")

# Run FastAPI Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
