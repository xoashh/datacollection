from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
import sqlite3
import pandas as pd
import io

API_KEYS = {"your_test_key": "Test User"}  # Replace with your real buyer keys

app = FastAPI()

def check_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")

def query_table(table, limit):
    conn = sqlite3.connect('trending_data.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM {table} ORDER BY created_utc DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    columns = [desc[0] for desc in c.description]
    results = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return results

@app.get("/reddit/trending")
def get_reddit_trending(limit: int = 20, x_api_key: str = Header(...)):
    check_api_key(x_api_key)
    return {"data": query_table('reddit_trending', limit)}

@app.get("/hn/trending")
def get_hn_trending(limit: int = 20, x_api_key: str = Header(...)):
    check_api_key(x_api_key)
    return {"data": query_table('hn_trending', limit)}

@app.get("/newsapi/trending")
def get_newsapi_trending(limit: int = 20, x_api_key: str = Header(...)):
    check_api_key(x_api_key)
    conn = sqlite3.connect('trending_data.db')
    c = conn.cursor()
    c.execute('SELECT source, title, url, published_at FROM news_trending ORDER BY published_at DESC LIMIT ?', (limit,))
    results = [
        {"source": row[0], "title": row[1], "url": row[2], "published_at": row[3]}
        for row in c.fetchall()
    ]
    conn.close()
    return {"data": results}

@app.get("/reddit/trending/csv")
def get_reddit_trending_csv(limit: int = 20, x_api_key: str = Header(...)):
    check_api_key(x_api_key)
    conn = sqlite3.connect('trending_data.db')
    df = pd.read_sql_query('SELECT * FROM reddit_trending ORDER BY score DESC LIMIT ?', conn, params=(limit,))
    conn.close()
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)
    return StreamingResponse(stream, media_type="text/csv")