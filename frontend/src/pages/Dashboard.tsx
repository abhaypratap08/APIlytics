import { useEffect, useState } from "react";
import {
  Activity, AlertTriangle, Bell, CircleDollarSign, Clock3, ShieldCheck, Zap
} from "lucide-react";
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api } from "../api/client";
import { useProject } from "../hooks/useProject";
import type { EndpointItem, SummaryResponse, Window } from "../types/api";

function Dashboard() {
  const { projectId, error: projectError } = useProject();
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [endpoints, setEndpoints] = useState<EndpointItem[]>([]);
  const [win, setWin] = useState<Window>("60m");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([
      api.summary(win, projectId),
      api.endpoints(win, projectId),
    ])
      .then(([s, e]) => {
        if (cancelled) return;
        setSummary(s);
        setEndpoints(e.items);
      })
      .catch((err: Error) => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [projectId, win]);

  const chartData = endpoints.slice(0, 8).map((e) => ({
    time: e.route_template.length > 18 ? e.route_template.slice(0, 18) + "…" : e.route_template,
    requests: e.request_count,
  }));

  const banner = projectError || error;

  return (
    <>
      <header className="topbar">
        <div>
          <p className="breadcrumb">Workspace / Overview</p>
          <h2>Dashboard</h2>
        </div>
        <div className="topbar-actions">
          <select className="date-button" value={win} onChange={(e) => setWin(e.target.value as Window)}>
            <option value="15m">Last 15m</option>
            <option value="60m">Last 60m</option>
            <option value="24h">Last 24h</option>
          </select>
        </div>
      </header>

      {banner && <div className="negative" style={{ padding: 12, marginBottom: 16 }}>Backend error: {banner}</div>}
      {loading && <p>Loading…</p>}

      {summary && (
        <>
          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-top"><Activity size={18} /> Total requests</div>
              <h3 className="stat-change positive">{summary.total_requests.toLocaleString()}</h3>
            </div>
            <div className="stat-card">
              <div className="stat-top"><AlertTriangle size={18} /> Error rate</div>
              <h3 className="stat-change negative">{summary.error_rate_pct.toFixed(2)}%</h3>
            </div>
            <div className="stat-card">
              <div className="stat-top"><Clock3 size={18} /> p95 latency</div>
              <h3 className="stat-change">{summary.p95_latency_ms.toFixed(1)} ms</h3>
            </div>
            <div className="stat-card">
              <div className="stat-top"><CircleDollarSign size={18} /> Estimated cost</div>
              <h3 className="stat-change">{summary.estimated_cost.toFixed(2)} <small>{summary.cost_unit}</small></h3>
            </div>
          </section>

          <section className="content-grid">
            <div className="panel traffic-panel">
              <div className="panel-header">
                <h3>Requests by endpoint</h3>
                <span className="chart-legend">Live data</span>
              </div>
              <div className="chart-container">
                {chartData.length === 0 ? (
                  <p>No requests in this window.</p>
                ) : (
                  <ResponsiveContainer width="100%" height={260}>
                    <AreaChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Area type="monotone" dataKey="requests" stroke="#2ea043" fill="#2ea04355" />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            <div className="panel health-panel">
              <div className="panel-header">
                <h3>System Health</h3>
              </div>
              <div className="health-status">
                <div className="health-icon"><Zap size={24} /></div>
                <h3>All systems operational</h3>
                <p>Monitoring {endpoints.length} active endpoints</p>
              </div>
              <div className="health-row">
                <span>Active Alerts</span>
                <strong className={summary.alerts_count > 0 ? "warning-text" : ""}>{summary.alerts_count}</strong>
              </div>
              <div className="health-row">
                <span>5xx Errors</span>
                <strong>{summary.error_count}</strong>
              </div>
              <div className="health-row">
                <span>Avg Latency</span>
                <strong>{summary.avg_latency_ms.toFixed(1)} ms</strong>
              </div>
            </div>
          </section>

          <section className="panel activity-panel">
            <div className="panel-header">
              <h3>Recent endpoint activity</h3>
            </div>
            <div className="table-wrapper">
              {endpoints.length === 0 ? (
                <p>No endpoint activity in this window.</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Method</th><th>Route</th>
                      <th>Requests</th><th>Error %</th>
                      <th>p95</th><th>Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {endpoints.slice(0, 10).map((e, i) => (
                      <tr key={`${e.method}:${e.route_template}:${i}`}>
                        <td><span className={`method ${e.method.toLowerCase()}`}>{e.method}</span></td>
                        <td>{e.route_template}</td>
                        <td>{e.request_count}</td>
                        <td>{e.error_rate_pct.toFixed(2)}%</td>
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
      )}
    </>
  );
}

export default Dashboard;
