from datetime import datetime
import math

import yfinance as yf


COMMODITIES = {
    "gold": "GC=F",
    "silver": "SI=F",
    "crude_oil": "CL=F",
    "natural_gas": "NG=F",
}

USD_INR_SYMBOL = "INR=X"
TROY_OUNCE_TO_GRAMS = 31.1035


def _to_number(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _empty_market_data():
    return {
        "price": None,
        "previous_close": None,
        "change_percent": None,
        "market_direction": "FLAT",
    }


def _calculate_market_data(current_price, previous_close):
    current_price = _to_number(current_price)
    previous_close = _to_number(previous_close)

    if current_price is None or previous_close is None:
        return _empty_market_data()

    change = current_price - previous_close
    change_percent = (change / previous_close) * 100 if previous_close != 0 else None

    if change > 0:
        direction = "UP"
    elif change < 0:
        direction = "DOWN"
    else:
        direction = "FLAT"

    return {
        "price": round(current_price, 2),
        "previous_close": round(previous_close, 2),
        "change_percent": round(change_percent, 2) if change_percent is not None else None,
        "market_direction": direction,
    }


def _fetch_latest_and_previous(symbol):
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="5d", interval="1d")

        if history is None or history.empty or "Close" not in history:
            return None, None

        close_prices = history["Close"].dropna()

        if close_prices.empty:
            return None, None

        current_price = close_prices.iloc[-1]
        previous_close = close_prices.iloc[-2] if len(close_prices) >= 2 else None

        return current_price, previous_close

    except Exception:
        return None, None


def _convert_gold_to_inr_per_10g(gold_usd_oz, usd_inr):
    gold_usd_gram = gold_usd_oz / TROY_OUNCE_TO_GRAMS
    gold_inr_gram = gold_usd_gram * usd_inr
    return gold_inr_gram * 10


def _convert_silver_to_inr_per_kg(silver_usd_oz, usd_inr):
    silver_usd_gram = silver_usd_oz / TROY_OUNCE_TO_GRAMS
    silver_inr_gram = silver_usd_gram * usd_inr
    return silver_inr_gram * 1000


def _fetch_single_commodity(name, symbol, usd_inr_current=None, usd_inr_previous=None):
    current_price, previous_close = _fetch_latest_and_previous(symbol)

    if name == "gold" and usd_inr_current is not None and usd_inr_previous is not None:
        current_price = _convert_gold_to_inr_per_10g(current_price, usd_inr_current)
        previous_close = _convert_gold_to_inr_per_10g(previous_close, usd_inr_previous)

    elif name == "silver" and usd_inr_current is not None and usd_inr_previous is not None:
        current_price = _convert_silver_to_inr_per_kg(current_price, usd_inr_current)
        previous_close = _convert_silver_to_inr_per_kg(previous_close, usd_inr_previous)

    return _calculate_market_data(current_price, previous_close)


def fetch_commodity_market_data():
    market_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    usd_inr_current, usd_inr_previous = _fetch_latest_and_previous(USD_INR_SYMBOL)

    market_data["usd_inr"] = _calculate_market_data(
        usd_inr_current,
        usd_inr_previous
    )

    for commodity_name, symbol in COMMODITIES.items():
        market_data[commodity_name] = _fetch_single_commodity(
            commodity_name,
            symbol,
            usd_inr_current,
            usd_inr_previous
        )

    return market_data


if __name__ == "__main__":
    data = fetch_commodity_market_data()
    print(data)