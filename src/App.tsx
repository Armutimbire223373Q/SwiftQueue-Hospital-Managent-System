import { Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./components/home";
import QueueDashboard from "./components/queue-dashboard";
import CustomerQueue from "./components/customer-queue";
import AdminPanel from "./components/admin-panel";
import QueueAnalytics from "./components/QueueAnalyticsNew";
import LoginForm from "./components/auth/LoginForm";
import RegisterForm from "./components/auth/RegisterForm";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import AppointmentBooking from "./components/appointment-booking";
import AppointmentManagement from "./components/appointment-management";
import PatientCheckin from "./components/patient-checkin";
import NotificationCenter from "./components/notification-center";
import HospitalNavigation from "./components/hospital-navigation";
import { Toaster } from "./components/ui/toaster";

function App() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-primary"></div>
      </div>
    }>
      <>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Home />} />
          <Route
            path="/login"
            element={
              <ProtectedRoute requireAuth={false}>
                <LoginForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/register"
            element={
              <ProtectedRoute requireAuth={false}>
                <RegisterForm />
              </ProtectedRoute>
            }
          />
          
          {/* Guest/Emergency access route */}
          <Route path="/join-queue" element={<CustomerQueue />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <QueueDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/queue"
            element={
              <ProtectedRoute>
                <CustomerQueue />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminPanel />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <QueueAnalytics />
              </ProtectedRoute>
            }
          />
          <Route
            path="/appointments"
            element={
              <ProtectedRoute>
                <AppointmentManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/book-appointment"
            element={
              <ProtectedRoute>
                <AppointmentBooking />
              </ProtectedRoute>
            }
          />
          <Route
            path="/checkin"
            element={
              <ProtectedRoute>
                <PatientCheckin />
              </ProtectedRoute>
            }
          />
          <Route
            path="/notifications"
            element={
              <ProtectedRoute>
                <NotificationCenter />
              </ProtectedRoute>
            }
          />
          <Route
            path="/navigation"
            element={
              <ProtectedRoute>
                <HospitalNavigation />
              </ProtectedRoute>
            }
          />
        </Routes>
        <Toaster />
      </>
    </Suspense>
  );
}

export default App;