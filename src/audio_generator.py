import os
import sys
import asyncio
import edge_tts

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VOICE_NAME

def generate_audio(text, output_filename="audio.mp3"):
    """Generates speech from text using Microsoft Edge TTS (100% Free)."""
    
    print(f"Generating audio for text: '{text}' using voice: {VOICE_NAME}...")
    output_path = os.path.join(os.getcwd(), output_filename)
    
    # Added a +25% speed increase so the voice sounds punchy and extremely fast-paced for tech audiences
    communicate = edge_tts.Communicate(text, VOICE_NAME, rate="+25%")
    
    # Run the async edge_tts function in a synchronous wrapper
    asyncio.run(communicate.save(output_path))
    
    print(f"Audio saved to {output_path}")
    return output_path

if __name__ == "__main__":
    # Test script
    generate_audio("This is a test of the free cinematic audio generator.", "test_audio.mp3")
