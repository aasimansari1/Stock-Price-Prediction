"""Unified prediction entrypoint used by the API.

Picks a model implementation, trains it on the fetched history, rolls it forward
the requested number of business days, and returns a JSON-serializable response
combining historical closes + forecasts + train/test scores.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pandas as pd

from .data_loader import fetch_stock_data_df
from .linear_model import predict_linear, train_linear
from .random_forest import predict_rf, train_rf


def _next_business_days(last_date: pd.Timestamp, days: int) -> list[str]:
    """Return the next `days` weekday dates after last_date as ISO strings.
    Naive — does not account for market holidays, which is fine for a demo."""
    out: list[str] = []
    cur = last_date
    while len(out) < days:
        cur = cur + timedelta(days=1)
        if cur.weekday() < 5:  # Mon-Fri
            out.append(cur.strftime("%Y-%m-%d"))
    return out


def predict_prices(symbol: str, model_name: str, days: int, period: str) -> dict[str, Any]:
    df = fetch_stock_data_df(symbol, period)
    closes = df["Close"].to_numpy(dtype=float)

    if model_name == "linear":
        model, train_score, test_score = train_linear(closes)
        predictions = predict_linear(model, closes, days)
    elif model_name == "random_forest":
        model, train_score, test_score = train_rf(closes)
        predictions = predict_rf(model, closes, days)
    elif model_name == "lstm":
        # Imported lazily so the API can boot even if TensorFlow is slow to import,
        # and so users who only want sklearn models don't pay the TF startup cost.
        from .lstm_model import predict_lstm, train_lstm

        model, scaler, train_score, test_score = train_lstm(closes)
        predictions = predict_lstm(model, scaler, closes, days)
    else:
        raise ValueError(f"Unknown model: {model_name}")

    last_date = pd.Timestamp(df.index[-1])
    future_dates = _next_business_days(last_date, days)

    history = [
        {"date": pd.Timestamp(d).strftime("%Y-%m-%d"), "close": round(float(c), 2)}
        for d, c in zip(df.index, closes)
    ]
    pred_list = [
        {"date": d, "predicted_price": round(float(p), 2)}
        for d, p in zip(future_dates, predictions)
    ]

    current_price = float(closes[-1])
    predicted_last = float(predictions[-1])
    pct = ((predicted_last - current_price) / current_price) * 100 if current_price else 0.0

    return {
        "symbol": symbol.upper(),
        "model": model_name,
        "period": period,
        "history": history,
        "predictions": pred_list,
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_last, 2),
        "percent_change": round(pct, 2),
        "train_score": round(float(train_score), 4),
        "test_score": round(float(test_score), 4),
    }
