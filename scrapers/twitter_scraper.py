import snscrape.modules.twitter as sntwitter
from datetime import datetime, timezone

def fetch_twitter_trending(limit=20):
    """Fetch recent trending tweets."""
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper("trending OR viral OR news").get_items()):
        if i >= limit:
            break
        tweets.append({
            "username": tweet.user.username,
            "content": tweet.content,
            "date": tweet.date.astimezone(timezone.utc).isoformat(),
            "url": f"https://twitter.com/{tweet.user.username}/status/{tweet.id}"
        })
    return tweets
