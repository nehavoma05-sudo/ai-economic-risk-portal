"""Fetch the latest policy repo rate from the Reserve Bank of India."""

from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup


# RBI publishes its current policy rates on its official homepage.
RBI_CURRENT_RATES_URL = "https://www.rbi.org.in/"

# A browser-like user agent helps RBI return its normal public HTML page.
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
}

# Limit the wait so a slow RBI response does not block an API indefinitely.
REQUEST_TIMEOUT_SECONDS = 15


def _extract_rate_from_text(text):
    """Extract one numeric value following the exact Policy Repo Rate label."""
    if not text:
        return None

    # Normalize whitespace because RBI pages may contain line breaks or
    # non-breaking spaces between the rate label and its numeric value.
    normalized_text = " ".join(text.replace("\xa0", " ").split())

    # Match only "Policy Repo Rate" to avoid reverse repo or other policy rates.
    match = re.search(
        r"\bPolicy\s+Repo\s+Rate\b\s*(?::|-)?\s*(\d+(?:\.\d+)?)\s*%",
        normalized_text,
        flags=re.IGNORECASE,
    )

    if match is None:
        return None

    try:
        return float(match.group(1))
    except (TypeError, ValueError):
        return None

def _extract_repo_rate(soup):
    """Find the latest policy repo rate in RBI's parsed HTML."""
    # First inspect table rows because RBI commonly displays current rates in
    # a table. Looking at one row at a time reduces the chance of matching a
    # nearby value that belongs to a different policy rate.
    for row in soup.find_all("tr"):
        row_text = row.get_text(" ", strip=True)
        if re.search(r"\bPolicy\s+Repo\s+Rate\b", row_text, re.IGNORECASE):
            rate = _extract_rate_from_text(row_text)
            if rate is not None:
                return rate

    # If RBI changes the table markup, search the complete visible page text
    # while retaining the same strict "Policy Repo Rate" label requirement.
    page_text = soup.get_text(" ", strip=True)
    return _extract_rate_from_text(page_text)


def fetch_repo_rate():
    """Return the latest RBI policy repo rate as a JSON-serializable dict."""
    try:
        # Download the current rates page directly from RBI.
        response = requests.get(
            RBI_CURRENT_RATES_URL,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        # Treat HTTP failures such as 403 or 500 as fetch errors.
        response.raise_for_status()

        # Parse the returned HTML so the rate can be extracted by its label.
        soup = BeautifulSoup(response.text, "html.parser")
        repo_rate = _extract_repo_rate(soup)

        # A successful HTTP response may still lack usable rate data.
        if repo_rate is None:
            raise ValueError("Policy Repo Rate was not found on the RBI page")

        # Create the timestamp only after a valid, dynamically extracted value
        # has been found.
        return {
            "repo_rate": round(repo_rate, 2),
            "source": "RBI",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except (requests.RequestException, ValueError, TypeError):
        # Return a stable fallback for network, HTML, and conversion failures.
        return {
            "repo_rate": None,
            "source": "RBI",
            "error": "Unable to fetch repo rate",
        }


# Allow this module to be run directly for a simple manual test.
if __name__ == "__main__":
    print(fetch_repo_rate())