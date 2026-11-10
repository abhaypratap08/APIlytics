import {
  Activity, AlertTriangle, Bell, CheckCircle2, ChevronRight,
  CircleDollarSign, Clock3, Globe, LayoutDashboard, Lock,
  Play, Search, Settings, ShieldCheck, Zap,
} from "lucide-react";
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

export default function Dashboard() {
  const trafficData = [
    { time: "09:00", requests: 150000 }, { time: "10:00", requests: 250000 },
    { time: "11:00", requests: 200000 }, { time: "12:00", requests: 350000 },
    { time: "13:00", requests: 300000 }, { time: "14:00", requests: 450000 },
    { time: "15:00", requests: 400000 }, { time: "16:00", requests: 520000 },
    { time: "17:00", requests: 480000 },
  ];

  const recentActivity = [
    { method: "GET", endpoint: "/api/users", status: "200", latency: "124ms" },
    { method: "POST", endpoint: "/api/auth/login", status: "200", latency: "210ms" },
    { method: "GET", endpoint: "/api/products", status: "200", latency: "98ms" },
    { method: "DELETE", endpoint: "/api/orders/42", status: "500", latency: "430ms" },
    { method: "GET", endpoint: "/api/analytics", status: "200", latency: "156ms" },
  ];

  return (
    <div className="app-container">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><Activity size={20} /></div>
          APIlytics
        </div>

        <div className="workspace">
          <div className="workspace-dot"></div>
          Production Workspace
        </div>

        <div className="nav-section">
          <div className="nav-title">Overview</div>
          <div className="nav-item active"><LayoutDashboard size={18} /> Dashboard</div>
          <div className="nav-item"><Activity size={18} /> API Monitoring</div>
          <div className="nav-item"><AlertTriangle size={18} /> Anomaly Detection</div>
          <div className="nav-item"><CircleDollarSign size={18} /> Cost Intelligence</div>
        </div>

        <div className="nav-section">
          <div className="nav-title">Preferences</div>
          <div className="nav-item"><Bell size={18} /> Alerts</div>
          <div className="nav-item"><Settings size={18} /> Settings</div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">API Intelligence Dashboard</p>
            <h2>Dashboard</h2>
          </div>
          <div className="topbar-actions">
            <div className="search-box">
              <Search size={16} />
              <input placeholder="Search anything..." />
              <span style={{ fontSize: 11, background: "#f1f5f9", padding: "2px 6px", borderRadius: 4 }}>Ctrl + K</span>
            </div>
            <button className="icon-button"><Bell size={18} /></button>
            <div className="status-indicator">
              <span></span> System Operational
            </div>
          </div>
        </header>

        {/* SANDBOX HERO */}
        <div className="hero-sandbox">
          <div className="hero-content">
            <h2><Globe size={24} color="#0f766e" /> Website Sandbox <span className="hero-badge">Try Now</span></h2>
            <p>Enter a URL to launch an isolated browser and monitor its API activity in real-time.</p>
            <div className="hero-form">
              <input type="text" placeholder="https://example.com" />
              <button className="hero-btn"><Play size={16} fill="white" /> Launch Sandbox</button>
            </div>
          </div>
          <div className="hero-features">
            <div className="hero-feature"><CheckCircle2 size={18} color="#0f766e" /> Isolated Browser</div>
            <div className="hero-feature"><CheckCircle2 size={18} color="#0f766e" /> Real-time Monitoring</div>
            <div className="hero-feature"><CheckCircle2 size={18} color="#0f766e" /> Safe & Secure</div>
          </div>
        </div>

        {/* STATS */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-top">Total API Requests <div className="stat-icon"><Activity size={18} /></div></div>
            <h2>1.28M</h2>
            <div className="stat-change positive"><Zap size={14} fill="currentColor" /> +12.5% <span style={{color:"#64748b"}}>vs previous period</span></div>
          </div>
          <div className="stat-card">
            <div className="stat-top">Avg Response Time <div className="stat-icon"><Clock3 size={18} /></div></div>
            <h2>142 ms</h2>
            <div className="stat-change positive"><Zap size={14} fill="currentColor" /> +8.8% <span style={{color:"#64748b"}}>vs previous period</span></div>
          </div>
          <div className="stat-card">
            <div className="stat-top">Error Rate <div className="stat-icon" style={{background:"#fee2e2", color:"#ef4444"}}><AlertTriangle size={18} /></div></div>
            <h2>0.42%</h2>
            <div className="stat-change negative"><Zap size={14} fill="currentColor" /> +0.12% <span style={{color:"#64748b"}}>vs previous period</span></div>
          </div>
          <div className="stat-card">
            <div className="stat-top">Estimated API Cost <div className="stat-icon"><CircleDollarSign size={18} /></div></div>
            <h2>$248.50</h2>
            <div className="stat-change positive"><Zap size={14} fill="currentColor" /> +5.6% <span style={{color:"#64748b"}}>vs previous period</span></div>
          </div>
        </div>

        {/* CHARTS & HEALTH */}
        <div className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>API Traffic Overview</h3>
                <p>Request volume over time</p>
              </div>
              <div className="chart-legend"><span></span> API Requests</div>
            </div>
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trafficData}>
                  <defs>
                    <linearGradient id="colorReq" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0f766e" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0f766e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill:"#64748b", fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill:"#64748b", fontSize: 12}} tickFormatter={(val) => `${val/1000}k`} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }} />
                  <Area type="monotone" dataKey="requests" stroke="#0f766e" strokeWidth={2} fillOpacity={1} fill="url(#colorReq)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>System Health</h3>
                <p>Current infrastructure status</p>
              </div>
            </div>
            <div className="health-status">
              <div className="health-icon"><ShieldCheck size={32} /></div>
              <h2>All Systems Normal</h2>
              <p>All monitored services are operational.</p>
            </div>
            <div className="health-row"><span>API Availability</span><strong>99.98%</strong></div>
            <div className="health-row"><span>Active Endpoints</span><strong>48</strong></div>
            <div className="health-row"><span>Active Alerts</span><strong style={{color: "#d97706"}}>3</strong></div>
          </div>
        </div>

        {/* TABLE */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Recent API Activity</h3>
              <p>Latest 5 requests across your endpoints</p>
            </div>
            <button style={{ background: "none", border: "none", color: "#0f766e", fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center" }}>
              View all <ChevronRight size={16} />
            </button>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>METHOD</th><th>ENDPOINT</th><th>STATUS</th><th>LATENCY</th>
                </tr>
              </thead>
              <tbody>
                {recentActivity.map((item, i) => (
                  <tr key={i}>
                    <td><span className={`method ${item.method.toLowerCase()}`}>{item.method}</span></td>
                    <td style={{ fontWeight: 500 }}>{item.endpoint}</td>
                    <td><span className={item.status === "200" ? "success-badge" : "error-badge"}>{item.status}</span></td>
                    <td><span className="latency"><Clock3 size={14} /> {item.latency}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
