"""LSTM forecaster (TensorFlow / Keras).

Sequence-to-one: feed the last `WINDOW` (scaled) closes through a stacked LSTM
and predict the next scaled close. Predictions are inverse-scaled back to dollars.

Trained on demand per request — kept small (2 layers, ~15 epochs) so a single
prediction call returns in a few seconds on CPU. For production you'd cache
trained models per (symbol, period).
"""

from __future__ import annotations

import os

# Quiet TF logs before importing it.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import numpy as np
from sklearn.metrics import r2_score
from sklearn.preprocessing import MinMaxScaler

import tensorflow as tf  # noqa: E402

# Determinism — close enough for a demo.
tf.random.set_seed(42)
np.random.seed(42)

WINDOW = 30
EPOCHS = 15
BATCH = 16


def _build_model():
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.models import Sequential

    model = Sequential(
        [
            Input(shape=(WINDOW, 1)),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def train_lstm(prices: np.ndarray):
    if len(prices) < WINDOW + 20:
        raise ValueError("Not enough history to train LSTM. Try period=2y or longer.")

    prices = prices.astype(np.float32).reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(prices)

    X, y = [], []
    for i in range(len(scaled) - WINDOW):
        X.append(scaled[i : i + WINDOW])
        y.append(scaled[i + WINDOW])
    X = np.array(X)
    y = np.array(y)

    split = max(int(len(X) * 0.8), 1)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = _build_model()
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH, verbose=0)

    train_pred = model.predict(X_train, verbose=0)
    train_score = float(r2_score(y_train, train_pred))
    if len(X_test):
        test_pred = model.predict(X_test, verbose=0)
        test_score = float(r2_score(y_test, test_pred))
    else:
        test_score = train_score

    return model, scaler, train_score, test_score


def predict_lstm(model, scaler, prices: np.ndarray, days: int):
    prices = prices.astype(np.float32).reshape(-1, 1)
    scaled = scaler.transform(prices)
    history = list(scaled[-WINDOW:].flatten())

    preds_scaled = []
    for _ in range(days):
        x = np.array(history[-WINDOW:]).reshape(1, WINDOW, 1)
        p = float(model.predict(x, verbose=0)[0][0])
        preds_scaled.append(p)
        history.append(p)

    arr = np.array(preds_scaled).reshape(-1, 1)
    return scaler.inverse_transform(arr).flatten().tolist()
