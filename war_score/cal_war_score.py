import datetime
import os

def fetch_middle_east_news():
    # Import dependencies inside the function so this feature is self-contained.
    import os
    from datetime import timedelta

    import requests
    from dotenv import load_dotenv

    # Load environment variables from .env and read the NewsAPI key.
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        return []

    # Build the 24-hour time window in UTC for the NewsAPI query.
    from_time = (
    datetime.datetime.now(datetime.timezone.utc) - timedelta(hours=48)
).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Search for Middle East conflict related news using the requested terms.
    query = (
        "Iran OR Israel OR Middle East OR Hormuz OR oil tanker OR missile "
        "OR attack OR ceasefire"
    )

    # Configure the NewsAPI /v2/everything endpoint with the requested filters.
    params = {
        "q": query,
        "from": from_time,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": api_key,
    }

    try:
        # Send the request and fail safely on HTTP or network errors.
        response = requests.get(
            "https://newsapi.org/v2/everything", params=params, timeout=10
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return []

    # Extract articles only when the API returns the expected list shape.
    articles = payload.get("articles", [])
    if not isinstance(articles, list):
        return []

    seen_urls = set()
    news_items = []

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
        news_items.append(
            {
                "title": article.get("title"),
                "description": article.get("description"),
                "publishedAt": article.get("publishedAt"),
                "url": url,
            }
        )
    return news_items

def calculate_war_score():
    news_articles=fetch_middle_east_news()
    # Return the default low tension score when there are no articles to analyze.
    if not news_articles:
        return {
            "war_score": 0.10,
            "positive_hits": 0,
            "negative_hits": 0,
            "articles_analyzed": 0,
        }

    # Keywords that increase the geopolitical tension score.
    positive_keywords = {
        "war": 0.20,
        "missile": 0.10,
        "attack": 0.15,
        "airstrike": 0.15,
        "explosion": 0.12,
        "drone": 0.08,
        "military": 0.08,
        "troops": 0.10,
        "conflict": 0.10,
        "oil tanker": 0.15,
        "hormuz": 0.12,
        "retaliation": 0.10,
        "sanctions": 0.05,
    }

    # Keywords that reduce the geopolitical tension score.
    negative_keywords = {
        "ceasefire": -0.20,
        "peace talks": -0.15,
        "agreement": -0.10,
        "de-escalation": -0.15,
        "diplomatic": -0.08,
        "negotiation": -0.08,
    }

    base_score = 0.10
    keyword_score = 0
    positive_hits = 0
    negative_hits = 0
    articles_analyzed = len(news_articles)

    for article in news_articles:
        # Combine title and description so both fields contribute to the score.
        title = article.get("title") or ""
        description = article.get("description") or ""
        article_text = f"{title} {description}".lower()

        # Add score for each positive keyword found in the article text.
        for keyword, weight in positive_keywords.items():
            if keyword in article_text:
                keyword_score += weight
                positive_hits += 1

        # Subtract score for each negative keyword found in the article text.
        for keyword, weight in negative_keywords.items():
            if keyword in article_text:
                keyword_score += weight
                negative_hits += 1

    # Add an intensity bonus when many positive signals appear across articles.
    if positive_hits > 40:
        keyword_score += 0.20
    elif positive_hits > 20:
        keyword_score += 0.10

    # Apply damping so a large number of articles does not create a huge score.
    score = base_score + (keyword_score / max(1, articles_analyzed))
    score = score * 3

    # Clamp the final score between 0 and 1.
    if score < 0:
        score = 0
    if score > 1:
        score = 1

    return {
        "war_score": round(score, 2),
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
        "articles_analyzed": articles_analyzed,
    }

if __name__ == "__main__":
    war_score_data = calculate_war_score()
    print(war_score_data)