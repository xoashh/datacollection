from pytrends.request import TrendReq

def fetch_google_trends(region="US", limit=10):
    """Fetch top trending search queries from Google Trends."""
    pytrends = TrendReq(hl='en-US', tz=360)
    trending_searches_df = pytrends.trending_searches(pn=region)
    trends = trending_searches_df[0].head(limit).tolist()
    return [{"rank": i + 1, "query": q} for i, q in enumerate(trends)]
