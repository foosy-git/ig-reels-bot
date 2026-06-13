import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import IG_USER_ID, IG_ACCESS_TOKEN

def get_top_performing_context(limit=15, top_k=3):
    """
    Fetches the most recent Reels from the user's IG account.
    Ranks them by total engagement (likes + comments * 2) to find what resonates.
    Returns a formatted string of the top-performing scripts to use as LLM context.
    """
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        print("Missing IG credentials. Skipping analytics fetch.")
        return None
        
    print(f"Fetching recent {limit} reels to analyze performance...")
    
    # Fetch recent media with basic engagement metrics
    url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
    params = {
        "fields": "id,caption,like_count,comments_count,media_product_type",
        "access_token": IG_ACCESS_TOKEN,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            print(f"Error fetching analytics: {data['error']['message']}")
            return None
            
        media_items = data.get("data", [])
        
        # Filter for only Reels and calculate an engagement score
        reels = []
        for item in media_items:
            if item.get("media_product_type") == "REELS" and "caption" in item:
                likes = item.get("like_count", 0)
                comments = item.get("comments_count", 0)
                # Comments indicate deeper engagement, so we weight them slightly higher
                score = likes + (comments * 2)
                
                reels.append({
                    "id": item["id"],
                    "caption": item["caption"],
                    "score": score,
                    "likes": likes,
                    "comments": comments
                })
                
        if not reels:
            print("No reels found to analyze.")
            return None
            
        # Sort by engagement score descending
        reels.sort(key=lambda x: x["score"], reverse=True)
        top_reels = reels[:top_k]
        
        # Format the top captions into a readable context block for Gemini
        context = ""
        for i, reel in enumerate(top_reels, 1):
            # Clean up caption (strip hashtags if possible, but keeping them is okay)
            clean_caption = reel['caption'].split('#')[0].strip()
            if not clean_caption:
                clean_caption = reel['caption']
                
            context += f"--- VIRAL VIDEO #{i} (Score: {reel['score']}, Likes: {reel['likes']}) ---\n"
            context += f"Script: {clean_caption}\n\n"
            
        print(f"Successfully analyzed analytics. Found {len(top_reels)} top performing scripts.")
        return context
        
    except Exception as e:
        print(f"Failed to fetch analytics: {e}")
        return None

if __name__ == "__main__":
    context = get_top_performing_context()
    if context:
        print("\n=== TOP PERFORMING CONTEXT FOR AI ===")
        print(context)
