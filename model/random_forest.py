"""Random Forest forecaster — same windowed framing as the linear baseline,
but uses an ensemble of trees so it can capture non-linear patterns.
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestRegressor

WINDOW = 10


def _make_dataset(prices: np.ndarray, window: int = WINDOW):
    X, y = [], []
    for i in range(len(prices) - window):
        X.append(prices[i : i + window])
        y.append(prices[i + window])
    return np.array(X), np.array(y)


def train_rf(prices: np.ndarray):
    if len(prices) < WINDOW + 5:
        raise ValueError("Not enough history to train Random Forest. Try a longer period.")

    X, y = _make_dataset(prices)
    split = max(int(len(X) * 0.8), 1)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    train_score = float(model.score(X_train, y_train))
    test_score = float(model.score(X_test, y_test)) if len(X_test) else train_score
    return model, train_score, test_score


def predict_rf(model, prices: np.ndarray, days: int):
    history = list(prices[-WINDOW:].astype(float))
    preds = []
    for _ in range(days):
        x = np.array(history[-WINDOW:]).reshape(1, -1)
        p = float(model.predict(x)[0])
        preds.append(p)
        history.append(p)
    return preds
