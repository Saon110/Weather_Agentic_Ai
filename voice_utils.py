import speech_recognition as sr
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize ElevenLabs client
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Get voice settings from environment
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default Rachel voice
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_monolingual_v1")

def record_and_transcribe(duration=10):
    """Record audio from microphone and transcribe using Google's speech recognition"""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎙️ Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, phrase_time_limit=duration)
            print("✅ Recording finished.")

        text = recognizer.recognize_google(audio)
        print(f"📝 Transcribed: {text}")
        return text
        
    except sr.UnknownValueError:
        return "❌ Could not understand the audio."
    except sr.RequestError as e:
        return f"❌ Speech API error: {str(e)}"
    except Exception as e:
        return f"❌ Recording error: {str(e)}"

def speak(text):
    """Convert text to speech using ElevenLabs API"""
    if not text:
        return
        
    try:
        # Generate audio
        audio = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=text,
            model_id=MODEL_ID
        )
        
        # Play the audio
        play(audio)
        
    except Exception as e:
        raise RuntimeError(f"Voice generation failed: {str(e)}")