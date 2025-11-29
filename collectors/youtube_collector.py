from googleapiclient.discovery import build
import config
from datetime import datetime

def collect_from_youtube(brand_keywords, risk_keywords):
    if not config.YOUTUBE_API_KEY:
        print("⚠️ YouTube Key missing. Skipping YouTube.")
        return []

    print(f"📺 Connecting to YouTube...")
    
    try:
        youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
        # Search for brand name
        query = " OR ".join(brand_keywords)
        
        request = youtube.search().list(
            q=query,
            part="snippet",
            order="date",
            maxResults=5, # Limit to 5 for speed
            type="video"
        )
        response = request.execute()
        
        results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            results.append({
                "platform": "youtube",
                "brand": brand_keywords[0],
                "text": f"{item['snippet']['title']} - {item['snippet']['description']}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "likes": 0, 
                "comments": 0,
                "shares": 0,
                "created_at": datetime.now()
            })
        return results
    except Exception as e:
        print(f"❌ YouTube Error: {e}")
        return []