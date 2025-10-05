
def init_db():
    conn = sqlite3.connect('trending_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reddit_trending (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            score INTEGER,
            created_utc TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS hn_trending (
            id INTEGER PRIMARY KEY,
            title TEXT,
            url TEXT,
            score INTEGER,
            created_utc TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS news_trending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            url TEXT,
            published_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def fetch_and_store_reddit():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    trending = reddit.subreddit('popular').hot(limit=50)
    conn = sqlite3.connect('trending_data.db')
    c = conn.cursor()
    for post in trending:
        c.execute('''
            INSERT OR IGNORE INTO reddit_trending (id, title, url, score, created_utc)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            post.id,
            post.title,
            post.url,
            post.score,
            datetime.fromtimestamp(post.created_utc, timezone.utc).isoformat()
        ))
    conn.commit()
    conn.close()


def fetch_and_store_hackernews():
    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    ids = requests.get(url).json()[:30]
    conn = sqlite3.connect('trending_data.db')
    c = conn.cursor()
    for hn_id in ids:
        item_url = f'https://hacker-news.firebaseio.com/v0/item/{hn_id}.json'
        item = requests.get(item_url).json()
        if item and 'title' in item and 'url' in item:
            hn_time = item.get('time')
            if hn_time:
                created_utc = datetime.fromtimestamp(hn_time, timezone.utc).isoformat()
            else:
                created_utc = datetime.now(timezone.utc).isoformat()

            c.execute('''
                INSERT OR IGNORE INTO hn_trending (id, title, url, score, created_utc)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item['id'],
                item['title'],
                item['url'],
                item.get('score', 0),
                created_utc
            ))
    conn.commit()
    conn.close()


def fetch_and_store_newsapi():
    url = f'https://newsapi.org/v2/top-headlines?language=en&pageSize=20&apiKey={NEWSAPI_KEY}'
    resp = requests.get(url)
    if resp.status_code == 200:
        articles = resp.json().get('articles', [])
        conn = sqlite3.connect('trending_data.db')
        c = conn.cursor()
        for art in articles:
            published_at = art.get('publishedAt')
            if published_at:
                try:
                    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    published_at = dt.astimezone(timezone.utc).isoformat()
                except Exception:
                    published_at = datetime.now(timezone.utc).isoformat()
            else:
                published_at = datetime.now(timezone.utc).isoformat()

            c.execute('''
                INSERT INTO news_trending (source, title, url, published_at)
                VALUES (?, ?, ?, ?)
            ''', (
                art.get('source', {}).get('name', ''),
                art.get('title', ''),
                art.get('url', ''),
                published_at
            ))
        conn.commit()
        conn.close()
