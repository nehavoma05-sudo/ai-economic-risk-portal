from datetime import datetime
from io import StringIO
import os
from dotenv import load_dotenv



import mysql.connector
import pandas as pd
import requests
load_dotenv()

NSE_FII_DII_CSV_URL = "https://www.nseindia.com/api/fiidiiTradeNse?csv=true"

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "port": int(os.getenv("MYSQLPORT", "3306")),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),             
    "database": os.getenv("MYSQLDATABASE", ""),
    }

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/csv,application/csv,text/plain,*/*",
    "Referer": "https://www.nseindia.com/reports/fii-dii",
    "X-Requested-With": "XMLHttpRequest",
}


def create_table(connection):
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fii_dii_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            trade_date DATE UNIQUE,
            fii_buy_value FLOAT,
            fii_sell_value FLOAT,
            fii_net_value FLOAT,
            dii_buy_value FLOAT,
            dii_sell_value FLOAT,
            dii_net_value FLOAT,
            fii_dii_flow FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    cursor.close()


def clean_number(value):
    if pd.isna(value):
        return 0.0

    cleaned_value = str(value).replace(",", "").strip()

    if cleaned_value in ["", "-", "--"]:
        return 0.0

    return float(cleaned_value)


def clean_column_name(column):
    return (
        str(column)
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("ï»¿", "")
        .replace("₹", "")
        .replace("â¹", "")
        .strip()
        .lower()
    )


def parse_latest_fii_dii_row(csv_text):
    csv_text = csv_text.replace("ï»¿", "")

    try:
        dataframe = pd.read_csv(StringIO(csv_text), engine="python")
    except Exception:
        print("Failed to read NSE CSV. First 500 characters:")
        print(csv_text[:500])
        raise

    dataframe = dataframe.dropna(how="all")

    if dataframe.empty:
        raise ValueError("NSE CSV did not contain any rows.")

    dataframe.columns = [clean_column_name(col) for col in dataframe.columns]

    category_col = None
    date_col = None
    buy_col = None
    sell_col = None
    net_col = None

    for col in dataframe.columns:
        if "category" in col:
            category_col = col
        elif "date" in col:
            date_col = col
        elif "buy value" in col:
            buy_col = col
        elif "sell value" in col:
            sell_col = col
        elif "net value" in col:
            net_col = col

    required = {
        "category": category_col,
        "date": date_col,
        "buy": buy_col,
        "sell": sell_col,
        "net": net_col,
    }

    missing = [name for name, col in required.items() if col is None]

    if missing:
        raise ValueError(f"Missing required columns in NSE CSV: {missing}")

    dataframe[date_col] = pd.to_datetime(
        dataframe[date_col], errors="coerce", dayfirst=True
    )

    dataframe = dataframe.dropna(subset=[date_col])

    if dataframe.empty:
        raise ValueError("Could not parse valid trade date from NSE CSV.")

    latest_trade_date = dataframe[date_col].max()
    latest_rows = dataframe[dataframe[date_col] == latest_trade_date]

    categories = latest_rows[category_col].astype(str).str.upper()

    fii_rows = latest_rows[categories.str.contains("FII", na=False)]
    dii_rows = latest_rows[categories.str.contains("DII", na=False)]

    if fii_rows.empty:
        raise ValueError("Could not find FII/FPI row in NSE CSV.")

    if dii_rows.empty:
        raise ValueError("Could not find DII row in NSE CSV.")

    fii_row = fii_rows.iloc[0]
    dii_row = dii_rows.iloc[0]

    fii_buy_value = clean_number(fii_row[buy_col])
    fii_sell_value = clean_number(fii_row[sell_col])
    fii_net_value = clean_number(fii_row[net_col])

    dii_buy_value = clean_number(dii_row[buy_col])
    dii_sell_value = clean_number(dii_row[sell_col])
    dii_net_value = clean_number(dii_row[net_col])

    return {
        "trade_date": latest_trade_date.date(),
        "fii_buy_value": fii_buy_value,
        "fii_sell_value": fii_sell_value,
        "fii_net_value": fii_net_value,
        "dii_buy_value": dii_buy_value,
        "dii_sell_value": dii_sell_value,
        "dii_net_value": dii_net_value,
        "fii_dii_flow": fii_net_value + dii_net_value,
    }


def fetch_csv_from_nse():
    session = requests.Session()
    session.headers.update(HEADERS)

    session.get("https://www.nseindia.com/", timeout=10)

    response = session.get(NSE_FII_DII_CSV_URL, timeout=20)
    response.raise_for_status()

    return response.content.decode("utf-8-sig", errors="replace")


def save_row_to_mysql(row):
    connection = mysql.connector.connect(**DB_CONFIG)

    try:
        create_table(connection)

        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO fii_dii_data (
                trade_date,
                fii_buy_value,
                fii_sell_value,
                fii_net_value,
                dii_buy_value,
                dii_sell_value,
                dii_net_value,
                fii_dii_flow
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                fii_buy_value = VALUES(fii_buy_value),
                fii_sell_value = VALUES(fii_sell_value),
                fii_net_value = VALUES(fii_net_value),
                dii_buy_value = VALUES(dii_buy_value),
                dii_sell_value = VALUES(dii_sell_value),
                dii_net_value = VALUES(dii_net_value),
                fii_dii_flow = VALUES(fii_dii_flow)
            """,
            (
                row["trade_date"],
                row["fii_buy_value"],
                row["fii_sell_value"],
                row["fii_net_value"],
                row["dii_buy_value"],
                row["dii_sell_value"],
                row["dii_net_value"],
                row["fii_dii_flow"],
            ),
        )

        connection.commit()
        cursor.close()

    finally:
        connection.close()


def fetch_and_save_fii_dii():
    try:
        csv_text = fetch_csv_from_nse()
        latest_row = parse_latest_fii_dii_row(csv_text)
        save_row_to_mysql(latest_row)

        print("Saved FII/DII row:")
        print(f"Trade Date: {latest_row['trade_date']}")
        print(f"FII Buy Value: {latest_row['fii_buy_value']}")
        print(f"FII Sell Value: {latest_row['fii_sell_value']}")
        print(f"FII Net Value: {latest_row['fii_net_value']}")
        print(f"DII Buy Value: {latest_row['dii_buy_value']}")
        print(f"DII Sell Value: {latest_row['dii_sell_value']}")
        print(f"DII Net Value: {latest_row['dii_net_value']}")
        print(f"FII/DII Flow: {latest_row['fii_dii_flow']}")
        print(f"Saved At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as error:
        print(f"Failed to fetch and save FII/DII data: {error}")


if __name__ == "__main__":
    fetch_and_save_fii_dii()