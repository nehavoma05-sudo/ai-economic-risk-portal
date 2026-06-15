import datetime
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pytz import timezone
import yfinance as yf

from gas_predicition.predict import predict
from stock_predict.fetch_data2 import fetch_latest_market_data
from stock_predict.predict_crash import predict_crash_risk
from panels.commodity_panel import fetch_commodity_market_data
from panels.market_overview import fetch_market_overview
from war_score.cal_war_score import calculate_war_score
from shiping_score.cal_ship_score import calculate_shipping_score
from new_sentiment.fetch_news import calculate_news_sentiment_score
from war_score.fetch_news import fetch_middle_east_war_news
from shiping_score.fetch_news import fetch_middle_east_ship_news
from new_sentiment.news import economic_news
from budget_planner.budget import calculate_budget_plan
from war_score.fetch_news import fetch_middle_east_war_news
from shiping_score.fetch_news import fetch_middle_east_ship_news
from new_sentiment.news import economic_news
app = Flask(__name__)
CORS(app)


def get_latest_price(ticker):
    data = yf.Ticker(ticker).history(period="5d", interval="1d")

    if data.empty:
        raise ValueError(f"No data found for {ticker}")

    return float(data["Close"].dropna().iloc[-1])


@app.get("/")
def home():
    return jsonify({"message": "Economic Impact Prediction API Running"})


@app.post("/predict-economic-impact")
def predict_economic_impact():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must contain valid JSON."}), 400

    missing_fields = [
        field
        for field in ("war_score", "shipping_score")
        if field not in data or data[field] is None
    ]

    if missing_fields:
        return jsonify({
            "error": f"Missing required values: {', '.join(missing_fields)}."
        }), 400

    war_score = data["war_score"]
    shipping_score = data["shipping_score"]

    if (
        isinstance(war_score, bool)
        or isinstance(shipping_score, bool)
        or not isinstance(war_score, (int, float))
        or not isinstance(shipping_score, (int, float))
    ):
        return jsonify({
            "error": "war_score and shipping_score must be numbers."
        }), 400

    if not 0 <= war_score <= 1 or not 0 <= shipping_score <= 1:
        return jsonify({
            "error": "war_score and shipping_score must be between 0 and 1."
        }), 400

    try:
        usd_inr = get_latest_price("INR=X")
        oil_price = get_latest_price("CL=F")
        gold_price = get_latest_price("GC=F")

        sample_input = {
            "war_score": war_score,
            "oil_price": oil_price,
            "usd_inr": usd_inr,
            "shipping_score": shipping_score,
            "gold_price": gold_price,
        }

        result = predict(sample_input)

        return jsonify(result)

    except Exception as e:
        app.logger.exception("Economic impact prediction failed")
        return jsonify({
            "error": "Could not predict economic impact.",
            "details": str(e)
        }), 500
    
@app.route("/stock-crash-warning", methods=["GET"])
def stock_crash_warning():
    try:
        # 1. Fetch latest live market data
        latest_data = fetch_latest_market_data()

        # 2. Predict crash risk
        prediction = predict_crash_risk(latest_data)

        # 3. Send result to frontend
        return jsonify(prediction), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to calculate stock crash warning",
            "details": str(e)
        }), 500
@app.route("/commodities", methods=["GET"])

def commodity_market_data():
    try:
        data = fetch_commodity_market_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
@app.get("/api/market-overview")

def market_overview():
    try:
        data = fetch_market_overview()
        return jsonify({
            "success": True,
            "data": data,
            "message": "Market overview fetched successfully"
        })
    except Exception as error:
        app.logger.exception("Market overview fetch failed")
        return jsonify({
            "success": False,
            "data": [],
            "message": str(error)
        }), 500
@app.route("/economic-overview", methods=["GET"])
def economic_overview():
    try:
        data = fetch_market_overview()
        return jsonify(data)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    

@app.route("/api/live-risk-dashboard", methods=["GET"])
def live_risk_dashboard():
    war_data = calculate_war_score()              # returns score + top articles
    shipping_data = calculate_shipping_score()    # returns score + top articles
    sentiment_data = calculate_news_sentiment_score()   # returns score + top articles

    war_score = war_data.get("war_score", 0)
    shipping_score = shipping_data.get("shipping_score", 0)
    news_sentiment = sentiment_data.get("news_sentiment", 0)

    if war_score >= 0.7 or shipping_score >= 0.7 or news_sentiment <= -0.4:
        risk_level = "HIGH"
    elif war_score >= 0.4 or shipping_score >= 0.4 or news_sentiment <= -0.2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return jsonify({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "war_score": round(war_score, 2),
        "shipping_score": round(shipping_score, 2),
        "news_sentiment": round(news_sentiment, 2),
        "risk_level": risk_level,
        "top_articles": {
            "war": war_data.get("top_articles", [])[:5],
            "shipping": shipping_data.get("top_articles", [])[:5],
            "sentiment": sentiment_data.get("top_articles", [])[:5]
        }
    })

@app.route("/budget-prediction", methods=["POST"])
def budget_plan():
    try:
        user_input = request.get_json()

        if not user_input:
            return jsonify({"error": "No input data received"}), 400

        result = calculate_budget_plan(user_input)

        return jsonify(result), 200

    except Exception as error:
        return jsonify({
            "error": "Unable to calculate budget plan",
            "details": str(error)
        }), 500
    
@app.route("/live-dashboard", methods=["GET"])
def live_dashboard():
    try:
        war_news = fetch_middle_east_war_news()
        war_data = calculate_war_score()
        war_score = war_data.get("war_score", 0)

        shipping_news = fetch_middle_east_ship_news()
        shipping_data = calculate_shipping_score()
        shipping_score = shipping_data.get("shipping_score", 0)

        economy_articles = economic_news()
        sentiment_data = calculate_news_sentiment_score()
        news_sentiment = sentiment_data.get("news_sentiment", 0)

        return jsonify({
        "war_score": round(war_score, 2),
        "war_news": war_news.get("titles", [])[:5],

        "shipping_score": round(shipping_score, 2),
        "shipping_news": shipping_news.get("titles", [])[:5],

        "news_sentiment": round(news_sentiment, 2),
        "economic_news": economy_articles.get("titles", [])[:5]
    })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
     