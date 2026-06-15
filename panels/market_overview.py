from datetime import timedelta
import math
import json
import yfinance as yf


MARKET_INDICES = [
    {"name": "NIFTY 50", "symbol": "^NSEI"},
    {"name": "SENSEX", "symbol": "^BSESN"},
    {"name": "Bank Nifty", "symbol": "^NSEBANK"},
    {"name": "India VIX", "symbol": "^INDIAVIX"},
    {"name": "NIFTY IT", "symbol": "^CNXIT"},
    {"name": "NIFTY Pharma", "symbol": "^CNXPHARMA"},
    {"name": "NIFTY Auto", "symbol": "^CNXAUTO"},
]


def _to_number(value):
    """Convert a value to a finite float or return None."""
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _percentage_change(current_value, previous_value):
    """Calculate a rounded percentage change without dividing by zero."""
    current_value = _to_number(current_value)
    previous_value = _to_number(previous_value)

    if (
        current_value is None
        or previous_value is None
        or previous_value == 0
    ):
        return None

    change = ((current_value - previous_value) / previous_value) * 100
    return round(change, 2)


def _close_on_or_before(close_prices, target_date):
    """Find the latest available close on or before a calendar date."""
    eligible_prices = close_prices[close_prices.index <= target_date]

    if eligible_prices.empty:
        return None

    return eligible_prices.iloc[-1]


def _empty_index_result(name, symbol):
    """Return a consistent result when an index has no usable data."""
    return {
        "name": name,
        "symbol": symbol,
        "current_value": None,
        "daily_change_percent": None,
        "seven_day_change_percent": None,
        "thirty_day_change_percent": None,
        "last_updated": None,
    }


def _fetch_index_data(name, symbol):
    """Fetch and calculate overview values for one market index."""
    result = _empty_index_result(name, symbol)

    try:
        history = yf.Ticker(symbol).history(period="3mo", interval="1d")

        if history is None or history.empty or "Close" not in history:
            return result

        close_prices = history["Close"].dropna()
        if close_prices.empty:
            return result

        latest_date = close_prices.index[-1]
        latest_close = _to_number(close_prices.iloc[-1])

        result["current_value"] = (
            round(latest_close, 2) if latest_close is not None else None
        )
        result["last_updated"] = latest_date.strftime("%Y-%m-%d %H:%M:%S")

        previous_close = (
            close_prices.iloc[-2] if len(close_prices) >= 2 else None
        )
        seven_day_close = _close_on_or_before(
            close_prices,
            latest_date - timedelta(days=7),
        )
        thirty_day_close = _close_on_or_before(
            close_prices,
            latest_date - timedelta(days=30),
        )

        result["daily_change_percent"] = _percentage_change(
            latest_close,
            previous_close,
        )
        result["seven_day_change_percent"] = _percentage_change(
            latest_close,
            seven_day_close,
        )
        result["thirty_day_change_percent"] = _percentage_change(
            latest_close,
            thirty_day_close,
        )
    except Exception:
        return result

    return result


def fetch_market_overview():
    """Return a JSON-serializable overview of the configured market indices."""
    return [
        _fetch_index_data(index["name"], index["symbol"])
        for index in MARKET_INDICES
    ]

if __name__ == "__main__":
    print(json.dumps(fetch_market_overview(), indent=2))    