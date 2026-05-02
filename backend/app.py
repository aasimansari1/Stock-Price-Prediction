"""FastAPI server for the Stock Price Prediction app.

Exposes:
  GET  /                 health check
  GET  /get-stock-data   historical OHLCV for a ticker
  POST /predict          next-N-days price forecast (linear / random_forest / lstm)
"""

import logging
import os
import sys

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure the repo root is importable so we can `from model import ...`
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from model.data_loader import fetch_stock_data
from model.predictor import predict_prices

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("stock-api")

app = FastAPI(title="Stock Price Prediction API", version="1.0.0")

# Allow the React dev server and any deployed frontend to call us.
# In production, set ALLOWED_ORIGINS to a comma-separated list of explicit origins.
allowed = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed.split(",")] if allowed != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    symbol: str = Field(..., description="Ticker symbol e.g. AAPL")
    model: str = Field("linear", description="linear | random_forest | lstm")
    days: int = Field(7, ge=1, le=30, description="Number of business days to forecast")
    period: str = Field("1y", description="yfinance period: 6mo, 1y, 2y, 5y, max ...")


@app.get("/")
def root():
    return {"status": "ok", "service": "Stock Price Prediction API"}


@app.get("/get-stock-data")
def get_stock_data(
    symbol: str = Query(..., min_length=1, max_length=15),
    period: str = Query("1y"),
):
    try:
        return fetch_stock_data(symbol, period)
    except ValueError as e:
        # Invalid ticker / no data
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:  # noqa: BLE001
        log.exception("get-stock-data failed")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@app.post("/predict")
def predict(req: PredictRequest):
    if req.model not in {"linear", "random_forest", "lstm"}:
        raise HTTPException(status_code=400, detail="model must be one of: linear, random_forest, lstm")
    try:
        return predict_prices(req.symbol, req.model, req.days, req.period)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:  # noqa: BLE001
        log.exception("predict failed")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
