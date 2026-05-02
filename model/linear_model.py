"""Linear Regression baseline.

Frames forecasting as: given the last `WINDOW` closes, predict the next close.
Simple, fast, and a decent benchmark to compare more complex models against.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LinearRegression

WINDOW = 10


def _make_dataset(prices: np.ndarray, window: int = WINDOW):
    X, y = [], []
    for i in range(len(prices) - window):
        X.append(prices[i : i + window])
        y.append(prices[i + window])
    return np.array(X), np.array(y)


def train_linear(prices: np.ndarray):
    if len(prices) < WINDOW + 5:
        raise ValueError("Not enough history to train Linear Regression. Try a longer period.")

    X, y = _make_dataset(prices)
    split = max(int(len(X) * 0.8), 1)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = LinearRegression()
    model.fit(X_train, y_train)

    train_score = float(model.score(X_train, y_train))
    test_score = float(model.score(X_test, y_test)) if len(X_test) else train_score
    return model, train_score, test_score


def predict_linear(model, prices: np.ndarray, days: int):
    """Roll the model forward one day at a time, feeding predictions back as input."""
    history = list(prices[-WINDOW:].astype(float))
    preds = []
    for _ in range(days):
        x = np.array(history[-WINDOW:]).reshape(1, -1)
        p = float(model.predict(x)[0])
        preds.append(p)
        history.append(p)
    return preds
