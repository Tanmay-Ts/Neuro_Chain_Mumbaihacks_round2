import os
from dotenv import load_dotenv

# Force reload .env to ensure fresh values
load_dotenv(override=True)

def get_clean_env(key, default=""):
    val = os.getenv(key, default)
    if val:
        return val.strip().strip('"').strip("'")
    return val

# --- OPENAI CONFIGURATION ---
OPENAI_API_KEY = get_clean_env("OPENAI_API_KEY")
OPENAI_ORG_ID = get_clean_env("OPENAI_ORG_ID")
OPENAI_PROJECT_ID = get_clean_env("OPENAI_PROJECT_ID")

# --- REAL DATA SOURCE KEYS ---
NEWS_API_KEY = get_clean_env("NEWS_API_KEY")
REDDIT_CLIENT_ID = get_clean_env("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = get_clean_env("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = get_clean_env("REDDIT_USER_AGENT", "neurochain_bot/1.0")
YOUTUBE_API_KEY = get_clean_env("YOUTUBE_API_KEY")
SERPAPI_KEY = get_clean_env("SERPAPI_KEY")

# --- EMAIL CONFIGURATION ---
EMAIL_SENDER = get_clean_env("EMAIL_SENDER")
EMAIL_PASSWORD = get_clean_env("EMAIL_PASSWORD")
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587

# --- APP CONFIG ---
BRAND_KEYWORDS = ["NeuroChain", "TechCorp", "AlphaSynergy"]
RISK_KEYWORDS = [
    "lawsuit", "antitrust", "monopoly", "layoffs", "privacy", 
    "scandal", "outage", "breach", "hack", "fine", "investigation",
    "fraud", "scam", "illegal", "danger", "collapse"
]

def has_key(key_name):
    val = globals().get(key_name)
    return val and "sk-" in str(val)