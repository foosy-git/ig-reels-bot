import os
import random
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PEXELS_API_KEY, TARGET_DURATION

QUERIES = ["two friends laughing", "couple walking", "friends coffee shop", "cinematic friends", "hugging friend", "romantic walk", "people sharing moment", "warm cafe friends"]

def fetch_background_video(output_filename="background.mp4"):
    """Fetches a random vertical video from Pexels."""
    if not PEXELS_API_KEY:
        raise ValueError("PEXELS_API_KEY is missing. Please set it in .env")

    query = random.choice(QUERIES)
    print(f"Searching Pexels for: {query}")
    
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&size=large&per_page=15"
    headers = {"Authorization": PEXELS_API_KEY}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    if not data.get('videos'):
        raise Exception(f"No videos found for query: {query}")
        
    # Filter for videos long enough
    valid_videos = [v for v in data['videos'] if v['duration'] >= TARGET_DURATION]
    
    if not valid_videos:
        valid_videos = data['videos'] # Fallback to any if none are long enough
        
    video_info = random.choice(valid_videos)
    
    # Get the best quality video file link
    video_files = video_info['video_files']
    # Prefer HD vertical
    best_file = None
    for vf in video_files:
        if vf['width'] >= 1080 and vf['height'] >= 1920:
            best_file = vf
            break
            
    if not best_file:
        best_file = max(video_files, key=lambda x: x['width'] * x['height'])
        
    print(f"Downloading video from Pexels (ID: {video_info['id']})")
    video_url = best_file['link']
    
    video_response = requests.get(video_url, stream=True)
    video_response.raise_for_status()
    
    output_path = os.path.join(os.getcwd(), output_filename)
    with open(output_path, 'wb') as f:
        for chunk in video_response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    print(f"Background video saved to {output_path}")
    return output_path

if __name__ == "__main__":
    fetch_background_video("test_bg.mp4")
