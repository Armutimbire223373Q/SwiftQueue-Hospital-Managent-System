import { Link } from "react-router-dom";
import {
  Stethoscope,
  Brain,
  Smartphone,
  Monitor,
  BarChart3,
  Users,
  Settings,
  Clock,
  Heart,
  Activity,
  Shield,
  CheckCircle,
  Star,
  ArrowRight,
  Zap,
  Award
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            {/* Logo and Title */}
            <div className="flex items-center justify-center mb-8">
              <div className="relative">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-2xl">
                  <Stethoscope className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center">
                  <Zap className="h-4 w-4 text-yellow-800" />
                </div>
              </div>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                SwiftQueue
              </span>
              <br />
              <span className="text-gray-800">Hospital</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 mb-4 max-w-3xl mx-auto">
              AI-Powered Hospital Queue Management System
            </p>

            <p className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto">
              Optimize patient flow and reduce waiting times with intelligent healthcare management
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Link
                to="/register"
                className="group bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-8 py-4 rounded-2xl font-semibold text-lg shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/dashboard"
                className="bg-white/80 backdrop-blur-sm border-2 border-gray-200 hover:border-blue-300 text-gray-700 hover:text-blue-600 px-8 py-4 rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center"
              >
                View Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Revolutionary Healthcare Technology
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience the future of hospital management with our AI-powered solutions
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature Cards */}
            <div className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 border border-gray-100">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">AI Patient Flow</h3>
              <p className="text-gray-600 leading-relaxed">
                Smart patient routing and treatment time predictions powered by advanced machine learning
              </p>
            </div>

            <div className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 border border-gray-100">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Smartphone className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Smart Notifications</h3>
              <p className="text-gray-600 leading-relaxed">
                Automated patient alerts and appointment reminders with intelligent scheduling
              </p>
            </div>

            <div className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 border border-gray-100">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Monitor className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Real-time Monitoring</h3>
              <p className="text-gray-600 leading-relaxed">
                Live patient queue tracking and department status monitoring with instant updates
              </p>
            </div>

            <div className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 border border-gray-100">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <BarChart3 className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Healthcare Analytics</h3>
              <p className="text-gray-600 leading-relaxed">
                Comprehensive patient flow insights and resource optimization analytics
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Role-Based Access Section */}
      <div className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Choose Your Access Level
            </h2>
            <p className="text-xl text-blue-100 max-w-2xl mx-auto">
              SwiftQueue adapts to your role with personalized dashboards and tools
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Patient Card */}
            <div className="group bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:scale-105">
              <div className="text-center">
                <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Users className="h-10 w-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Patients</h3>
                <p className="text-blue-100 mb-6 leading-relaxed">
                  Join digital queues, track your position, receive smart notifications, and access emergency services
                </p>
                <div className="space-y-3 mb-8">
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>Digital queue registration</span>
                  </div>
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>Real-time queue status</span>
                  </div>
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>AI wait time predictions</span>
                  </div>
                </div>
                <Link
                  to="/register"
                  className="inline-flex items-center bg-white text-blue-600 px-6 py-3 rounded-xl font-semibold hover:bg-blue-50 transition-colors duration-300"
                >
                  Register as Patient
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </div>
            </div>

            {/* Staff Card */}
            <div className="group bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:scale-105">
              <div className="text-center">
                <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Stethoscope className="h-10 w-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Medical Staff</h3>
                <p className="text-blue-100 mb-6 leading-relaxed">
                  Manage patient queues, monitor department operations, and optimize healthcare delivery
                </p>
                <div className="space-y-3 mb-8">
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>Live queue management</span>
                  </div>
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>AI-powered insights</span>
                  </div>
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>Department monitoring</span>
                  </div>
                </div>
                <Link
                  to="/dashboard"
                  className="inline-flex items-center bg-white text-blue-600 px-6 py-3 rounded-xl font-semibold hover:bg-blue-50 transition-colors duration-300"
                >
                  Access Dashboard
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </div>
            </div>

            {/* Admin Card */}
            <div className="group bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:scale-105">
              <div className="text-center">
                <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                  <Settings className="h-10 w-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Administrators</h3>
                <p className="text-blue-100 mb-6 leading-relaxed">
                  Configure hospital settings, manage staff, and oversee AI optimization systems
                </p>
                <div className="space-y-3 mb-8">
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>Staff management</span>
                  </div>
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>System configuration</span>
                  </div>
                  <div className="flex items-center text-blue-100">
                    <CheckCircle className="h-5 w-5 mr-3 text-green-300" />
                    <span>AI analytics oversight</span>
                  </div>
                </div>
                <Link
                  to="/admin"
                  className="inline-flex items-center bg-white text-blue-600 px-6 py-3 rounded-xl font-semibold hover:bg-blue-50 transition-colors duration-300"
                >
                  Admin Panel
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Trusted by Healthcare Professionals
            </h2>
            <p className="text-xl text-gray-600">
              Join thousands of hospitals optimizing patient care with SwiftQueue
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">500+</div>
              <div className="text-gray-600">Hospitals</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">2M+</div>
              <div className="text-gray-600">Patients Served</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2">45%</div>
              <div className="text-gray-600">Wait Time Reduction</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-orange-600 mb-2">98%</div>
              <div className="text-gray-600">Satisfaction Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mr-3">
                <Stethoscope className="h-6 w-6 text-white" />
              </div>
              <span className="text-2xl font-bold">SwiftQueue Hospital</span>
            </div>
            <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
              Revolutionizing healthcare with AI-powered queue management and intelligent patient flow optimization
            </p>
            <div className="flex items-center justify-center space-x-6 text-sm text-gray-400">
              <span>© 2024 SwiftQueue Hospital</span>
              <span>•</span>
              <span>AI-Powered Healthcare Solutions</span>
              <span>•</span>
              <span>Improving Patient Care Worldwide</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}