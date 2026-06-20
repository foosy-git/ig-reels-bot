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
        "Hidden AI Tools: Discovering lesser-known AI websites or tools that can save you 10+ hours a week. Focus on tools that feel like a 'cheat code'.",
        "Workflow Automation: A tip on how to automate repetitive daily tasks (emails, data entry, scheduling) using tools like Zapier or AI assistants.",
        "ChatGPT Prompt Engineering: Sharing a highly specific, advanced ChatGPT prompt that solves a common productivity problem or supercharges learning.",
        "Time Management Frameworks: Combining technology with deep work frameworks (like automated Pomodoro or AI-driven calendar blocking) to beat burnout.",
        "The Anti-Hustle Automation: Using AI not to work harder, but to work less so you can enjoy your life. Focus on 'getting time back'."
    ]
    selected_topic = random.choice(viral_topics)
    print(f"Selected Topic for Generation: {selected_topic}")
    
    prompt = f"""
    You are an expert social media manager and AI productivity consultant for a viral tech Instagram reels page.
    Generate a highly actionable, fast-paced script focused specifically on this theme:
    "{selected_topic}" 
    
    CRITICAL INSTRUCTION: DO NOT use poetic, emotional, or philosophical language. Write in sharp, authoritative, and energetic language. It should sound like an exclusive tip from a senior tech founder.
    
    ALGORITHMIC FOCUS: Optimize the script for "Saves". The viewer must feel an overwhelming urge to hit the "Save" button so they can reference the tools/tips later.
    
    The script MUST follow this exact 3-part viral structure:
    - **Part 1 (The Hook - Save Bait):** A fast, high-energy opening sentence that creates FOMO (e.g., '3 AI tools that feel illegal to know', 'Stop doing X manually, do this instead', 'Save this workflow for Monday morning').
    - **Part 2 (The Value & How-To):** Name a specific, actionable tool or prompt structure AND explicitly explain HOW to use it in a real-world scenario. Give concrete context (e.g., don't just say 'Use Zapier', say 'Use Zapier to automatically turn starred emails into tasks in Notion so nothing falls through the cracks.'). Keep it punchy but dense with practical value.
    - **Part 3 (The CTA):** A brief closing directing them to the caption.
    
    The entire script should be fast and take exactly 15 to 25 seconds to read aloud.
    """
    
    if analytics_context:
        prompt += f"\n\nTo help you capture the perfect viral tone, here is data from our recent top-performing videos:\n{analytics_context}\nPlease lean heavily into the style, hooks, and themes that made these top videos successful, but write a brand new script!"
        
    prompt += """
    
    Also generate a LONG, highly detailed, step-by-step tutorial caption. It must be long enough that it takes the viewer at least 30-40 seconds to read (which will cause the short video to loop multiple times in the background, skyrocketing Watch Time). 
    
    The caption MUST end with a high-engagement call to action: 'Comment AUTOMATE and I will DM you the exact links/prompts.'
    Include high-reach hashtags like #ai #productivity #automation #tech #chatgpt.
    
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
            "Stop wasting hours on repetitive tasks. Save this video for Monday. Tool number 1 is Zapier. You can use Zapier to automatically turn starred emails into Notion tasks so nothing falls through the cracks. Read the caption for the exact setup.",
            "Want to get 10 hours of your week back? Here is the exact step-by-step workflow you need to set up right now. First... [Detailed tutorial here].\n\nComment AUTOMATE and I will send you the direct links right now!\n\n#ai #productivity #automation #tech #chatgpt"
        )

if __name__ == "__main__":
    quote, caption = generate_content()
    print(f"Quote: {quote}\nCaption: {caption}")
