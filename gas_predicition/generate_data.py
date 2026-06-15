import random

import numpy as np
import pandas as pd


RANDOM_SEED = 42
ROW_COUNT = 5000
OUTPUT_FILE = "india_middle_east_war_impact_5000.csv"


def clip(value, low, high):
    return float(np.clip(value, low, high))


def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    start_date = pd.Timestamp("2024-01-01")
    end_date = pd.Timestamp("2026-05-28")
    date_range_days = (end_date - start_date).days

    seed_rows = pd.DataFrame(
        [
            ["2026-03-05", 0.62, 82.4, 89.10, 0.48, 138500, 2.8, 3.1, 18, -0.9, 5.9],
            ["2026-03-18", 0.71, 91.7, 91.85, 0.57, 143200, 4.6, 5.2, 30, -1.8, 6.4],
            ["2026-04-02", 0.79, 101.3, 93.40, 0.66, 147850, 5.8, 6.7, 42, -2.6, 6.9],
            ["2026-04-21", 0.87, 112.8, 95.05, 0.78, 152400, 7.1, 8.6, 54, -3.7, 7.5],
            ["2026-05-28", 0.93, 120.6, 96.18, 0.89, 156550, 7.5, 9.2, 60, -4.5, 8.1],
        ],
        columns=[
            "date",
            "war_score",
            "oil_price",
            "usd_inr",
            "shipping_score",
            "gold_price",
            "petrol_rise",
            "diesel_rise",
            "lpg_rise",
            "rupee_change",
            "inflation",
        ],
    )
    seed_rows["date"] = pd.to_datetime(seed_rows["date"])

    rows = []
    synthetic_count = ROW_COUNT - len(seed_rows)

    for _ in range(synthetic_count):
        date = start_date + pd.Timedelta(days=random.randint(0, date_range_days))
        progress = (date - start_date).days / date_range_days

        # War pressure gradually rises into 2026, with daily randomness and occasional spikes.
        base_war_score = 0.12 + 0.52 * progress + np.random.normal(0, 0.11)
        if date >= pd.Timestamp("2026-03-01"):
            base_war_score += 0.19 + np.random.beta(2.5, 5.0) * 0.18
        elif random.random() < 0.08:
            base_war_score += np.random.uniform(0.08, 0.24)
        war_score = clip(base_war_score, 0.01, 0.99)

        shipping_score = clip(
            0.12 + 0.68 * war_score + 0.08 * progress + np.random.normal(0, 0.07),
            0.01,
            0.99,
        )

        usd_inr = clip(
            82.1 + 7.2 * progress + 6.6 * war_score + np.random.normal(0, 1.05),
            80.0,
            98.8,
        )

        oil_price = clip(
            68.0 + 34.0 * war_score + 9.0 * shipping_score + 4.2 * progress + np.random.normal(0, 4.1),
            55.0,
            132.0,
        )

        gold_price = clip(
            109500
            + 33000 * war_score
            + 11500 * progress
            + 520 * (usd_inr - 83)
            + np.random.normal(0, 2300),
            95000,
            165000,
        )

        petrol_rise = clip(
            -2.0 + 0.063 * (oil_price - 60) + 0.12 * (usd_inr - 82) + 1.9 * war_score + np.random.normal(0, 0.55),
            0.0,
            11.5,
        )
        diesel_rise = clip(
            -2.4 + 0.072 * (oil_price - 60) + 0.13 * (usd_inr - 82) + 2.1 * war_score + np.random.normal(0, 0.65),
            0.0,
            13.0,
        )
        lpg_rise = clip(
            2.5 + 24.0 * shipping_score + 21.0 * war_score + 0.18 * (oil_price - 70) + np.random.normal(0, 4.5),
            0.0,
            75.0,
        )

        rupee_change = clip(
            0.65 - 0.43 * (usd_inr - 84) - 1.15 * war_score + np.random.normal(0, 0.48),
            -6.5,
            1.5,
        )

        inflation = clip(
            3.5
            + 0.11 * petrol_rise
            + 0.10 * diesel_rise
            + 0.014 * lpg_rise
            + 0.028 * (oil_price - 70)
            + 0.035 * (usd_inr - 82)
            + 0.55 * shipping_score
            + np.random.normal(0, 0.28),
            1.5,
            10.5,
        )

        rows.append(
            {
                "date": date,
                "war_score": round(war_score, 2),
                "oil_price": round(oil_price, 1),
                "usd_inr": round(usd_inr, 2),
                "shipping_score": round(shipping_score, 2),
                "gold_price": int(round(gold_price / 50) * 50),
                "petrol_rise": round(petrol_rise, 1),
                "diesel_rise": round(diesel_rise, 1),
                "lpg_rise": int(round(lpg_rise)),
                "rupee_change": round(rupee_change, 1),
                "inflation": round(inflation, 1),
            }
        )

    synthetic_rows = pd.DataFrame(rows)
    dataset = pd.concat([seed_rows, synthetic_rows], ignore_index=True)
    dataset = dataset.sort_values("date").reset_index(drop=True)

    dataset["date"] = dataset["date"].dt.strftime("%Y-%m-%d")
    dataset.to_csv(OUTPUT_FILE, index=False)
    print(f"Generated {len(dataset)} rows and saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()