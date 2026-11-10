
import { BrowserRouter, Routes, Route } from "react-router-dom";

import DashboardLayout from "./layouts/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import ApiMonitoring from "./pages/ApiMonitoring";
import Anomalies from "./pages/Anomalies";
import CostIntelligence from "./pages/CostIntelligence";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/monitoring" element={<ApiMonitoring />} />
          <Route path="/anomalies" element={<Anomalies />} />
          <Route path="/cost-intelligence" element={<CostIntelligence />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
