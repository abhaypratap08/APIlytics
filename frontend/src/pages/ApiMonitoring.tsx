import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useProject } from "../hooks/useProject";
import type { EndpointItem, Window } from "../types/api";

function ApiMonitoring() {
  const { projectId } = useProject();
  const [win, setWin] = useState<Window>("60m");
  const [items, setItems] = useState<EndpointItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;
    setLoading(true);
    api.endpoints(win, projectId, 100)
      .then((r) => { if (!cancelled) { setItems(r.items); setError(null); } })
      .catch((e: Error) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [projectId, win]);

  return (
    <>
      <header className="topbar">
        <div>
          <p className="breadcrumb">Workspace / Monitoring</p>
          <h2>API Monitoring</h2>
        </div>
        <div className="topbar-actions">
          <select className="date-button" value={win} onChange={(e) => setWin(e.target.value as Window)}>
            <option value="15m">Last 15m</option>
            <option value="60m">Last 60m</option>
            <option value="24h">Last 24h</option>
          </select>
        </div>
      </header>

      {error && <p className="negative">{error}</p>}
      
      <section className="panel activity-panel">
        <div className="panel-header">
          <h3>Endpoint Details</h3>
        </div>
        <div className="table-wrapper">
          {loading && <p>Loading…</p>}
          {!loading && items.length === 0 && <p>No endpoints have data in this window.</p>}
          {!loading && items.length > 0 && (
            <table>
              <thead>
                <tr><th>Method</th><th>Route</th><th>Requests</th><th>Error %</th>
                  <th>Avg</th><th>p95</th><th>Cost</th></tr>
              </thead>
              <tbody>
                {items.map((e, i) => (
                  <tr key={`${e.method}:${e.route_template}:${i}`}>
                    <td><span className={`method ${e.method.toLowerCase()}`}>{e.method}</span></td>
                    <td>{e.route_template}</td>
                    <td>{e.request_count}</td>
                    <td>{e.error_rate_pct.toFixed(2)}%</td>
                    <td>{e.avg_latency_ms.toFixed(1)} ms</td>
                    <td>{e.p95_latency_ms.toFixed(1)} ms</td>
                    <td>{e.estimated_cost.toFixed(2)} {e.cost_unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}

export default ApiMonitoring;
