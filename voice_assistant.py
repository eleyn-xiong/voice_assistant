import os
import uuid
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from openai import OpenAI

print("Starting voice assistant...")

#load env vars
load_dotenv()

ELEVEN_API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not ELEVEN_API_KEY:
    raise ValueError("Missing ElevenLabs API key")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key")

eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

recognizer = sr.Recognizer()
mic = sr.Microphone()

messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly, intelligent voice assistant. "
            "Speak naturally and concisely. "
            "Do not repeat the user's words. "
            "Respond like a real assistant."
        )
    }
]



def listen():
    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    return recognizer.recognize_google(audio)

def speak(text):
    audio_stream = eleven_client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
        text=text,
        model_id="eleven_multilingual_v2"
    )

    filename = f"speech_{uuid.uuid4().hex}.wav"

    with open(filename, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)

    data, samplerate = sf.read(filename)
    sd.play(data, samplerate)
    sd.wait()

    os.remove(filename)

def get_ai_response(user_input):
    messages.append({"role": "user", "content": user_input})

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply



def main():
    speak("Hello Eleyn. How can I help you today?")
    while True:
        try:
            user_input = listen()
            print("You:", user_input)

            if "exit" in user_input.lower():
                speak("Goodbye!")
                break

            reply = get_ai_response(user_input)
            print("Assistant:", reply)
            speak(reply)

        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
