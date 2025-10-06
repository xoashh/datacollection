import praw
import requests
import sqlite3
from datetime import datetime, timezone

# --- Database Initialization ---
def init_db():
    """Creates the database tables if they don't exist."""
    conn = sqlite3.connect('trending_data.db')
    c = conn.cursor()
    
    # Create Reddit table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reddit_trending (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            score INTEGER,
            created_utc REAL
        )
    ''')
    
    # Create Hacker News table
    c.execute('''
        CREATE TABLE IF NOT EXISTS hn_trending (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            score INTEGER,
            created_utc REAL
        )
    ''')
    
    # Create NewsAPI table
    c.execute('''
        CREATE TABLE IF NOT EXISTS news_trending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            url TEXT UNIQUE,
            published_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# --- Data Fetching Functions ---
def fetch_and_store_reddit():
    """Fetches trending data from Reddit and stores it."""
    # TODO: Add your PRAW logic here to fetch data from Reddit
    print("Fetching and storing Reddit data... (placeholder)")
    # Example: conn.execute("INSERT INTO ...")

def fetch_and_store_hackernews():
    """Fetches trending data from Hacker News and stores it."""
    # TODO: Add your requests logic here to fetch data from the HN API
    print("Fetching and storing Hacker News data... (placeholder)")
    # Example: conn.execute("INSERT INTO ...")

def fetch_and_store_newsapi():
    """Fetches trending data from NewsAPI and stores it."""
    # TODO: Add your requests logic here to fetch data from NewsAPI
    print("Fetching and storing NewsAPI data... (placeholder)")
    # Example: conn.execute("INSERT INTO ...")


def main():
    """Main function to run all data collection steps."""
    init_db()
    fetch_and_store_reddit()
    fetch_and_store_hackernews()
    fetch_and_store_newsapi()
    print("Trending data collection process finished.")

# This allows you to run this file by itself to collect data
if __name__ == "__main__":
    main()