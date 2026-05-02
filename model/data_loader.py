"""Fetch and preprocess historical stock data via yfinance."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

VALID_PERIODS = {"1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}


def _normalize_symbol(symbol: str) -> str:
    if not symbol or not symbol.strip():
        raise ValueError("Stock symbol must be non-empty")
    return symbol.strip().upper()


def _download(symbol: str, period: str) -> pd.DataFrame:
    """Pull OHLCV history from yfinance. Returns a cleaned DataFrame indexed by Date."""
    if period not in VALID_PERIODS:
        period = "1y"

    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, auto_adjust=True)

    if df is None or df.empty:
        raise ValueError(f"No data found for symbol '{symbol}'. Check the ticker.")

    # Drop rows with missing closes; forward-fill the rest so feature engineering
    # downstream doesn't trip on NaNs.
    df = df.dropna(subset=["Close"]).ffill()
    if df.empty:
        raise ValueError(f"No usable rows after cleaning for symbol '{symbol}'.")

    # yfinance returns a tz-aware DatetimeIndex; strip tz so date arithmetic is simple.
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df


def fetch_stock_data_df(symbol: str, period: str = "1y") -> pd.DataFrame:
    """Internal helper used by the ML predictor — returns a DataFrame."""
    return _download(_normalize_symbol(symbol), period)


def fetch_stock_data(symbol: str, period: str = "1y") -> dict:
    """Public API shape: return JSON-serializable dict for /get-stock-data."""
    symbol = _normalize_symbol(symbol)
    df = _download(symbol, period)

    df_out = df.reset_index().rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    df_out["date"] = pd.to_datetime(df_out["date"]).dt.strftime("%Y-%m-%d")

    prices = [
        {
            "date": row["date"],
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
            "volume": int(row["volume"]) if not pd.isna(row["volume"]) else 0,
        }
        for _, row in df_out.iterrows()
    ]

    current = float(df["Close"].iloc[-1])
    first = float(df["Close"].iloc[0])
    pct = ((current - first) / first) * 100 if first else 0.0

    return {
        "symbol": symbol,
        "period": period,
        "prices": prices,
        "current_price": round(current, 2),
        "percent_change": round(pct, 2),
        "start_date": prices[0]["date"],
        "end_date": prices[-1]["date"],
    }
