from datetime import datetime, timedelta, timezone
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def fetch_middle_east_war_news():
    from_time = (
        datetime.now(timezone.utc) - timedelta(hours=72)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    query = (
        '(Iran OR Israel OR Gaza OR Hamas OR Hezbollah OR "Red Sea" OR Hormuz) '
        'AND '
        '(attack OR missile OR drone OR strike OR bombing OR military OR conflict OR war OR ceasefire)'
    )

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "from": from_time,
        "searchIn": "title",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if data.get("status") != "ok":
            return {"error": data.get("message", "Unknown error")}

        seen_urls = set()
        titles = []

        for article in data.get("articles", []):
            article_url = article.get("url")

            if not article_url or article_url in seen_urls:
                continue

            seen_urls.add(article_url)

            title = article.get("title")
            if title:
                titles.append(title)

        return {
            "titles": titles
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import json
    print(json.dumps(fetch_middle_east_war_news(), indent=2))