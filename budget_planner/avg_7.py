import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "port": int(os.getenv("MYSQLPORT", "3306")),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),             
    "database": os.getenv("MYSQLDATABASE", ""),
    }

# Most recent day gets 0.30 weight, then previous days get lower weights
WEIGHTS = [0.30, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05]


def calculate_weighted_average(rows, column_name):
    values_with_weights = []

    for index, row in enumerate(rows):
        value = row[column_name]

        if value is not None:
            weight = WEIGHTS[index]
            values_with_weights.append((float(value), weight))

    if not values_with_weights:
        return None

    total_weight = sum(weight for _, weight in values_with_weights)

    return sum(value * weight for value, weight in values_with_weights) / total_weight


def get_7_day_weighted_scores():
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                score_date,
                avg_war_score,
                avg_shipping_score,
                avg_oil_price,
                avg_usd_inr
            FROM daily_average_scores
            ORDER BY score_date DESC
            LIMIT 7
            """
        )

        rows = cursor.fetchall()

        if not rows:
            return {
                "weighted_war_score": None,
                "weighted_shipping_score": None,
                "weighted_oil_price": None,
                "weighted_usd_inr": None,
                "days_used": 0,
            }

        return {
            "weighted_war_score": round(
                calculate_weighted_average(rows, "avg_war_score"), 4
            ),
            "weighted_shipping_score": round(
                calculate_weighted_average(rows, "avg_shipping_score"), 4
            ),
            "weighted_oil_price": round(
                calculate_weighted_average(rows, "avg_oil_price"), 4
            ),
            "weighted_usd_inr": round(
                calculate_weighted_average(rows, "avg_usd_inr"), 4
            ),
            "days_used": len(rows),
            "latest_score_date": str(rows[0]["score_date"]),
        }

    except Error as error:
        print(f"Error calculating weighted scores: {error}")
        return {
            "weighted_war_score": None,
            "weighted_shipping_score": None,
            "weighted_oil_price": None,
            "weighted_usd_inr": None,
            "error": str(error),
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    result = get_7_day_weighted_scores()
    print(result)