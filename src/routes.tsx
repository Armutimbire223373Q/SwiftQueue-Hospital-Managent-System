import { RouteObject } from "react-router-dom";
import HomePage from "./components/HomePage";
import Dashboard from "./components/Dashboard";
import QueuePage from "./components/QueuePage";
import AdminPanelSimple from "./components/AdminPanelSimple";
import Analytics from "./components/Analytics";

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <HomePage />
  },
  {
    path: "/dashboard",
    element: <Dashboard />
  },
  {
    path: "/queue",
    element: <QueuePage />
  },
  {
    path: "/admin",
    element: <AdminPanelSimple />
  },
  {
    path: "/analytics",
    element: <Analytics />
  }
];
