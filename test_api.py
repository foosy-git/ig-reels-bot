import sys, os, requests
sys.path.append(os.path.abspath('.'))
from config import IG_USER_ID, IG_ACCESS_TOKEN

print('Fetching basic media metrics...')
url = f'https://graph.facebook.com/v22.0/{IG_USER_ID}/media?fields=id,caption,like_count,comments_count,media_product_type&access_token={IG_ACCESS_TOKEN}'
res = requests.get(url)
print(res.status_code)
data = res.json()
for d in data.get('data', [])[:3]:
    print(f"ID: {d['id']}, Likes: {d.get('like_count')}, Comments: {d.get('comments_count')}")
