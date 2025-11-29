from collectors.news_collector import collect_from_news
from collectors.reddit_collector import collect_from_reddit
from collectors.youtube_collector import collect_from_youtube
from collectors.web_collector import collect_from_web
from core.priority import score_priority
from models import create_post
from db import get_db
import config

def collect_for_company(company_name, risk_keywords):
    """
    Runs collectors for a SPECIFIC company.
    """
    brand_keywords = [company_name]
    raw_data = []
    
    print(f"🔎 Scanning for {company_name}...")
    
    # Run all collectors
    # We catch errors individually inside collectors so one fail doesn't stop others
    raw_data.extend(collect_from_news(brand_keywords, risk_keywords))
    raw_data.extend(collect_from_reddit(brand_keywords, risk_keywords))
    raw_data.extend(collect_from_youtube(brand_keywords, risk_keywords))
    raw_data.extend(collect_from_web(brand_keywords, risk_keywords))

    db = next(get_db())
    saved_count = 0

    for item in raw_data:
        # Calculate Priority
        prio = score_priority(
            item.get('likes'), 
            item.get('comments'), 
            item.get('shares'), 
            item.get('text')
        )
        item['priority'] = prio

        # --- LOGIC UPDATE: Save ALL posts (Low/Med/High) ---
        # We removed the 'if prio in [Med, High]' check so you can see everything.
        post = create_post(db, item)
        if post:
            saved_count += 1
            print(f"   Saved: {item['text'][:30]}... [{prio}]")
    
    print(f"   -> Total new posts saved: {saved_count}")
    return saved_count

def collect_all_sources():
    # Fallback
    return collect_for_company("Google", config.RISK_KEYWORDS)