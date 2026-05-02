# Stock Price Prediction — Full-Stack AI Web App

A React + FastAPI app that fetches historical stock prices from Yahoo Finance,
trains a model (Linear Regression / Random Forest / LSTM) on demand, and shows
the next 1–30 business days of predicted closes alongside the actual chart.

```
.
├── backend/      FastAPI server — REST endpoints
├── model/        ML code — data loading, three models, unified predictor
└── frontend/     React + Vite + Recharts UI
```

---

## What it does

- **Input** a ticker (`AAPL`, `TSLA`, `MSFT`, `INFY.NS`, `RELIANCE.NS`, …)
- **Pick** a history window (6mo – 5y) and a model (Linear / Random Forest / LSTM)
- **See** an actual-vs-predicted chart, percentage change, and a daily forecast table
- **Train/test R²** are surfaced so you can compare model quality

API endpoints exposed by the backend:

| Method | Path                | Description                                 |
| ------ | ------------------- | ------------------------------------------- |
| GET    | `/get-stock-data`   | Historical OHLCV for a symbol               |
| POST   | `/predict`          | Forecast next N business days               |
| GET    | `/`                 | Health check                                |

---

## Quick start (local)

You'll run two processes: the Python API on `:8000` and the Vite dev server on `:5173`.

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Open <http://localhost:8000/docs> to see the auto-generated Swagger UI.

> **Note on TensorFlow:** the LSTM model requires `tensorflow`. If you don't
> need LSTM, you can comment that line out of `requirements.txt` and the
> Linear / Random Forest models will still work — TF is imported lazily.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The Vite dev server proxies `/get-stock-data`
and `/predict` to the FastAPI backend so there is no CORS configuration to do
in development.

---

## Project layout

```
backend/
  app.py             FastAPI app — wires the API to model.predictor
  requirements.txt
  render.yaml        Render.com blueprint
  Procfile           Railway / Heroku-style procfile
  .env.example

model/
  __init__.py
  data_loader.py     yfinance fetch + preprocessing
  linear_model.py    sklearn Linear Regression (windowed)
  random_forest.py   sklearn Random Forest (windowed)
  lstm_model.py      Keras LSTM (sequence-to-one)
  predictor.py       Unified train + forecast entrypoint

frontend/
  package.json
  vite.config.js     Dev proxy to backend on :8000
  index.html
  vercel.json        SPA rewrite for Vercel
  .env.example
  src/
    main.jsx
    App.jsx          Top-level: form → fetch → chart + panel
    App.css
    api.js           Tiny fetch wrapper
    components/
      StockForm.jsx       Ticker, period, model, days inputs
      PriceChart.jsx      Recharts line chart, actual + predicted
      PredictionPanel.jsx Stats cards + prediction table
```

---

## How the models work

All three models share the same framing: **given the last `N` daily closes,
predict the next close**. To produce a multi-day forecast, predictions are fed
back in autoregressively. Errors compound over the horizon — that's expected.

| Model           | Window | Notes                                                 |
| --------------- | ------ | ----------------------------------------------------- |
| Linear          | 10     | sklearn `LinearRegression`. Fast baseline.            |
| Random Forest   | 10     | 200 trees, parallel, `min_samples_leaf=2`.            |
| LSTM            | 30     | 2 stacked LSTM layers + dropout, 15 epochs, Adam.     |

Train/test split is **80/20 chronological** (no shuffling — that would leak
future into past). The `train_score` and `test_score` returned by `/predict`
are R² values on each split.

LSTM is trained on demand per request, which keeps the project simple but
means the first LSTM call for a symbol takes ~10–20s on CPU. For production,
cache the trained model per `(symbol, period)`.

---

## Deployment

### Frontend → Vercel

1. Push the repo to GitHub.
2. Import the project on Vercel and set the **Root Directory** to `frontend`.
3. Vercel detects Vite from `vercel.json` automatically.
4. Add an env var `VITE_API_BASE` pointing to your deployed backend URL
   (e.g. `https://stock-prediction-api.onrender.com`).
5. Deploy.

### Backend → Render

1. Create a **New Web Service** on Render and point it at the same GitHub repo.
2. Set the **Root Directory** to `backend` (or rely on `render.yaml`, which
   already configures this).
3. Render will run `pip install -r requirements.txt` then
   `uvicorn app:app --host 0.0.0.0 --port $PORT`.
4. Optionally set `ALLOWED_ORIGINS` to your Vercel URL for stricter CORS.

> **Memory note:** TensorFlow needs ~500 MB RAM. Render's free tier (512 MB)
> is borderline — if you OOM on LSTM, either upgrade the plan or remove
> `tensorflow` from `requirements.txt` and only ship the Linear / RF models.

### Backend → Railway (alternative)

Railway picks up the `Procfile`. Set the Root Directory to `backend` and
deploy — it'll install requirements and run uvicorn automatically.

---

## API examples

```bash
# Historical data
curl "http://localhost:8000/get-stock-data?symbol=AAPL&period=1y"

# Forecast
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","model":"random_forest","days":7,"period":"1y"}'
```

Response from `/predict`:

```json
{
  "symbol": "AAPL",
  "model": "random_forest",
  "period": "1y",
  "history":  [{ "date": "2024-05-02", "close": 173.03 }, ...],
  "predictions": [
    { "date": "2025-05-05", "predicted_price": 207.41 },
    { "date": "2025-05-06", "predicted_price": 207.88 }
  ],
  "current_price": 205.10,
  "predicted_price": 207.88,
  "percent_change": 1.36,
  "train_score": 0.9821,
  "test_score": 0.4135
}
```

---

## Error handling

- **Invalid ticker** → backend returns `404 {"detail": "No data found ..."}`,
  the UI shows a red banner.
- **Insufficient history** (period too short for LSTM) → `400` with a
  human-readable message; switch to a longer period or a simpler model.
- **Network failure** → the React `api.js` wrapper surfaces the error message
  unchanged into the UI.

---

## Possible extensions

- **Login / signup** — add JWT auth in FastAPI, persist watchlists in SQLite/Postgres.
- **Multi-stock comparison** — `/predict` already returns history, so the
  frontend just needs to call it for several tickers and overlay the lines.
- **News sentiment** — pull headlines (NewsAPI / Finnhub), score with a HF
  sentiment model, feed daily sentiment as an extra LSTM feature.
- **Caching** — memoize `/predict` by `(symbol, period, model, day)` to make
  the LSTM path interactive.

---

## Disclaimer

This is an educational demo. Past prices and naive autoregressive forecasts
do **not** reliably predict future returns. Don't trade real money on this.
