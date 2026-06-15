import os
import logging
import mysql.connector
import yfinance as yf
from dotenv import load_dotenv
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from war_score.cal_war_score import calculate_war_score
from shiping_score.cal_ship_score import calculate_shipping_score

load_dotenv()

logging.basicConfig(level=logging.INFO)


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        port=int(os.getenv("MYSQLPORT")),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )
    


def create_live_scores_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS live_scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            war_score FLOAT NOT NULL,
            shipping_score FLOAT NOT NULL,
            oil_price FLOAT,
            usd_inr FLOAT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_live_scores_created_at (created_at)
        )
        """
    )

    conn.commit()
    cursor.close()
    conn.close()

    logging.info("live_scores table ready")


def get_latest_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d", interval="15m")

        if data.empty:
            data = yf.Ticker(ticker).history(period="5d", interval="1d")

        if data.empty:
            return None

        return float(data["Close"].dropna().iloc[-1])

    except Exception as e:
        logging.error(f"Error fetching {ticker}: {e}")
        return None


def get_latest_oil_price():
    return get_latest_price("CL=F")


def get_latest_usd_inr():
    return get_latest_price("INR=X")


def save_live_scores():
    conn = None
    cursor = None

    try:
        
        data=calculate_war_score()
        war_score = data["war_score"]
        data2=calculate_shipping_score()
        shipping_score = data2["shipping_score"]
        oil_price = get_latest_oil_price()
        usd_inr = get_latest_usd_inr()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO live_scores
            (war_score, shipping_score, oil_price, usd_inr)
            VALUES (%s, %s, %s, %s)
            """,
            (war_score, shipping_score, oil_price, usd_inr)
        )

        conn.commit()

        result = {
            "war_score": war_score,
            "shipping_score": shipping_score,
            "oil_price": oil_price,
            "usd_inr": usd_inr,
            "saved": True
        }

        logging.info("Live scores saved successfully")
        logging.info(result)

        return result

    except Exception as e:
        if conn:
            conn.rollback()

        logging.error(f"Failed to save live scores: {e}")

        return {
            "saved": False,
            "error": str(e)
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    create_live_scores_table()
    save_live_scores()