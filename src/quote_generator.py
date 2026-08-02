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
        "Unspoken truth about true friendship and loyalty.",
        "Overcoming silent struggles and finding inner peace.",
        "The pain of letting go of someone you love, but knowing it's right.",
        "A reminder that you are enough, even on your hardest days.",
        "The beauty of quiet moments and self-love.",
        "Appreciating the people who stayed when things got hard."
    ]
    selected_topic = random.choice(viral_topics)
    print(f"Selected Topic for Generation: {selected_topic}")
    
    prompt = f"""
    You are an expert social media copywriter for an Instagram page dedicated to deeply emotional, relatable, and beautiful quotes.
    Generate exactly 3 static text quotes focused specifically on this theme:
    "{selected_topic}" 
    
    CRITICAL INSTRUCTIONS: 
    1. Write quotes that touch people's hearts. They must be highly relatable, slightly vulnerable, and evoke a strong emotional response (nostalgia, comfort, gentle melancholy, or profound gratitude).
    2. The quotes MUST be highly shareable—the kind of quote someone instantly wants to forward to their best friend, partner, or put on their story because it perfectly captures how they feel.
    3. Keep them relatively short (1 to 3 sentences maximum per quote) so they fit beautifully in large font on a portrait image. Do not use hashtags or emojis in the quotes themselves.
    4. Make sure each of the 3 quotes is unique but fits the theme.
    
    Also generate a single Instagram caption to accompany this 3-slide carousel. The caption should be thoughtful, encourage people to tag a friend or share, and include high-reach hashtags like #quotes #relatable #lifequotes #mindset #growth.
    
    Respond STRICTLY in JSON format:
    {{
      "quotes": [
        "The first emotional quote goes here.",
        "The second emotional quote goes here.",
        "The third emotional quote goes here."
      ],
      "caption": "The caption with CTA and hashtags here."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
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
        
        quotes = data['quotes']
        caption = data['caption']
        
        # Ensure we always return exactly 3 quotes
        if len(quotes) != 3:
            print("Warning: Gemini did not return exactly 3 quotes. Adjusting...")
            quotes = (quotes + [""] * 3)[:3]
            
        # Hard safeguard for caption length
        if len(caption) > 2100:
            caption = caption[:2100] + "..."
            
        return quotes, caption
    except Exception as e:
        print(f"Error from Gemini API: {e}")
        return (
            [
                "Some people arrive and make such a beautiful impact on your life, you can barely remember what life was like without them.",
                "It takes courage to let go of what you can't change and embrace the quiet peace of starting over.",
                "Forward this to someone who makes your bad days a little bit brighter just by existing."
            ],
            "Tag the person who came to mind. ❤️\n\n#quotes #friendship #love #healing #relatable #mindset"
        )

if __name__ == "__main__":
    quotes, caption = generate_content()
    print(f"Quotes: {json.dumps(quotes, indent=2)}\nCaption: {caption}")
