#!/usr/bin/env python3
"""
analysis/visualize.py
Part 2 Task 11 — two PNGs under visualizations/.
Requires analysis/clean_and_eda.py to have written data/orders_cleaned.csv.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "visualizations"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    path = DATA / "orders_cleaned.csv"
    if not path.exists():
        raise SystemExit(f"Missing {path}. Run analysis/clean_and_eda.py first.")

    df = pd.read_csv(path)
    df["order_date"] = pd.to_datetime(df["order_date"])

    # 1. return_rate_by_payment.png
    rates = (
        df.groupby("payment_method")["returned"].mean().mul(100).round(1).sort_values(ascending=False)
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(rates.index.astype(str), rates.values, color=["#E45756", "#F58518", "#4C78A8"])
    for bar, val in zip(bars, rates.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val}%", ha="center")
    ax.set_ylabel("Return rate (%)")
    ax.set_xlabel("Payment method")
    ax.set_title("COD Returns at 44.4% — 3x Card")
    ax.set_ylim(0, max(rates.values) * 1.2)
    fig.tight_layout()
    fig.savefig(OUT / "return_rate_by_payment.png", dpi=120)
    plt.close(fig)
    print(f"Wrote {OUT / 'return_rate_by_payment.png'}")

    # 2. monthly_revenue_trend.png — outlier-corrected series
    df["is_outlier"] = df["is_outlier"].astype(bool) if "is_outlier" in df.columns else False
    clean = df.loc[~df["is_outlier"]].copy()
    clean["year_month"] = clean["order_date"].dt.to_period("M").astype(str)
    monthly = clean.groupby("year_month")["order_value"].sum().round(2)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(monthly.index, monthly.values, marker="o", color="#4C78A8")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (INR)")
    ax.set_title("Outlier-corrected monthly revenue — peak: March 2026 (20318.90 INR)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUT / "monthly_revenue_trend.png", dpi=120)
    plt.close(fig)
    print(f"Wrote {OUT / 'monthly_revenue_trend.png'}")


if __name__ == "__main__":
    main()
