import config

def score_priority(likes, comments, shares, text):
    """
    Calculates priority based on engagement metrics and risk keywords.
    """
    # Safe defaults
    likes = likes or 0
    comments = comments or 0
    shares = shares or 0
    text = text or ""

    # 1. Base Score from Engagement
    # (1 like = 1 pt, 1 comment = 2 pts, 1 share = 3 pts)
    score = likes + (2 * comments) + (3 * shares)
    
    text_lower = text.lower()
    
    # 2. Risk Keyword Boost
    # If a dangerous keyword is found, we boost the score significantly.
    risk_found = any(risk in text_lower for risk in config.RISK_KEYWORDS)
    
    if risk_found:
        score += 150 # Massive boost to ensure it hits High priority
        
    # 3. Determine Tier
    # Adjusted thresholds to ensure Risk Keywords always trigger High
    if score >= 100:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"