import React, { useState } from "react";

const PERIODS = [
  { value: "6mo", label: "6 months" },
  { value: "1y", label: "1 year" },
  { value: "2y", label: "2 years" },
  { value: "5y", label: "5 years" },
];

const MODELS = [
  { value: "linear", label: "Linear Regression (fast)" },
  { value: "random_forest", label: "Random Forest" },
  { value: "lstm", label: "LSTM (slow, ~10–20s)" },
];

export default function StockForm({ onSubmit, loading }) {
  const [symbol, setSymbol] = useState("AAPL");
  const [period, setPeriod] = useState("1y");
  const [model, setModel] = useState("linear");
  const [days, setDays] = useState(7);

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = symbol.trim().toUpperCase();
    if (!trimmed) return;
    onSubmit({ symbol: trimmed, period, model, days: Number(days) });
  }

  return (
    <form className="stock-form" onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="symbol">Stock symbol</label>
        <input
          id="symbol"
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="AAPL, TSLA, INFY.NS"
          autoComplete="off"
          spellCheck={false}
        />
      </div>

      <div className="field">
        <label htmlFor="period">History</label>
        <select id="period" value={period} onChange={(e) => setPeriod(e.target.value)}>
          {PERIODS.map((p) => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="model">Model</label>
        <select id="model" value={model} onChange={(e) => setModel(e.target.value)}>
          {MODELS.map((m) => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="days">Days ahead</label>
        <input
          id="days"
          type="number"
          min={1}
          max={30}
          value={days}
          onChange={(e) => setDays(e.target.value)}
        />
      </div>

      <button type="submit" disabled={loading} className="primary">
        {loading ? "Predicting…" : "Fetch & Predict"}
      </button>
    </form>
  );
}
