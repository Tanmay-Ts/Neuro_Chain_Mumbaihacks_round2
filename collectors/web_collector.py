import requests
import config
from datetime import datetime

def collect_from_web(brand_keywords, risk_keywords):
    if not config.SERPAPI_KEY:
        print("⚠️ SerpAPI Key missing. Skipping Web Search.")
        return []

    print(f"🕸️ Connecting to Google Web Search...")
    
    query = " OR ".join(brand_keywords)
    # Search specifically for news or discussions
    url = f"https://serpapi.com/search.json?q={query}&api_key={config.SERPAPI_KEY}&num=5&tbm=nws"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        results = []
        for result in data.get("news_results", []):
            results.append({
                "platform": "web",
                "brand": brand_keywords[0],
                "text": f"{result.get('title')} - {result.get('snippet', '')}",
                "url": result.get('link'),
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "created_at": datetime.now()
            })
        return results
    except Exception as e:
        print(f"❌ Web Search Error: {e}")
        return []