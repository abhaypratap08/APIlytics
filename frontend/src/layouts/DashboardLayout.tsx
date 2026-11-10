
import { NavLink, Outlet } from "react-router-dom";
import {
  Activity,
  LayoutDashboard,
  Network,
  ShieldCheck,
  CircleDollarSign,
  Bell,
  Settings,
} from "lucide-react";

function DashboardLayout() {
  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Activity size={23} />
          </div>
          <span>APIlytics</span>
        </div>

        <div className="workspace">
          <span className="workspace-dot"></span>
          Production Workspace
        </div>

        <p className="nav-label">OVERVIEW</p>

        <nav className="navigation">
          <NavLink to="/" end className={({ isActive }) =>
            `nav-item ${isActive ? "active" : ""}`
          }>
            <LayoutDashboard size={19} />
            Dashboard
          </NavLink>

          <NavLink to="/monitoring" className={({ isActive }) =>
            `nav-item ${isActive ? "active" : ""}`
          }>
            <Network size={19} />
            API Monitoring
          </NavLink>

          <NavLink to="/anomalies" className={({ isActive }) =>
            `nav-item ${isActive ? "active" : ""}`
          }>
            <ShieldCheck size={19} />
            Anomaly Detection
          </NavLink>

          <NavLink to="/cost-intelligence" className={({ isActive }) =>
            `nav-item ${isActive ? "active" : ""}`
          }>
            <CircleDollarSign size={19} />
            Cost Intelligence
          </NavLink>
        </nav>

        <p className="nav-label">PREFERENCES</p>

        <nav className="navigation">
          <a href="#alerts" className="nav-item">
            <Bell size={19} />
            Alerts
          </a>

          <a href="#settings" className="nav-item">
            <Settings size={19} />
            Settings
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="avatar">JS</div>
          <div>
            <strong>Jay Singh</strong>
            <small>Frontend Developer</small>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

export default DashboardLayout;
