import React from "react";

function pctClass(v) {
  if (v == null) return "";
  return v >= 0 ? "pct up" : "pct down";
}

export default function PredictionPanel({ result }) {
  if (!result) return null;
  const { symbol, model, current_price, predicted_price, percent_change, train_score, test_score, predictions } = result;

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>{symbol}</h2>
        <span className="badge">{model}</span>
      </div>

      <div className="stats">
        <div className="stat">
          <div className="label">Current</div>
          <div className="value">${current_price?.toFixed?.(2) ?? current_price}</div>
        </div>
        <div className="stat">
          <div className="label">Predicted (last day)</div>
          <div className="value">${predicted_price?.toFixed?.(2) ?? predicted_price}</div>
        </div>
        <div className="stat">
          <div className="label">Forecast change</div>
          <div className={`value ${pctClass(percent_change)}`}>
            {percent_change >= 0 ? "+" : ""}
            {percent_change?.toFixed?.(2)}%
          </div>
        </div>
        <div className="stat">
          <div className="label">Train R²</div>
          <div className="value muted">{train_score?.toFixed?.(3)}</div>
        </div>
        <div className="stat">
          <div className="label">Test R²</div>
          <div className="value muted">{test_score?.toFixed?.(3)}</div>
        </div>
      </div>

      <table className="pred-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Predicted price</th>
          </tr>
        </thead>
        <tbody>
          {predictions?.map((p) => (
            <tr key={p.date}>
              <td>{p.date}</td>
              <td>${p.predicted_price.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
