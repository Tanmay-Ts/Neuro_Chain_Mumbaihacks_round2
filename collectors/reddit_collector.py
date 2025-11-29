import praw
import config
from datetime import datetime

def collect_from_reddit(brand_keywords, risk_keywords):
    if not config.REDDIT_CLIENT_ID or not config.REDDIT_CLIENT_SECRET:
        print("⚠️ Reddit Keys missing. Skipping Reddit.")
        return []

    print(f"👽 Connecting to Reddit...")
    
    try:
        reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT
        )
        
        results = []
        query = " OR ".join(brand_keywords)
        
        # Search all subreddits
        for submission in reddit.subreddit("all").search(query, sort="new", limit=5):
            results.append({
                "platform": "reddit",
                "brand": brand_keywords[0],
                "text": f"{submission.title} - {submission.selftext[:200]}",
                "url": submission.url,
                "likes": submission.score,
                "comments": submission.num_comments,
                "shares": 0,
                "created_at": datetime.utcfromtimestamp(submission.created_utc)
            })
        return results
    except Exception as e:
        print(f"❌ Reddit Error: {e}")
        return []