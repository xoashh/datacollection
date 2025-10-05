import praw
import requests
import sqlite3
from datetime import datetime, timezone

# --- Reddit API Setup ---




def main():
    init_db()
    fetch_and_store_reddit()
    fetch_and_store_hackernews()
    fetch_and_store_newsapi()
    print("Trending data collected and stored.")


if __name__ == "__main__":
    main()
