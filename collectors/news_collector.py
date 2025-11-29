import requests
import config
from datetime import datetime

def collect_from_news(brand_keywords, risk_keywords):
    if not config.NEWS_API_KEY:
        print("⚠️ NewsAPI Key missing.")
        return []

    print(f"🌍 NewsAPI scanning: {brand_keywords}")
    query = " OR ".join(brand_keywords)
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={config.NEWS_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        results = []
        for article in data.get("articles", [])[:10]:
            if article['title'] == "[Removed]": continue
            results.append({
                "platform": "news",
                "brand": brand_keywords[0],
                "text": f"{article['title']} - {article.get('description','')}",
                "url": article['url'],
                "likes": 0, "comments": 0, "shares": 0,
                "created_at": datetime.now()
            })
        return results
    except Exception as e:
        print(f"❌ NewsAPI Error: {e}")
        return []