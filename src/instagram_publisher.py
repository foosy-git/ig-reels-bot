import os
import time
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import IG_USER_ID, IG_ACCESS_TOKEN

def upload_to_temp_host(file_path):
    """
    Uploads the file to uguu.se to get a direct, temporary public URL.
    The Instagram Graph API requires a publicly accessible video URL.
    """
    print("Uploading video to temporary public host for Instagram processing...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                "https://uguu.se/upload", 
                files={"files[]": f}
            )
        
        response.raise_for_status()
        
        # uguu.se returns JSON with the file url
        data = response.json()
        direct_url = data['files'][0]['url']
        print(f"Temporary Public URL obtained: {direct_url}")
        return direct_url
    except Exception as e:
        print(f"Failed to upload to temp host: {e}")
        raise e

def publish_reel(video_url, caption):
    """
    Publishes a Reel to Instagram. 
    """
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        print("Instagram credentials missing. Skipping publish step.")
        return
        
    print("Initiating Instagram Reel upload...")
    
    # 1. Create Media Container
    post_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
    payload = {
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': caption,
        'access_token': IG_ACCESS_TOKEN,
        'share_to_feed': True
    }
    
    response = requests.post(post_url, data=payload)
    if response.status_code != 200:
        print(f"Failed to create media container: {response.text}")
        response.raise_for_status()
        
    container_id = response.json().get('id')
    print(f"Container created (ID: {container_id}). Waiting for Meta processing...")
    
    # 2. Poll for Status
    status_url = f"https://graph.facebook.com/v22.0/{container_id}?fields=status_code&access_token={IG_ACCESS_TOKEN}"
    
    max_retries = 30 # 2.5 minutes max
    retries = 0
    while retries < max_retries:
        status_res = requests.get(status_url)
        status_data = status_res.json()
        status = status_data.get('status_code')
        
        print(f"Status: {status}")
        if status == 'FINISHED':
            break
        elif status == 'ERROR':
            raise Exception(f"Meta failed to process the video. Details: {status_data}")
            
        time.sleep(5)
        retries += 1
        
    if retries >= max_retries:
        raise Exception("Timed out waiting for Meta to process the video.")
        
    # 3. Publish Media
    print("Publishing Reel...")
    publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        'creation_id': container_id,
        'access_token': IG_ACCESS_TOKEN
    }
    
    pub_res = requests.post(publish_url, data=publish_payload)
    pub_res.raise_for_status()
    
    print("Reel published successfully!")
    return pub_res.json()
