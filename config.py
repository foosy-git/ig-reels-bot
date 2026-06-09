import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Instagram / Meta API
IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

# Edge TTS Settings
# en-US-AriaNeural is a very warm, empathetic, and captivating female voice.
VOICE_NAME = "en-US-AriaNeural"

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
TARGET_DURATION = 15 # Minimum duration in seconds (15-30s)
