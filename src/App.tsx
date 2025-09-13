import { Suspense } from "react";
import { useRoutes, Routes, Route } from "react-router-dom";
import Home from "./components/home";
import QueueDashboard from "./components/queue-dashboard";
import CustomerQueue from "./components/customer-queue";
import AdminPanel from "./components/admin-panel";
import QueueAnalytics from "./components/QueueAnalyticsNew";
import { Toaster } from "./components/ui/toaster";
import routes from "tempo-routes";

function App() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-primary"></div>
      </div>
    }>
      <>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<QueueDashboard />} />
          <Route path="/queue" element={<CustomerQueue />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/analytics" element={<QueueAnalytics />} />
        </Routes>
        <Toaster />
        {import.meta.env.VITE_TEMPO === "true" && useRoutes(routes)}
      </>
    </Suspense>
  );
}

export default App;