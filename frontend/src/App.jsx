import React, { useState } from "react";
import StockForm from "./components/StockForm.jsx";
import PriceChart from "./components/PriceChart.jsx";
import PredictionPanel from "./components/PredictionPanel.jsx";
import { predict } from "./api.js";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function handleSubmit(params) {
    setLoading(true);
    setError(null);
    try {
      // /predict already returns the full history alongside the forecast,
      // so we don't also need to call /get-stock-data here.
      const data = await predict(params);
      setResult(data);
    } catch (e) {
      setError(e.message || "Something went wrong");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <h1>Stock Price Prediction</h1>
        <p>Pick a ticker and a model, see a 1–30 day forecast.</p>
      </header>

      <StockForm onSubmit={handleSubmit} loading={loading} />

      {error && <div className="error">⚠ {error}</div>}

      {result && (
        <>
          <PriceChart history={result.history} predictions={result.predictions} />
          <PredictionPanel result={result} />
        </>
      )}

      {!result && !error && !loading && (
        <div className="empty">
          Try AAPL, TSLA, MSFT, GOOGL, INFY.NS, RELIANCE.NS — anything Yahoo Finance knows.
        </div>
      )}

      <footer className="foot">
        <span>Educational demo — not financial advice.</span>
      </footer>
    </div>
  );
}
