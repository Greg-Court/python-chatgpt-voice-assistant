import os
from dotenv import load_dotenv
import openai
from gtts import gTTS
import speech_recognition as sr
import pygame

load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the recognizer and microphone
recognizer = sr.Recognizer()

pygame.mixer.init()  # initialize pygame mixer for playing audio


def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("temp.mp3")
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.remove("temp.mp3")


def listen_for_command():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for 'computer'...")
        audio = recognizer.listen(source, timeout=10)  # Adjust the timeout as needed
        try:
            text = recognizer.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            return ""


def get_response_from_openai(user_input):
    completion = openai.ChatCompletion.create(
        model="gpt-4-0314",  # Ensure you're using the right model name
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ],
    )
    return completion.choices[0].message["content"]


while True:
    command = listen_for_command()
    if "computer" in command:
        speak("Yes?")

        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                user_command = recognizer.recognize_google(audio)
                response = get_response_from_openai(user_command)
                speak(response)
            except sr.UnknownValueError:
                speak("Sorry, I couldn't understand that.")
