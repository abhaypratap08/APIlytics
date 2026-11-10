import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useProject } from "../hooks/useProject";
import type { EndpointItem, SummaryResponse, Window } from "../types/api";

function CostIntelligence() {
  const { projectId } = useProject();
  const [win, setWin] = useState<Window>("60m");
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [items, setItems] = useState<EndpointItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;
    setLoading(true);
    Promise.all([api.summary(win, projectId), api.endpoints(win, projectId, 100)])
      .then(([s, e]) => { if (!cancelled) { setSummary(s); setItems(e.items); setError(null); } })
      .catch((e: Error) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [projectId, win]);

  const sorted = [...items].sort((a, b) => b.estimated_cost - a.estimated_cost);

  return (
    <>
      <header className="topbar">
        <div>
          <p className="breadcrumb">Workspace / Cost</p>
          <h2>Cost Intelligence</h2>
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
      {loading && <p>Loading…</p>}

      {summary && (
        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-top">Total Estimated Cost</div>
            <h3 className="stat-change">{summary.estimated_cost.toFixed(4)} {summary.cost_unit}</h3>
            <p className="breadcrumb" style={{ marginTop: 8 }}>
              Demo estimate: requests / 1000 × configured rate.
            </p>
          </div>
        </section>
      )}

      <section className="panel activity-panel">
        <div className="panel-header">
          <h3>Cost by Endpoint</h3>
        </div>
        <div className="table-wrapper">
          {!loading && sorted.length > 0 && (
            <table>
              <thead>
                <tr><th>Route</th><th>Requests</th><th>Estimated cost</th><th>Share</th></tr>
              </thead>
              <tbody>
                {sorted.map((e, i) => {
                  const total = summary?.estimated_cost || 0;
                  const share = total > 0 ? (e.estimated_cost / total) * 100 : 0;
                  return (
                    <tr key={`${e.method}:${e.route_template}:${i}`}>
                      <td>
                        <span className={`method ${e.method.toLowerCase()}`}>{e.method}</span> {e.route_template}
                      </td>
                      <td>{e.request_count}</td>
                      <td>{e.estimated_cost.toFixed(4)} {e.cost_unit}</td>
                      <td>{share.toFixed(1)}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}

export default CostIntelligence;
