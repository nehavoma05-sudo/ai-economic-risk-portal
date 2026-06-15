import datetime
import os
from datetime import timedelta

import requests
from dotenv import load_dotenv
load_dotenv()

def fetch_economic_news():
    # Import dependencies inside the function so this feature is self-contained.
    

    # Load environment variables from .env and read the NewsAPI key.
    api_key =os.getenv("API_KEY")
    if not api_key:
        print("❌ Error: API_KEY not found in environment variables or .env file.")
        return []
    
    # Build the 48-hour time window in UTC for the NewsAPI query.
    from_time = (
    datetime.datetime.now(datetime.timezone.utc) - timedelta(hours=48)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")


    # Search for India economy and market-related news.
    query = (
        '(India OR "Indian economy" OR RBI OR Nifty OR Sensex OR rupee OR INR) '
        'AND '
        '(inflation OR recession OR growth OR slowdown OR recovery '
        'OR "crude oil" OR "oil prices" OR petrol OR diesel '
        'OR "fuel price" OR "interest rate" OR repo rate '
        'OR "USD/INR" OR forex OR currency '
        'OR "stock market" OR crash OR correction OR volatility '
        'OR "FII outflow" OR "FII inflow" OR investment '
        'OR exports OR imports OR trade deficit)'
    )

    seen_urls = set()
    economic_news = []
    total_results = 0

    try:
        # Fetch up to 3 pages and combine their articles.
            params = {
                "q": query,
                "from": from_time,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 100,
                "apiKey": api_key,
            }

            # Send the request and fail safely on HTTP or network errors.
            response = requests.get(
                "https://newsapi.org/v2/everything", params=params, timeout=10
            )
            if response.status_code != 200:
                print(f"❌ API Error ({response.status_code}): {response.json().get('message', '')}")
                return []
            response.raise_for_status()
            payload = response.json()

            # Capture the total result count reported by NewsAPI.
            total_results = payload.get("totalResults", total_results)

            # Extract articles only when the API returns the expected list shape.
            articles = payload.get("articles", [])
            # If the API returns an unexpected shape for articles, treat as empty list.
            if not isinstance(articles, list):
                articles = []

            for article in articles:
                # Skip malformed article entries and articles without a URL.
                if not isinstance(article, dict):
                    continue

                url = article.get("url")
                if not url or url in seen_urls:
                    continue

                # Track URLs to remove duplicate articles from the final result.
                seen_urls.add(url)

                # Keep only the requested article fields.
                economic_news.append(
                    {
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "publishedAt": article.get("publishedAt"),
                        "url": url,
                    }
                )
    except Exception as e:
        print(f"❌ An unexpected exception occurred during fetch: {e}")
        return []

    return economic_news

def calculate_news_sentiment_score():
    news_articles = fetch_economic_news()  
    # Return a neutral sentiment score when there are no articles to analyze.
    if not news_articles:
        return {
            "news_sentiment": 0.00,
            "positive_hits": 0,
            "negative_hits": 0,
            "articles_analyzed": 0,
        }

    # Keywords that increase the economic news sentiment score.
    positive_keywords = {
        "growth": 0.15,
        "recovery": 0.15,
        "surge": 0.12,
        "gain": 0.10,
        "rally": 0.12,
        "strong": 0.10,
        "boost": 0.10,
        "profit": 0.10,
        "increase": 0.08,
        "stable": 0.08,
        "eases": 0.10,
        "cooling inflation": 0.15,
        "rate cut": 0.15,
    }

    # Keywords that decrease the economic news sentiment score.
    negative_keywords = {
        "crash": -0.20,
        "fall": -0.12,
        "decline": -0.12,
        "drop": -0.12,
        "loss": -0.10,
        "recession": -0.20,
        "inflation": -0.12,
        "fuel price hike": -0.18,
        "oil price surge": -0.18,
        "rupee weakens": -0.15,
        "rate hike": -0.15,
        "selloff": -0.18,
        "uncertainty": -0.10,
        "crisis": -0.18,
    }

    sentiment_score = 0.00
    positive_hits = 0
    negative_hits = 0
    articles_analyzed = len(news_articles)

    for article in news_articles:
        # Combine title and description so both fields affect sentiment.
        title = article.get("title") or ""
        description = article.get("description") or ""
        article_text = f"{title} {description}".lower()

        # Add sentiment for each positive keyword found.
        for keyword, weight in positive_keywords.items():
            if keyword in article_text:
                sentiment_score += weight
                positive_hits += 1

        # Subtract sentiment for each negative keyword found.
        for keyword, weight in negative_keywords.items():
            if keyword in article_text:
                sentiment_score += weight
                negative_hits += 1

    # Normalize by article count so more articles do not automatically dominate.
    score = sentiment_score / max(1, articles_analyzed)

    # Amplify the normalized signal slightly.
    score = score * 3

    # Clamp the score between -1 and +1.
    score = max(-1, min(score, 1))

    return {
        "news_sentiment": round(score, 2),
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
        "articles_analyzed": articles_analyzed,
    }

if __name__ == "__main__":
    sentiment_result = calculate_news_sentiment_score()
    print(sentiment_result)  

