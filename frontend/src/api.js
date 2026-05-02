// Thin wrapper around fetch that targets the FastAPI backend.
// In dev, VITE_API_BASE is empty and Vite proxies /get-stock-data and /predict to localhost:8000.
// In prod, set VITE_API_BASE to the deployed backend URL (e.g. on Render).
const BASE = import.meta.env.VITE_API_BASE || "";

async function handle(res) {
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) msg = body.detail;
    } catch {
      /* swallow — keep generic message */
    }
    throw new Error(msg);
  }
  return res.json();
}

export function getStockData(symbol, period = "1y") {
  const url = `${BASE}/get-stock-data?symbol=${encodeURIComponent(symbol)}&period=${encodeURIComponent(period)}`;
  return fetch(url).then(handle);
}

export function predict({ symbol, model = "linear", days = 7, period = "1y" }) {
  return fetch(`${BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, model, days, period }),
  }).then(handle);
}
