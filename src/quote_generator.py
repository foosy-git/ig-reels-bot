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
        "Friendship: A message about platonic soulmates, outgrowing friends, or the beauty of low-maintenance friendships.",
        "The Unsent Letter: Silent breakups and the quiet grief of walking away from someone who didn't fight to keep you.",
        "The Plot Twist: The feeling that after a long, difficult season, the universe is about to reward you with a massive, unexpected win.",
        "Soft Discipline: Doing the hard things (gym, studying, working) not out of aggression, but as an act of profound self-love for your future self.",
        "Burnout & Exhaustion: Validating the feeling of being chronically tired from the daily grind and overwhelming everyday tasks."
    ]
    selected_topic = random.choice(viral_topics)
    print(f"Selected Topic for Generation: {selected_topic}")
    
    prompt = f"""
    You are an expert social media manager for a viral Instagram reels page.
    Generate a deeply relatable, conversational script focused specifically on this theme:
    "{selected_topic}" 
    
    CRITICAL INSTRUCTION: DO NOT use abstract poetry, metaphors about "seasons changing," or overly profound philosophical language. 
    Write in simple, natural, everyday language. It should sound like a warm, supportive voice note from a best friend who understands the daily grind.
    
    The script MUST follow this exact 3-part viral structure:
    - **Part 1 (The Hook):** A short, highly relatable opening sentence designed to stop scrollers (e.g., 'If you're waking up feeling completely exhausted today...', 'A gentle reminder for anyone who feels like they are falling behind...').
    - **Part 2 (The Body):** A warm 2-3 sentence validation of their feelings and an encouraging shift in perspective. Keep it grounded in day-to-day life.
    - **Part 3 (The Outro):** A soft, practical closing thought (e.g., 'Take a deep breath. You are doing okay.', 'Go easy on yourself today.').
    
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
