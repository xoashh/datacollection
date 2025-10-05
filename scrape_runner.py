from fastapi import FastAPI, Depends, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, HttpUrl
from typing import List
from datetime import date
import requests
from bs4 import BeautifulSoup
from scrape.ebay import scrape_ebay_products
from scrape.realestate import scrape_craigslist_homes


# -----------------------------
# ✅ API Key Setup
# -----------------------------
API_KEYS = {"secret-api-key-1"}
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return x_api_key

# -----------------------------
# ✅ FastAPI App
# -----------------------------
app = FastAPI(
    title="Scraped Jobs Data API",
    version="1.0.0",
    description="Real-time job listings scraped from RemoteOK",
    openapi_tags=[{"name": "Jobs", "description": "Get job data"}]
)

# ✅ Add security scheme to OpenAPI for Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": API_KEY_NAME
        }
    }
    openapi_schema["security"] = [{"apiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# -----------------------------
# ✅ Pydantic Models
# -----------------------------
class JobListing(BaseModel):
    title: str
    company: str
    location: str
    postedDate: str
    url: HttpUrl

class JobSearchResponse(BaseModel):
    results: List[JobListing]
    totalResults: int

# -----------------------------
# ✅ Scraper Function
# -----------------------------
def scrape_remoteok_jobs(query: str):
    url = f"https://remoteok.com/remote-{query}-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch jobs")

    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []

    for job_card in soup.find_all("tr", class_="job"):
        title = job_card.find("h2", {"itemprop": "title"})
        company = job_card.find("h3", {"itemprop": "name"})
        link = job_card.get("data-href")

        if title and company and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip(),
                "location": "Remote",
                "postedDate": str(date.today()),
                "url": f"https://remoteok.com{link}"
            })

    return jobs

# -----------------------------
# ✅ /jobs Endpoint
# -----------------------------
@app.get("/jobs", response_model=JobSearchResponse, tags=["Jobs"])
async def get_job_listings(
    query: str = Query(..., description="Job title or keywords (e.g. 'python')"),
    location: str = Query(..., description="Location (not used for RemoteOK)"),
    page: int = Query(1, description="Page number (unused)"),
    api_key: str = Depends(verify_api_key)
):
    listings = scrape_remoteok_jobs(query.lower().replace(" ", "-"))
    return {
        "results": listings[:5],
        "totalResults": len(listings)
    }
# ebay endpoint

@app.get("/products", tags=["Products"])
async def get_products(
    query: str = Query(..., description="Product search term"),
    api_key: str = Depends(verify_api_key)
):
    products = scrape_ebay_products(query)
    return {
        "results": products,
        "totalResults": len(products)
    }

# real estate endpoint 

@app.get("/realestate", tags=["Real Estate"])
async def get_real_estate_listings(
    city: str = Query("newyork", description="Craigslist city (e.g., 'newyork', 'sfbay', 'losangeles')"),
    query: str = Query("apartment", description="Search term (e.g., 'house', 'duplex')"),
    api_key: str = Depends(verify_api_key)
):
    listings = scrape_craigslist_homes(city, query)
    return {
        "results": listings,
        "totalResults": len(listings)
    }

# -----------------------------
# ✅ Error Handler
# -----------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
	
