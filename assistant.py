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

PERSONALITIES = {
    'stephen_king': "You are the writer Stephen King. You are deep and introspective. Your responses are to be of similar calibre to his writing. ",
    'helpful': "You are a helpful assistant."
}

VERBOSITIES = {
    'short': "Your responses are always short.",
    'medium': "Your responses are always moderate in length.",
    'long': "Your responses are always long."
}

chosen_personality = 'helpful'
chosen_verbosity = 'short'

system_context = PERSONALITIES[chosen_personality] + VERBOSITIES[chosen_verbosity]

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
    print(f"Google text to speech conversion took {end_time - start_time:.2f} seconds.")


def listen_for_command():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("\nAdjusted for ambient noise.")
        print("Listening for 'computer'...")
        audio = recognizer.listen(source, timeout=1000)
        
        try:
            print("\nSending audio to Google for transcription...")
            start_time = time.time()
            text = recognizer.recognize_google(audio)
            end_time = time.time()
            print(
                f"Google speech to text took {end_time - start_time:.2f} seconds."
            )
            if "computer" in text.lower():
                print("Computer command detected.")
            return text.lower()
        except sr.UnknownValueError:
            print("Failed to recognize the command.")
            return ""


def get_response_from_openai(user_input):
    start_time = time.time()
    print("\nSending to OpenAI:")
    print(user_input)

    completion = openai.ChatCompletion.create(
        model="gpt-4-0314",
        messages=[
            {"role": "system", "content": system_context},
            {"role": "user", "content": user_input},
        ],
        max_tokens=1024,
    )

    end_time = time.time()
    print(
        f"Response from OpenAI generation took {end_time - start_time:.2f} seconds:\n)"
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
                    f"\nReceived transcription from Google. Voice to text conversion took {end_time - start_time:.2f} seconds."
                )
                response = get_response_from_openai(user_command)
                print(response)
                speak(response)
            except sr.UnknownValueError:
                speak("Sorry, I couldn't understand that.")
