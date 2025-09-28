# datacollection
# Trending Data Product

This project scrapes trending stories from Reddit, Hacker News, and NewsAPI, and provides them via a secure FastAPI selling interface.

## Setup

1. Clone the repository and enter the folder.
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Add your API keys to `data_collector.py`.
4. Run the data collector:
    ```
    python data_collector.py
    ```
5. Start the API server:
    ```
    uvicorn selling_api:app --reload
    ```
6. Access endpoints at `http://localhost:8000` (see API_DOCUMENTATION.md).

## Automate Data Collection

Add a cronjob or use Task Scheduler to run `data_collector.py` hourly/daily.

## Add Buyers

- Add buyer API keys to `API_KEYS` in `selling_api.py`.
- Require buyers to use the `X-API-Key` header.

## Deploy

Deploy with Heroku, DigitalOcean, AWS, etc. (see below for more details).
c37b9d0 (Initial commit)
