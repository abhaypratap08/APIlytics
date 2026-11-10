import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Bell,
  CircleDollarSign,
  Clock3,
  Search,
  ShieldCheck,
  Zap,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "../App.css";
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
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, win]);

  // Use the top endpoints as our traffic chart data
  const chartData = endpoints.slice(0, 8).map((e) => ({
    time: e.route_template.length > 15 ? e.route_template.slice(0, 15) + "…" : e.route_template,
    requests: e.request_count,
  }));

  // Use the top 5 endpoints as our recent activity
  const activities = endpoints.slice(0, 5);

  const banner = projectError || error;

  return (
    <>
      <header className="topbar">
        <div>
          <p className="breadcrumb">Workspace / Overview</p>
          <h2>Dashboard</h2>
        </div>

        <div className="topbar-actions">
          <div className="search-box">
            <Search size={17} />
            <input placeholder="Search anything..." />
          </div>
          <button className="icon-button" aria-label="Notifications">
            <Bell size={19} />
          </button>
          <div className="status-indicator">
            <span></span> System Operational
          </div>
        </div>
      </header>

      {banner && (
        <div className="negative" style={{ padding: "12px", marginBottom: "20px", borderRadius: "8px" }}>
          Backend Error: {banner}
        </div>
      )}

      <section className="welcome-section">
        <div>
          <h1>Welcome back, Abhay 👋</h1>
          <p>Here's what's happening with your APIs today.</p>
        </div>
        <select
          className="date-button"
          value={win}
          onChange={(e) => setWin(e.target.value as Window)}
        >
          <option value="15m">Last 15 minutes ▾</option>
          <option value="60m">Last 60 minutes ▾</option>
          <option value="24h">Last 24 hours ▾</option>
        </select>
      </section>

      {loading && !summary && <p>Loading live data...</p>}

      {summary && (
        <>
          <section className="stats-grid">
            <StatCard
              title="Total API Requests"
              value={summary.total_requests.toLocaleString()}
              change=""
              icon={<Activity />}
              positive
            />
            <StatCard
              title="Avg. Response Time"
              value={`${summary.avg_latency_ms.toFixed(1)} ms`}
              change=""
              icon={<Zap />}
              positive={summary.avg_latency_ms < 500}
            />
            <StatCard
              title="Error Rate"
              value={`${summary.error_rate_pct.toFixed(2)}%`}
              change=""
              icon={<AlertTriangle />}
              positive={summary.error_rate_pct === 0}
            />
            <StatCard
              title="Estimated API Cost"
              value={`${summary.estimated_cost.toFixed(2)} ${summary.cost_unit}`}
              change=""
              icon={<CircleDollarSign />}
              positive
            />
          </section>

          <section className="content-grid">
            <div className="panel traffic-panel">
              <div className="panel-header">
                <div>
                  <h3>API Traffic Overview</h3>
                  <p>Request volume by endpoint</p>
                </div>
                <span className="chart-legend">
                  <span></span> API Requests
                </span>
              </div>

              <div className="chart-container">
                {chartData.length === 0 ? (
                  <p>No traffic in this window.</p>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="trafficGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.35} />
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="#252b3b" strokeDasharray="4 4" vertical={false} />
                      <XAxis dataKey="time" stroke="#788198" tickLine={false} axisLine={false} />
                      <YAxis stroke="#788198" tickLine={false} axisLine={false} />
                      <Tooltip
                        contentStyle={{
                          background: "#171d2b",
                          border: "1px solid #343b50",
                          borderRadius: "10px",
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="requests"
                        stroke="#9b7bff"
                        strokeWidth={2.5}
                        fill="url(#trafficGradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            <div className="panel health-panel">
              <div className="panel-header">
                <div>
                  <h3>System Health</h3>
                  <p>Current infrastructure status</p>
                </div>
              </div>

              <div className="health-status">
                <div className="health-icon">
                  <ShieldCheck size={32} />
                </div>
                <h2>All Systems Normal</h2>
                <p>All monitored services are operational.</p>
              </div>

              <div className="health-row">
                <span>API Availability</span>
                <strong>{(100 - summary.error_rate_pct).toFixed(2)}%</strong>
              </div>
              <div className="health-row">
                <span>Active Endpoints</span>
                <strong>{endpoints.length}</strong>
              </div>
              <div className="health-row">
                <span>Active Alerts</span>
                <strong className={summary.alerts_count > 0 ? "warning-text" : ""}>
                  {summary.alerts_count}
                </strong>
              </div>
            </div>
          </section>

          <section className="panel activity-panel">
            <div className="panel-header">
              <div>
                <h3>Recent API Activity</h3>
                <p>Latest requests across your endpoints</p>
              </div>
            </div>

            <div className="table-wrapper">
              {activities.length === 0 ? (
                <p>No endpoint activity yet.</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>METHOD</th>
                      <th>ENDPOINT</th>
                      <th>REQUESTS</th>
                      <th>ERROR RATE</th>
                      <th>LATENCY</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activities.map((item, index) => (
                      <tr key={index}>
                        <td>
                          <span className={`method ${item.method.toLowerCase()}`}>
                            {item.method}
                          </span>
                        </td>
                        <td className="endpoint">{item.route_template}</td>
                        <td>{item.request_count}</td>
                        <td>
                          <span
                            className={
                              item.error_rate_pct === 0 ? "success-badge" : "error-badge"
                            }
                          >
                            {item.error_rate_pct.toFixed(2)}%
                          </span>
                        </td>
                        <td>
                          <span className="latency">
                            <Clock3 size={14} /> {item.p95_latency_ms.toFixed(1)} ms
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        </>
      )}

      <footer className="footer">
        APIlytics © 2026 · AI-powered API intelligence
      </footer>
    </>
  );
}

type StatCardProps = {
  title: string;
  value: string;
  change: string;
  icon: React.ReactNode;
  positive?: boolean;
};

function StatCard({
  title,
  value,
  change,
  icon,
  positive = false,
}: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{title}</span>
        <div className="stat-icon">{icon}</div>
      </div>
      <h2>{value}</h2>
      {change && (
        <div className="stat-change">
          {positive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
          <strong className={positive ? "positive" : "negative"}>
            {change}
          </strong>
          <span>vs previous period</span>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
