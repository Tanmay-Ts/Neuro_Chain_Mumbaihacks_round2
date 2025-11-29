import os
import sys
import requests
import praw
from googleapiclient.discovery import build
from openai import OpenAI
import config

# Define colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_status(service, status, message=""):
    if status == "PASS":
        print(f"[{GREEN}PASS{RESET}] {service}: {message}")
    elif status == "FAIL":
        print(f"[{RED}FAIL{RESET}] {service}: {message}")
    else:
        print(f"[{YELLOW}SKIP{RESET}] {service}: {message}")

def test_openai():
    print("\nTesting OpenAI...")
    if not config.OPENAI_API_KEY or "sk-" not in config.OPENAI_API_KEY:
        print_status("OpenAI", "FAIL", "Key missing or invalid format")
        return

    try:
        # Using the exact logic from core/llm_client.py
        client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            organization=config.OPENAI_ORG_ID,
            project=config.OPENAI_PROJECT_ID,
            base_url="https://api.openai.com/v1"
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        print_status("OpenAI", "PASS", f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print_status("OpenAI", "FAIL", str(e))

def test_newsapi():
    print("\nTesting NewsAPI...")
    if not config.NEWS_API_KEY or len(config.NEWS_API_KEY) < 10:
        print_status("NewsAPI", "SKIP", "Key appears empty")
        return

    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={config.NEWS_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print_status("NewsAPI", "PASS", f"Found {data.get('totalResults', 0)} articles")
        else:
            print_status("NewsAPI", "FAIL", f"Status Code: {response.status_code} - {response.json().get('message')}")
    except Exception as e:
        print_status("NewsAPI", "FAIL", str(e))

def test_reddit():
    print("\nTesting Reddit...")
    if not config.REDDIT_CLIENT_ID or not config.REDDIT_CLIENT_SECRET:
        print_status("Reddit", "SKIP", "Client ID or Secret missing")
        return

    try:
        reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT or "test_script/1.0"
        )
        # Try to fetch 1 post from r/python
        for submission in reddit.subreddit("python").hot(limit=1):
            print_status("Reddit", "PASS", f"Fetched post: {submission.title[:30]}...")
            return
    except Exception as e:
        print_status("Reddit", "FAIL", str(e))

def test_youtube():
    print("\nTesting YouTube...")
    if not config.YOUTUBE_API_KEY:
        print_status("YouTube", "SKIP", "Key missing")
        return

    try:
        youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
        request = youtube.search().list(part="snippet", q="news", maxResults=1)
        response = request.execute()
        if "items" in response:
            print_status("YouTube", "PASS", "Successfully searched video")
        else:
            print_status("YouTube", "FAIL", "No items returned")
    except Exception as e:
        print_status("YouTube", "FAIL", str(e))

def test_serpapi():
    print("\nTesting SerpAPI (Google)...")
    if not config.SERPAPI_KEY:
        print_status("SerpAPI", "SKIP", "Key missing")
        return

    try:
        url = f"https://serpapi.com/search.json?q=Apple&api_key={config.SERPAPI_KEY}&num=1"
        response = requests.get(url)
        if response.status_code == 200:
            print_status("SerpAPI", "PASS", "Search successful")
        else:
            print_status("SerpAPI", "FAIL", f"Error {response.status_code}: {response.text[:50]}...")
    except Exception as e:
        print_status("SerpAPI", "FAIL", str(e))

if __name__ == "__main__":
    print("="*40)
    print(" NeuroChain API Connectivity Test")
    print("="*40)
    
    test_openai()
    test_newsapi()
    test_reddit()
    test_youtube()
    test_serpapi()
    
    print("\n" + "="*40)
    print(" Test Complete")
    print("="*40)