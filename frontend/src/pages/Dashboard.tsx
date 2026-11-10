import { useEffect, useState } from "react";
import {
  Activity, AlertTriangle, Bell, CheckCircle2, CircleDollarSign,
  Clock3, Globe, Play, Search, ShieldCheck,
} from "lucide-react";
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api } from "../api/client";
import { useProject } from "../hooks/useProject";
import type { EndpointItem, SummaryResponse } from "../types/api";

export default function Dashboard() {
  const { projectId } = useProject();
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [endpoints, setEndpoints] = useState<EndpointItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isLive, setIsLive] = useState(false);

  // Sandbox state
  const [targetUrl, setTargetUrl] = useState("https://jsonplaceholder.typicode.com");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionMsg, setSessionMsg] = useState("");

  useEffect(() => {
    if (!projectId) return;
    setLoading(true);

    // 1. Initial fetch
    Promise.all([
      api.summary("60m", projectId),
      api.endpoints("60m", projectId),
    ]).then(([s, e]) => {
      setSummary(s);
      setEndpoints(e.items);
      setLoading(false);
    }).catch(console.error);

    // 2. Connect to SSE Stream
    const streamUrl = `${api.baseUrl}/api/v1/stream/metrics?project_id=${projectId}`;
    console.log("Connecting to SSE:", streamUrl);
    const eventSource = new EventSource(streamUrl);

    eventSource.onopen = () => {
      console.log("SSE Connection Opened!");
      setIsLive(true);
    };
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setSummary(data.summary);
        setEndpoints(data.endpoints);
        setLoading(false);
      } catch (err) {
        console.error("Failed to parse SSE data", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE connection error", err);
      setIsLive(false);
    };

    return () => {
      eventSource.close();
    };
  }, [projectId]);

  const handleLaunchSandbox = async () => {
    if (!projectId) return;
    setSessionMsg("Starting session...");
    try {
      const res = await fetch(`${api.baseUrl}/api/v1/projects/${projectId}/sandbox-sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_url: targetUrl })
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setSessionId(data.id);
      setSessionMsg(`Session ${data.id} Active. Run the worker script now!`);
    } catch (e: any) {
      setSessionMsg(`Error: ${e.message}`);
    }
  };

  const chartData = endpoints.slice(0, 8).map((e) => ({
    time: e.route_template.length > 15 ? e.route_template.slice(0, 15) + "…" : e.route_template,
    requests: e.request_count,
  }));

  return (
    <>
      <header className="topbar">
        <div><p className="breadcrumb">API Intelligence Dashboard</p><h2>Dashboard</h2></div>
        <div className="topbar-actions">
          <div className="search-box"><Search size={16} /><input placeholder="Search anything..." /><span style={{ fontSize: 11, background: "#f1f5f9", padding: "2px 6px", borderRadius: 4 }}>Ctrl + K</span></div>
          <button className="icon-button"><Bell size={18} /></button>
          {isLive ? (
            <div className="status-indicator" style={{ background: "#ecfdf5", color: "#059669", borderColor: "#a7f3d0" }}>
              <span style={{ background: "#059669" }}></span> Live Connected
            </div>
          ) : (
            <div className="status-indicator" style={{ background: "#fef2f2", color: "#dc2626", borderColor: "#fecaca" }}>
              <span style={{ background: "#dc2626" }}></span> Offline
            </div>
          )}
        </div>
      </header>

      <div className="hero-sandbox">
        <div className="hero-content">
          <h2><Globe size={24} color="#0f766e" /> Website Sandbox <span className="hero-badge">Live Test</span></h2>
          <p>Enter a URL to launch an isolated browser and monitor its API activity in real-time.</p>
          <div className="hero-form">
            <input type="text" value={targetUrl} onChange={(e) => setTargetUrl(e.target.value)} placeholder="https://jsonplaceholder.typicode.com" />
            <button className="hero-btn" onClick={handleLaunchSandbox}><Play size={16} fill="white" /> Launch Sandbox</button>
          </div>
          {sessionMsg && <p style={{ marginTop: 8, fontSize: 13, color: "#0f766e", fontWeight: "bold" }}>{sessionMsg}</p>}
          {sessionId && <p style={{ fontSize: 12, background: "#e2e8f0", padding: 8, borderRadius: 4, marginTop: 8 }}>Run in terminal: <code>python collector/sandbox_worker.py {sessionId} {targetUrl}</code></p>}
        </div>
        <div className="hero-features">
          <div className="hero-feature"><CheckCircle2 size={18} color="#0f766e" /> Isolated Browser</div>
          <div className="hero-feature"><CheckCircle2 size={18} color="#0f766e" /> Real-time Monitoring</div>
          <div className="hero-feature"><CheckCircle2 size={18} color="#0f766e" /> Safe & Secure</div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">Total API Requests <div className="stat-icon"><Activity size={18} /></div></div>
          <h2>{loading ? "..." : summary?.total_requests.toLocaleString() || "0"}</h2>
        </div>
        <div className="stat-card">
          <div className="stat-top">Avg Response Time <div className="stat-icon"><Clock3 size={18} /></div></div>
          <h2>{loading ? "..." : summary?.avg_latency_ms.toFixed(1) || "0"} <span style={{fontSize: 16}}>ms</span></h2>
        </div>
        <div className="stat-card">
          <div className="stat-top">Error Rate <div className="stat-icon" style={{background:"#fee2e2", color:"#ef4444"}}><AlertTriangle size={18} /></div></div>
          <h2>{loading ? "..." : summary?.error_rate_pct.toFixed(2) || "0"}%</h2>
        </div>
        <div className="stat-card">
          <div className="stat-top">Estimated API Cost <div className="stat-icon"><CircleDollarSign size={18} /></div></div>
          <h2>${loading ? "..." : summary?.estimated_cost.toFixed(2) || "0.00"}</h2>
        </div>
      </div>

      <div className="content-grid">
        <div className="panel">
          <div className="panel-header">
            <div><h3>API Traffic Overview</h3><p>Request volume over time</p></div>
            <div className="chart-legend"><span></span> API Requests</div>
          </div>
          <div style={{ height: 300 }}>
            {chartData.length === 0 ? <p style={{color:"#64748b"}}>No requests yet. Launch a sandbox above!</p> : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorReq" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0f766e" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0f766e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill:"#64748b", fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill:"#64748b", fontSize: 12}} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }} />
                  <Area type="monotone" dataKey="requests" stroke="#0f766e" strokeWidth={2} fillOpacity={1} fill="url(#colorReq)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header"><div><h3>System Health</h3><p>Current infrastructure status</p></div></div>
          <div className="health-status">
            <div className="health-icon"><ShieldCheck size={32} /></div>
            <h2>All Systems Normal</h2>
            <p>All monitored services are operational.</p>
          </div>
          <div className="health-row"><span>Active Alerts</span><strong style={{color: summary?.alerts_count ? "#d97706" : "#10b981"}}>{summary?.alerts_count || 0}</strong></div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header"><div><h3>Recent API Activity</h3><p>Latest requests across your endpoints</p></div></div>
        <div className="table-wrapper">
          <table>
            <thead><tr><th>METHOD</th><th>ENDPOINT</th><th>REQUESTS</th><th>LATENCY</th></tr></thead>
            <tbody>
              {endpoints.length === 0 ? <tr><td colSpan={4} style={{textAlign:"center", color:"#64748b"}}>No events captured.</td></tr> :
                endpoints.map((item, i) => (
                <tr key={i}>
                  <td><span className={`method ${item.method.toLowerCase()}`}>{item.method}</span></td>
                  <td style={{ fontWeight: 500 }}>{item.route_template}</td>
                  <td>{item.request_count}</td>
                  <td><span className="latency"><Clock3 size={14} /> {item.avg_latency_ms.toFixed(1)} ms</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
