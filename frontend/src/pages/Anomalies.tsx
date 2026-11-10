import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useProject } from "../hooks/useProject";
import type { AlertItem, Window } from "../types/api";

function Anomalies() {
  const { projectId } = useProject();
  const [win, setWin] = useState<Window>("60m");
  const [items, setItems] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;
    setLoading(true);
    api.alerts(win, projectId)
      .then((r) => { if (!cancelled) { setItems(r.items); setError(null); } })
      .catch((e: Error) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [projectId, win]);

  return (
    <>
      <header className="topbar">
        <div>
          <p className="breadcrumb">Workspace / Anomalies</p>
          <h2>Anomaly Detection</h2>
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
      {!loading && items.length === 0 && <p>No anomalies detected in this window.</p>}

      <section className="content-grid" style={{ display: "block" }}>
        {items.map((a) => (
          <div key={a.id} className="panel" style={{ marginBottom: 16 }}>
            <div className="panel-header">
              <h3>{a.title}</h3>
              <span className={`badge ${a.severity === "HIGH" ? "error-badge" : "success-badge"}`}>
                {a.severity}
              </span>
            </div>
            <p>{a.message}</p>
            <p className="breadcrumb" style={{ marginTop: 8 }}>
              <strong>{a.method} {a.route_template}</strong> · {a.type}
            </p>
            <p className="breadcrumb" style={{ marginTop: 4 }}>
              Recommendation: {a.recommendation}
            </p>
          </div>
        ))}
      </section>
    </>
  );
}

export default Anomalies;
