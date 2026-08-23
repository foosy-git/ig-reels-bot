import os
import time
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import IG_USER_ID, IG_ACCESS_TOKEN

def upload_to_temp_host(file_path):
    """
    Uploads the file to uguu.se to get a direct, temporary public URL.
    """
    print(f"Uploading {file_path} to temporary public host...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                "https://uguu.se/upload", 
                files={"files[]": f},
                timeout=30
            )
        
        response.raise_for_status()
        
        data = response.json()
        direct_url = data['files'][0]['url']
        print(f"Temporary Public URL obtained: {direct_url}")
        return direct_url
    except Exception as e:
        print(f"Failed to upload to temp host: {e}")
        raise e

def create_carousel_item(image_url):
    """Creates a container for a single image in a carousel."""
    post_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'is_carousel_item': 'true',
        'access_token': IG_ACCESS_TOKEN
    }
    response = requests.post(post_url, data=payload, timeout=30)
    if response.status_code != 200:
        print(f"Meta API Error (Carousel Item): {response.text}")
    response.raise_for_status()
    item_id = response.json().get('id')
    print(f"Created carousel item container (ID: {item_id})")
    return item_id

def publish_carousel(image_paths, caption):
    """
    Publishes a Carousel (multiple images) to Instagram.
    """
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        print("Instagram credentials missing. Skipping publish step.")
        return
        
    print("Initiating Instagram Carousel upload...")
    
    # 1. Upload all images and create item containers
    item_ids = []
    for path in image_paths:
        public_url = upload_to_temp_host(path)
        item_id = create_carousel_item(public_url)
        item_ids.append(item_id)
        time.sleep(2) # brief pause to prevent rate limiting
        
    # 2. Create the main Carousel Container
    print("Creating main Carousel container...")
    carousel_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
    carousel_payload = {
        'media_type': 'CAROUSEL',
        'children': ','.join(item_ids),
        'caption': caption,
        'access_token': IG_ACCESS_TOKEN
    }
    
    response = requests.post(carousel_url, data=carousel_payload, timeout=30)
    if response.status_code != 200:
        print(f"Failed to create carousel container: {response.text}")
        response.raise_for_status()
        
    container_id = response.json().get('id')
    print(f"Carousel container created (ID: {container_id}). Waiting for Meta processing...")
    
    # 3. Poll for Status
    status_url = f"https://graph.facebook.com/v22.0/{container_id}?fields=status_code&access_token={IG_ACCESS_TOKEN}"
    
    max_retries = 30 # 2.5 minutes max
    retries = 0
    while retries < max_retries:
        status_res = requests.get(status_url, timeout=30)
        status_data = status_res.json()
        status = status_data.get('status_code')
        
        print(f"Status: {status}")
        if status == 'FINISHED':
            break
        elif status == 'ERROR':
            raise Exception(f"Meta failed to process the carousel. Details: {status_data}")
            
        time.sleep(5)
        retries += 1
        
    if retries >= max_retries:
        raise Exception("Timed out waiting for Meta to process the carousel.")
        
    # 4. Publish Media
    print("Publishing Carousel...")
    publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        'creation_id': container_id,
        'access_token': IG_ACCESS_TOKEN
    }
    
    pub_res = requests.post(publish_url, data=publish_payload, timeout=30)
    pub_res.raise_for_status()
    
    print("Carousel published successfully!")
    return pub_res.json()
