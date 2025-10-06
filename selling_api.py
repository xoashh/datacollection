from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
import sqlite3
import pandas as pd
import io
import sqlite3
from fastapi import Depends, Header
from data_collector import (
	fetch_and_store_reddit,
	fetch_and_store_hackernews,
	fetch_and_store_newsapi,
)


app = FastAPI()

API_KEYS = {"buyer_secret_key_123": "Client A",
			"another_key_456": "Client B",
			"your_test_key": "Test User"
		}  # Replace with your real keys



def verify_api_key(x_api_key: str = Header(...)):
	if x_api_key not in API_KEYS:
		raise HTTPException(status_code=403, detail="Invalid API Key")
	return x_api_key


@app.post("/scrape/reddit", tags=["data_collector"])
async def trigger_reddit_scrape(api_key: str = Depends(verify_api_key)):
	fetch_and_store_reddit()
	return {"detail": "Reddit trending data updated."}

@app.post("/scrape/hackernews", tags=["data_collector"])
async def trigger_hn_scrape(api_key: str = Depends(verify_api_key)):
	fetch_and_store_hackernews()
	return {"detail": "Hacker News trending data updated."}

@app.post("/scrape/news", tags=["data_collector"])
async def trigger_news_scrape(api_key: str = Depends(verify_api_key)):
	fetch_and_store_newsapi()
	return {"detail": "NewsAPI data updated."}



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
	
@app.get("/data/reddit", tags=["Data"])
async def get_reddit_data(limit: int = 10, api_key: str = Depends(verify_api_key)):
	conn = sqlite3.connect("trending_data.db")
	c = conn.cursor()
	c.execute("""
		SELECT title, url, score, created_utc 
		FROM reddit_trending 
		ORDER BY created_utc DESC 
		LIMIT ?
	""", (limit,))
	rows = c.fetchall()
	conn.close()
	return {"results": [dict(zip(["title", "url", "score", "created_utc"], row)) for row in rows
	
		],
		"totalResults": len(rows)
	}
@app.get("/data/hackernews", tags=["Data"])
async def get_hackernews_data(limit: int = 10, api_key: str = Depends(verify_api_key)):
	conn = sqlite3.connect("trending_data.db")
	c = conn.cursor()
	c.execute("""
		SELECT title, url, score, created_utc 
		FROM hn_trending 
		ORDER BY created_utc DESC 
		LIMIT ?
	""", (limit,))
	rows = c.fetchall()
	conn.close()
	return {
		"results": [
			{"title": r[0], "url": r[1], "score": r[2], "created_utc": r[3]}
			for r in rows
		],
		"totalResults": len(rows)
	}
	
@app.get("/data/news", tags=["Data"])
async def get_newsapi_data(limit: int = 10, api_key: str = Depends(verify_api_key)):
	conn = sqlite3.connect("trending_data.db")
	c = conn.cursor()
	c.execute("""
		SELECT source, title, url, published_at 
		FROM news_trending 
		ORDER BY published_at DESC 
		LIMIT ?
	""", (limit,))
	rows = c.fetchall()
	conn.close()
	return {
		"results": [
			{"source": r[0], "title": r[1], "url": r[2], "published_at": r[3]}
			for r in rows
		],
		"totalResults": len(rows)
	}
	
	from scrapers.twitter_scraper import fetch_twitter_trending
from scrapers.google_trends_scraper import fetch_google_trends
from scrapers.crypto_scraper import fetch_crypto_trending

@app.get("/data/twitter_trends", tags=["Data"])
async def get_twitter_trends(limit: int = 20, api_key: str = Depends(verify_api_key)):
	data = fetch_twitter_trending(limit)
	return {"results": data, "totalResults": len(data)}

@app.get("/data/google_trends", tags=["Data"])
async def get_google_trends(region: str = "united_states", api_key: str = Depends(verify_api_key)):
	data = fetch_google_trends(region)
	return {"region": region, "results": data, "totalResults": len(data)}

@app.get("/data/crypto_trending", tags=["Data"])
async def get_crypto_trending(api_key: str = Depends(verify_api_key)):
	data = fetch_crypto_trending()
	return {"results": data, "totalResults": len(data)}


from fastapi.openapi.utils import get_openapi

def custom_openapi():
	if app.openapi_schema:
		return app.openapi_schema

	openapi_schema = get_openapi(
		title=app.title,
		version="1.0.0",
		description="API for collecting and selling trending data.",
		routes=app.routes,
	)

	openapi_schema["components"]["securitySchemes"] = {
		"apiKeyAuth": {
			"type": "apiKey",
			"in": "header",
			"name": "x-api-key"
		}
	}
	openapi_schema["security"] = [{"apiKeyAuth": []}]
	app.openapi_schema = openapi_schema
	return app.openapi_schema

app.openapi = custom_openapi
