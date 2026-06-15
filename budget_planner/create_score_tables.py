import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "port": int(os.getenv("MYSQLPORT", "3306")),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),             
    "database": os.getenv("MYSQLDATABASE", ""),
    }


def create_tables():
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

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

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_average_scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                score_date DATE NOT NULL UNIQUE,
                avg_war_score FLOAT NOT NULL,
                avg_shipping_score FLOAT NOT NULL,
                avg_oil_price FLOAT,
                avg_usd_inr FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_daily_average_scores_score_date (score_date)
            )
            """
        )

        connection.commit()
        print("Tables created successfully")
    except Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        print(f"Error creating tables: {error}")
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    create_tables()