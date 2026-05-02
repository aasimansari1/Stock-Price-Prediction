import React, { useMemo } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
} from "recharts";

// Merges the historical closes and forecasted prices onto a single time axis,
// with the forecast living in a separate series so it renders as a distinct line.
export default function PriceChart({ history, predictions }) {
  const data = useMemo(() => {
    const merged = (history || []).map((p) => ({
      date: p.date,
      actual: p.close,
      predicted: null,
    }));

    if (history && history.length && predictions && predictions.length) {
      // Anchor the predicted line at the last actual point so the two segments connect.
      const last = history[history.length - 1];
      merged.push({ date: last.date, actual: last.close, predicted: last.close });
    }

    (predictions || []).forEach((p) => {
      merged.push({ date: p.date, actual: null, predicted: p.predicted_price });
    });

    return merged;
  }, [history, predictions]);

  const splitDate = predictions && predictions.length ? history?.[history.length - 1]?.date : null;

  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height={380}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3a" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#9aa3b2" }}
            minTickGap={40}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#9aa3b2" }}
            domain={["auto", "auto"]}
            tickFormatter={(v) => `$${v.toFixed(0)}`}
          />
          <Tooltip
            contentStyle={{
              background: "#161922",
              border: "1px solid #2a2f3a",
              borderRadius: 6,
              color: "#e6e8ee",
            }}
            formatter={(v) => (v == null ? "—" : `$${Number(v).toFixed(2)}`)}
          />
          <Legend />
          {splitDate && <ReferenceLine x={splitDate} stroke="#5b6070" strokeDasharray="4 4" label={{ value: "today", fill: "#9aa3b2", fontSize: 11, position: "top" }} />}
          <Line
            type="monotone"
            dataKey="actual"
            name="Actual"
            stroke="#4f8cff"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="predicted"
            name="Predicted"
            stroke="#f59e0b"
            strokeWidth={2}
            strokeDasharray="6 4"
            dot={{ r: 3, fill: "#f59e0b" }}
            connectNulls={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
