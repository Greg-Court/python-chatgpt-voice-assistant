import os
import time
from dotenv import load_dotenv
import openai
from gtts import gTTS
import speech_recognition as sr
import pygame

load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API key initialized.")

# Initialize the recognizer and microphone
recognizer = sr.Recognizer()
print("Recognizer and microphone initialized.")

pygame.mixer.init()  # initialize pygame mixer for playing audio
print("Pygame mixer initialized.")


def speak(text):
    start_time = time.time()

    tts = gTTS(text=text, lang="en")
    tts.save("temp.mp3")
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.remove("temp.mp3")

    end_time = time.time()
    print(f"Converting text to speech took {end_time - start_time:.2f} seconds.")


def listen_for_command():
    start_time = time.time()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Adjusted for ambient noise.")
        print("Listening for 'computer'...")
        audio = recognizer.listen(source, timeout=10)
        try:
            print("Sending audio to Google for transcription...")
            text = recognizer.recognize_google(audio)
            end_time = time.time()
            print(
                f"Received transcription from Google. Voice to text conversion took {end_time - start_time:.2f} seconds."
            )
            if "computer" in text.lower():
                print("Computer command detected.")
            return text.lower()
        except sr.UnknownValueError:
            print("Failed to recognize the command.")
            return ""


def get_response_from_openai(user_input):
    start_time = time.time()
    print("Sending command to OpenAI...")

    completion = openai.ChatCompletion.create(
        model="gpt-4-0314",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ],
        max_tokens=128,
    )

    end_time = time.time()
    print(
        f"Received response from OpenAI. Response generation took {end_time - start_time:.2f} seconds."
    )
    return completion.choices[0].message["content"]


while True:
    command = listen_for_command()
    if "computer" in command:
        speak("Yes?")
        start_time = time.time()

        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                print("Sending audio to Google for transcription...")
                user_command = recognizer.recognize_google(audio)
                end_time = time.time()
                print(
                    f"Received transcription from Google. Voice to text conversion took {end_time - start_time:.2f} seconds."
                )
                response = get_response_from_openai(user_command)
                print(response)
                speak(response)
            except sr.UnknownValueError:
                speak("Sorry, I couldn't understand that.")
