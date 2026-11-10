
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Bell,
  CircleDollarSign,
  Clock3,
  LayoutDashboard,
  Network,
  Search,
  Settings,
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

const trafficData = [
  { time: "09:00", requests: 1200 },
  { time: "10:00", requests: 2100 },
  { time: "11:00", requests: 1800 },
  { time: "12:00", requests: 3200 },
  { time: "13:00", requests: 2700 },
  { time: "14:00", requests: 4100 },
  { time: "15:00", requests: 3600 },
  { time: "16:00", requests: 5200 },
  { time: "17:00", requests: 4500 },
];

const activities = [
  { method: "GET", endpoint: "/api/users", status: "200", latency: "124ms" },
  { method: "POST", endpoint: "/api/auth/login", status: "200", latency: "210ms" },
  { method: "GET", endpoint: "/api/products", status: "200", latency: "98ms" },
  { method: "DELETE", endpoint: "/api/orders/42", status: "500", latency: "430ms" },
  { method: "GET", endpoint: "/api/analytics", status: "200", latency: "156ms" },
];

function Dashboard() {
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

        <section className="welcome-section">
          <div>
            <h1>Welcome back, Jay 👋</h1>
            <p>Here's what's happening with your APIs today.</p>
          </div>
          <button className="date-button">Last 24 hours ▾</button>
        </section>

        <section className="stats-grid">
          <StatCard
            title="Total API Requests"
            value="1.28M"
            change="+12.8%"
            icon={<Activity />}
            positive
          />
          <StatCard
            title="Avg. Response Time"
            value="142 ms"
            change="-8.2%"
            icon={<Zap />}
            positive
          />
          <StatCard
            title="Error Rate"
            value="0.42%"
            change="+0.12%"
            icon={<AlertTriangle />}
          />
          <StatCard
            title="Estimated API Cost"
            value="$248.50"
            change="-5.4%"
            icon={<CircleDollarSign />}
            positive
          />
        </section>

        <section className="content-grid">
          <div className="panel traffic-panel">
            <div className="panel-header">
              <div>
                <h3>API Traffic Overview</h3>
                <p>Request volume over time</p>
              </div>
              <span className="chart-legend">
                <span></span> API Requests
              </span>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trafficData}>
                  <defs>
                    <linearGradient
                      id="trafficGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    stroke="#252b3b"
                    strokeDasharray="4 4"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="time"
                    stroke="#788198"
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#788198"
                    tickLine={false}
                    axisLine={false}
                  />
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
              <strong>99.98%</strong>
            </div>
            <div className="health-row">
              <span>Active Endpoints</span>
              <strong>48</strong>
            </div>
            <div className="health-row">
              <span>Active Alerts</span>
              <strong className="warning-text">3</strong>
            </div>
          </div>
        </section>

        <section className="panel activity-panel">
          <div className="panel-header">
            <div>
              <h3>Recent API Activity</h3>
              <p>Latest requests across your endpoints</p>
            </div>
            <button className="view-button">View all →</button>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>METHOD</th>
                  <th>ENDPOINT</th>
                  <th>STATUS</th>
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
                    <td className="endpoint">{item.endpoint}</td>
                    <td>
                      <span
                        className={
                          item.status === "200" ? "success-badge" : "error-badge"
                        }
                      >
                        {item.status}
                      </span>
                    </td>
                    <td>
                      <span className="latency">
                        <Clock3 size={14} /> {item.latency}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

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
      <div className="stat-change">
        {positive ? (
          <ArrowUpRight size={16} />
        ) : (
          <ArrowDownRight size={16} />
        )}
        <strong className={positive ? "positive" : "negative"}>
          {change}
        </strong>
        <span>vs previous period</span>
      </div>
    </div>
  );
}

export default Dashboard;
