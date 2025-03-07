import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import gradio as gr
from fastapi import FastAPI

# Configure Gemini API
genai.configure(api_key="AIzaSyC9nma4N9yX08HgRd87TJ5BhFE-guX_4tw")

# Initialize TTS engine
engine = pyttsx3.init()

# Function to get AI response
def ask_gemini(prompt):
    response = genai.chat(model="gemini-pro").send_message(prompt)
    return response.text

# Function to convert text to speech
def speak(text):
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
        speak("Opening YouTube")
    elif "search google for" in command:
        search_query = command.replace("search google for", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        speak(f"Searching Google for {search_query}")
    elif "tell me a joke" in command:
        joke = ask_gemini("Tell me a joke.")
        speak(joke)
    elif "exit" in command:
        speak("Goodbye!")
        exit()
    else:
        response = ask_gemini(command)
        speak(response)

# Wake word activation
while True:
    wake_word = listen()
    if "hey assistant" in wake_word:
        speak("How can I help you?")
        command = listen()
        process_command(command)

# Web UI using Gradio
app = FastAPI()

def chat_with_assistant(text):
    return ask_gemini(text)

ui = gr.Interface(fn=chat_with_assistant, inputs="text", outputs="text")
@app.get("/")
def home():
    return {"message": "AI Voice Assistant is running"}

app = gr.mount_gradio_app(app, ui, path="/")
