from datetime import datetime, timezone
import json

import mysql.connector
import yfinance as yf
import sys
import os
from dotenv import load_dotenv

load_dotenv()

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from repo_rate.repoRate import fetch_repo_rate

SYMBOLS = {
    "nifty_50_price": "^NSEI",
    "sensex_price": "^BSESN",
    "india_vix": "^INDIAVIX",
    "usd_inr": "INR=X",
    "crude_oil_price": "CL=F",
    "gold_price": "GC=F",
}

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "port": int(os.getenv("MYSQLPORT", "3306")),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),             
    "database": os.getenv("MYSQLDATABASE", ""),
}


data=fetch_repo_rate()
REPO_RATE = data["repo_rate"]
INFLATION = 3.48


from war_score.cal_war_score import calculate_war_score
from shiping_score.cal_ship_score import calculate_shipping_score
from new_sentiment.fetch_news import calculate_news_sentiment_score


def _latest_close(symbol):
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="5d", interval="15m")

    if history.empty or "Close" not in history:
        return None

    latest_close = history["Close"].dropna()
    if latest_close.empty:
        return None

    return round(float(latest_close.iloc[-1]), 2)


def _calculate_return(latest_close, old_close):
    if old_close is None or old_close == 0:
        return None

    return round(((latest_close - old_close) / old_close) * 100, 2)


def calculate_market_returns():
    returns = {
        "nifty_daily_return": None,
        "nifty_7_day_return": None,
        "nifty_30_day_return": None,
    }

    try:
        ticker = yf.Ticker("^NSEI")
        history = ticker.history(period="35d", interval="1d")
    except Exception:
        return returns

    if history.empty or "Close" not in history:
        return returns

    closes = history["Close"].dropna()
    if closes.empty:
        return returns

    latest_close = float(closes.iloc[-1])

    if len(closes) >= 2:
        returns["nifty_daily_return"] = _calculate_return(
            latest_close, float(closes.iloc[-2])
        )

    if len(closes) >= 8:
        returns["nifty_7_day_return"] = _calculate_return(
            latest_close, float(closes.iloc[-8])
        )

    if len(closes) >= 31:
        returns["nifty_30_day_return"] = _calculate_return(
            latest_close, float(closes.iloc[-31])
        )

    return returns


def extract_score(result, key):
    try:
        if isinstance(result, str):
            result = json.loads(result)

        if isinstance(result, list):
            if len(result) == 0:
                return None
            result = result[0]

        if isinstance(result, dict):
            if key in result:
                return result[key]

            if "data" in result and isinstance(result["data"], list):
                if len(result["data"]) > 0:
                    first_row = result["data"][0]
                    if isinstance(first_row, dict):
                        return first_row.get(key)

            if "result" in result and isinstance(result["result"], list):
                if len(result["result"]) > 0:
                    first_row = result["result"][0]
                    if isinstance(first_row, dict):
                        return first_row.get(key)

        return None

    except Exception:
        return None


def get_war_score():
    try:
        result = calculate_war_score()
        return extract_score(result, "war_score")
    except Exception:
        return None


def get_shipping_score():
    try:
        result = calculate_shipping_score()
        return extract_score(result, "shipping_score")
    except Exception:
        return None


def get_news_sentiment():
    try:
        result = calculate_news_sentiment_score()
        return extract_score(result, "news_sentiment")
    except Exception:
        return None


def get_latest_fii_dii_flow():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT fii_dii_flow
            FROM fii_dii_data
            ORDER BY trade_date DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if row is None:
            return None

        return round(float(row[0]), 2)

    except Exception:
        return None


def fetch_latest_market_data():
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    for key, symbol in SYMBOLS.items():
        try:
            data[key] = _latest_close(symbol)
        except Exception:
            data[key] = None

    data.update(calculate_market_returns())

    data["fii_dii_flow"] = get_latest_fii_dii_flow()
    data["repo_rate"] = REPO_RATE
    data["inflation"] = INFLATION
    data["war_score"] = get_war_score()
    data["shipping_score"] = get_shipping_score()
    data["news_sentiment"] = get_news_sentiment()

    return data


if __name__ == "__main__":
    result = fetch_latest_market_data()
    print(json.dumps(result, indent=4))