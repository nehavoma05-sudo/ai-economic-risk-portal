import os

import mysql.connector

def insert_yesterday_averages():
    conn = mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        port=int(os.getenv("MYSQLPORT")),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )

    cursor = conn.cursor()

    query = """
    INSERT INTO daily_average_scores (
        avg_war_score,
        avg_shipping_score,
        avg_oil_price,
        avg_usd_inr,
        score_date
    )
    SELECT
        AVG(war_score),
        AVG(shipping_score),
        AVG(oil_price),
        AVG(usd_inr),
        DATE(created_at)
    FROM live_scores
    WHERE DATE(created_at) = CURDATE() - INTERVAL 1 DAY
    GROUP BY DATE(created_at);
    """

    cursor.execute(query)

    conn.commit()

    print(f"{cursor.rowcount} row inserted")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    insert_yesterday_averages()