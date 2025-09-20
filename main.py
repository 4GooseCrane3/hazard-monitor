import requests
from bs4 import BeautifulSoup
import json
import praw
from googleapiclient.discovery import build

TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAG%2FK4AEAAAAAtVpmsL6JyUqWKwctnvvtH8n%2B5kg%3D3BBlfBA2OCuMxljuNv9L1GJ1siYJlwzjVr2QobpG9rQu9y3LhS"
TWITTER_QUERY = "tsunami OR cyclone OR flood"

def fetch_twitter():
    url = f"https://api.twitter.com/2/tweets/search/recent?query={TWITTER_QUERY}&max_results=5"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    response = requests.get(url, headers=headers)
    tweets = response.json().get("data", [])
    return [{"source": "Twitter", "text": t["text"]} for t in tweets]

REDDIT_CLIENT_ID = "IJQPwSTNiehgyXVGyJ8S0w"
REDDIT_CLIENT_SECRET = "xWBPxG4TkjMv2wzSFc7ExXxcErvsGA"
REDDIT_USER_AGENT = "hazard-monitor"

def fetch_reddit():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    subreddit = reddit.subreddit("disaster+india")
    posts = []
    for post in subreddit.new(limit=5):
        posts.append({
            "source": "Reddit",
            "title": post.title,
            "url": post.url
        })
    return posts

YOUTUBE_API_KEY = "AIzaSyBNkdFN9TH1ATalRh62Db6QULBJH2iZglQ"
YOUTUBE_QUERY = "tsunami OR cyclone OR flood"

def fetch_youtube():
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=YOUTUBE_QUERY, part="snippet", maxResults=5)
    response = request.execute()
    videos = []
    for item in response["items"]:
        videos.append({
            "source": "YouTube",
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                   if item["id"]["kind"] == "youtube#video" else ""
        })
    return videos

NEWS_URL = "https://www.ndma.gov.in/news"

def fetch_news():
    response = requests.get(NEWS_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    news = []
    for article in soup.find_all("h2", class_="news-title"):
        title = article.text.strip()
        link = article.find("a")["href"]
        news.append({
            "source": "NDMA News",
            "title": title,
            "url": link
        })
    return news

def main():
    all_posts = []
    all_posts.extend(fetch_twitter())
    all_posts.extend(fetch_reddit())
    all_posts.extend(fetch_youtube())
    all_posts.extend(fetch_news())
    with open("hazard_data.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=4)
    print("Data fetched and saved to hazard_data.json\n")
    for p in all_posts:
        print(p)

if __name__ == "__main__":
    main()

