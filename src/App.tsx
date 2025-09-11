import { Suspense } from "react";
import { useRoutes, Routes, Route } from "react-router-dom";
import Home from "./components/home";
import QueueDashboard from "./components/queue-dashboard";
import CustomerQueue from "./components/customer-queue";
import AdminPanel from "./components/admin-panel";
import routes from "tempo-routes";

function App() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<QueueDashboard />} />
          <Route path="/queue" element={<CustomerQueue />} />
          <Route path="/admin" element={<AdminPanel />} />
        </Routes>
        {import.meta.env.VITE_TEMPO === "true" && useRoutes(routes)}
      </>
    </Suspense>
  );
}

export default App;