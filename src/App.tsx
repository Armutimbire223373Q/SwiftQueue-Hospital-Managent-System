import { Routes, Route } from "react-router-dom";
import HomePage from "./components/HomePage";
import Dashboard from "./components/Dashboard";
import QueuePage from "./components/QueuePage";
import AdminPanelSimple from "./components/AdminPanelSimple";
import Analytics from "./components/Analytics";
import StaffPortal from "./components/StaffPortal";
import DepartmentPortal from "./components/DepartmentPortal";
import AdminDashboard from "./components/AdminDashboard";
import ReceptionistPortal from "./components/ReceptionistPortal";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/queue" element={<QueuePage />} />
      <Route path="/admin" element={<AdminPanelSimple />} />
      <Route path="/admin-dashboard" element={<AdminDashboard />} />
      <Route path="/staff-portal" element={<StaffPortal />} />
      <Route path="/department/:id" element={<DepartmentPortal />} />
      <Route path="/receptionist-portal" element={<ReceptionistPortal />} />
      <Route path="/analytics" element={<Analytics />} />
    </Routes>
  );
}

export default App;