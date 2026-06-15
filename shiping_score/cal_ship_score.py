import datetime
import os
from datetime import timedelta

import requests
from dotenv import load_dotenv
load_dotenv()

def fetch_shipping_news():
    # Import dependencies inside the function so this feature is self-contained.
   

    # Load environment variables from .env and read the NewsAPI key.
    api_key = os.getenv("API_KEY")
    if not api_key:
        return []

    # Build the 48-hour time window in UTC for the NewsAPI query.
    from_time = (
    datetime.datetime.now(datetime.timezone.utc) - timedelta(hours=48)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Search for shipping and trade route disruption related news.
    query = (
        '("Red Sea" OR Hormuz OR "Suez Canal" OR "oil tanker" OR shipping '
        "OR freight OR vessel) AND (attack OR missile OR drone OR disruption "
        "OR delay OR reroute OR blockade OR congestion)"
    )

    seen_urls = set()
    shipping_news = []
    total_results = 0

    try:
        # Fetch up to 3 pages and combine their articles.
        for page in range(1, 2):
            params = {
                "q": query,
                "from": from_time,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 100,
                "page": page,
                "apiKey": api_key,
            }

            # Send the request and fail safely on HTTP or network errors.
            response = requests.get(
                "https://newsapi.org/v2/everything", params=params, timeout=10
            )
            response.raise_for_status()
            payload = response.json()

            # Capture the total result count reported by NewsAPI.
            total_results = payload.get("totalResults", total_results)

            # Extract articles only when the API returns the expected list shape.
            articles = payload.get("articles", [])
            if not isinstance(articles, list):
                continue

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
                shipping_news.append(
                    {
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "publishedAt": article.get("publishedAt"),
                        "url": url,
                    }
                )
    except Exception:
        return []

    # Print a short fetch summary for visibility.
    print(f"Number of articles fetched: {len(shipping_news)}")
    print(f"Total results from API: {total_results}")

    return shipping_news

def calculate_shipping_score():
    news_articles = fetch_shipping_news()
    # Return the default low disruption score when there are no articles.
    if not news_articles:
        return {
            "shipping_score": 0.10,
            "positive_hits": 0,
            "negative_hits": 0,
            "articles_analyzed": 0,
        }

    # Keywords that increase the shipping disruption score.
    positive_keywords = {
        "red sea": 0.15,
        "hormuz": 0.15,
        "suez canal": 0.12,
        "shipping": 0.08,
        "oil tanker": 0.15,
        "container ship": 0.10,
        "vessel": 0.08,
        "freight": 0.08,
        "port congestion": 0.12,
        "route disruption": 0.15,
        "supply chain": 0.10,
        "blockade": 0.18,
        "attack": 0.15,
        "missile": 0.12,
        "drone": 0.10,
        "piracy": 0.15,
        "reroute": 0.12,
        "delayed shipment": 0.10,
    }

    # Keywords that reduce the shipping disruption score.
    negative_keywords = {
        "normal operations": -0.15,
        "resumed": -0.12,
        "reopened": -0.15,
        "ceasefire": -0.10,
        "de-escalation": -0.10,
        "stable": -0.08,
    }

    base_score = 0.10
    keyword_score = 0
    positive_hits = 0
    negative_hits = 0
    articles_analyzed = len(news_articles)

    for article in news_articles:
        # Combine title and description so both fields are checked.
        title = article.get("title") or ""
        description = article.get("description") or ""
        article_text = f"{title} {description}".lower()

        # Add score for each positive disruption keyword found.
        for keyword, weight in positive_keywords.items():
            if keyword in article_text:
                keyword_score += weight
                positive_hits += 1

        # Subtract score for each calming or recovery keyword found.
        for keyword, weight in negative_keywords.items():
            if keyword in article_text:
                keyword_score += weight
                negative_hits += 1

    # Add an intensity bonus when many disruption signals appear.
    if positive_hits > 40:
        keyword_score += 0.20
    elif positive_hits > 20:
        keyword_score += 0.10

    # Average keyword impact across articles, then scale the result.
    score = base_score + (keyword_score / max(1, articles_analyzed))
    score = score * 3

    # Clamp the final score between 0 and 1.
    score = max(0, min(score, 1))

    return {
        "shipping_score": round(score, 2),
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
        "articles_analyzed": articles_analyzed,
    }

if __name__ == "__main__":
    shipping_score_data = calculate_shipping_score()
    print(shipping_score_data)