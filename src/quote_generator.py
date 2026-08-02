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
        "True leadership is about serving others, not yourself.",
        "The power of listening and understanding in building deep relationships.",
        "How a leader's character influences their team more than their skills.",
        "Building trust: the foundation of every meaningful human connection.",
        "Empowering others to succeed rather than taking the credit.",
        "Why valuing people is the ultimate secret to true influence."
    ]
    selected_topic = random.choice(viral_topics)
    print(f"Selected Topic for Generation: {selected_topic}")
    
    prompt = f"""
    You are an expert social media copywriter for an Instagram page dedicated to profound, authoritative quotes on Leadership and People Relationships.
    Generate exactly 5 static text quotes focused specifically on this theme:
    "{selected_topic}" 
    
    CRITICAL INSTRUCTIONS: 
    1. Write quotes that provide timeless wisdom on leadership and human connection (similar to the tone of John C. Maxwell or Simon Sinek).
    2. They must be authoritative, insightful, and highly shareable—the kind of quote a manager or professional would instantly want to save or share.
    3. Keep them relatively short (1 to 2 sentences maximum per quote) so they fit beautifully in large font on a portrait image. Do not use hashtags or emojis in the quotes themselves.
    4. Make sure each of the 5 quotes is unique but fits the theme.
    
    Also generate a single Instagram caption to accompany this 5-slide carousel. The caption should be thoughtful, encourage engagement, and include high-reach hashtags like #leadership #relationships #growth #influence #mindset.
    
    Respond STRICTLY in JSON format:
    {{
      "quotes": [
        "The first leadership quote goes here.",
        "The second leadership quote goes here.",
        "The third leadership quote goes here.",
        "The fourth leadership quote goes here.",
        "The fifth leadership quote goes here."
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
        
        # Ensure we always return exactly 5 quotes
        if len(quotes) != 5:
            print("Warning: Gemini did not return exactly 5 quotes. Adjusting...")
            quotes = (quotes + [""] * 5)[:5]
            
        # Hard safeguard for caption length
        if len(caption) > 2100:
            caption = caption[:2100] + "..."
            
        return quotes, caption
    except Exception as e:
        print(f"Error from Gemini API: {e}")
        return (
            [
                "True leadership is not about being in charge. It is about taking care of those in your charge.",
                "People don't care how much you know until they know how much you care.",
                "A great leader's courage to fulfill their vision comes from passion, not position.",
                "Influence is built on a foundation of trust, empathy, and consistent integrity.",
                "You cannot lead people if you do not value them first."
            ],
            "Which one of these resonates with you the most? Drop your thoughts below! 👇\n\n#leadership #relationships #growth #influence #mindset"
        )

if __name__ == "__main__":
    quotes, caption = generate_content()
    print(f"Quotes: {json.dumps(quotes, indent=2)}\nCaption: {caption}")
