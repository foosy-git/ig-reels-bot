import json
import os
import sys
import random
from google import genai

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY

def generate_content(analytics_context=None):
    """Generates a quote and a caption using Gemini."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing. Please set it in .env")

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    viral_topics = [
        "Friendship Appreciation: A message about the friend who never judges you, who you can sit in silence with, and who feels like home. Focus on low-maintenance, deep connections.",
        "The Silent Supporter: A message for the friend who checks in on you when you go quiet, the one who notices when your energy shifts before anyone else does.",
        "Long Distance Friendship: The beauty of having a platonic soulmate where no matter how much time passes, the connection never fades.",
        "Relationship Gratitude: A reminder of how beautiful it is to finally find a partner who brings peace instead of chaos, and who makes the heavy days feel lighter.",
        "The Plot Twist: The feeling that after a long, difficult season, the universe is about to reward you with a massive, unexpected win. (Keep 20% focus on personal growth)"
    ]
    selected_topic = random.choice(viral_topics)
    print(f"Selected Topic for Generation: {selected_topic}")
    
    prompt = f"""
    You are an expert social media manager for a viral Instagram reels page.
    Generate a deeply relatable, conversational script focused specifically on this theme:
    "{selected_topic}" 
    
    CRITICAL INSTRUCTION: DO NOT use abstract poetry, metaphors about "seasons changing," or overly profound philosophical language. 
    Write in simple, natural, everyday language. It should sound like a cheerful, optimistic, and highly positive voice note from a best friend.
    
    ALGORITHMIC FOCUS: Optimize the script for "Shares". Subtly phrase it so the viewer immediately thinks of a specific person and wants to DM the reel to them. Ensure the tone leaves the viewer feeling incredibly happy and uplifted.
    
    The script MUST follow this exact 3-part viral structure:
    - **Part 1 (The Hook):** A short, highly relatable opening sentence designed to stop scrollers (e.g., 'Send this to the person who...', 'If you have a friend who...', 'A gentle reminder about the person who...').
    - **Part 2 (The Body):** A warm 2-3 sentence validation of the relationship. Keep it grounded in day-to-day life and quiet appreciation.
    - **Part 3 (The Outro):** A soft, practical closing thought expressing gratitude.
    
    The entire script should take about 15 to 25 seconds to read aloud slowly.
    """
    
    if analytics_context:
        prompt += f"\n\nTo help you capture the perfect viral tone, here is data from our recent top-performing videos:\n{analytics_context}\nPlease lean heavily into the style, hooks, and themes that made these top videos successful, but write a brand new script!"
        
    prompt += """
    
    Also generate an engaging caption with a universal call-to-action (e.g., 'Share this with someone you love' or 'Save this reminder') and high-reach hashtags like #healingjourney, #lifequotes, #mindfulness, and #innerpeace.
    
    Respond STRICTLY in JSON format:
    {
      "quote": "The full generated text (Hook + Body + Outro) as a single continuous paragraph.",
      "caption": "The caption with CTA and hashtags here."
    }
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
            
        data = json.loads(text.strip())
        return data['quote'], data['caption']
    except Exception as e:
        print(f"Error from Gemini API: {e}")
        return (
            "Healing doesn't mean the damage never existed. It means the damage no longer controls our lives. It means we have finally decided to take back our power and walk toward the light. Your journey is yours alone, but you are never truly alone.",
            "Save this reminder for when you need it most. ✨\n\n#healingjourney #lifequotes #mindfulness #innerpeace #growth"
        )

if __name__ == "__main__":
    quote, caption = generate_content()
    print(f"Quote: {quote}\nCaption: {caption}")
