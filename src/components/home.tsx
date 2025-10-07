import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Monitor, 
  Users, 
  Settings, 
  Clock, 
  Brain, 
  Smartphone,
  BarChart3,
  CheckCircle,
  Heart,
  Stethoscope,
  Activity,
  Shield,
  AlertTriangle,
  UserCheck
} from "lucide-react";

export default function Home() {
  const isGuestSession = localStorage.getItem('isGuestSession') === 'true';
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  
  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Guest Session Alert */}
        {isGuestSession && (
          <Alert className="mb-6 border-blue-200 bg-blue-50">
            <UserCheck className="h-4 w-4" />
            <AlertDescription>
              <strong>Guest Mode:</strong> You're browsing as a guest user. 
              {user?.name === 'Emergency Patient' && (
                <span className="text-red-600 font-semibold"> Emergency access enabled.</span>
              )}
              <Link to="/register" className="ml-2 text-blue-600 hover:underline">
                Create an account for full features
              </Link>
            </AlertDescription>
          </Alert>
        )}

        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mr-4">
              <Stethoscope className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900">SwiftQueue Hospital</h1>
          </div>
          <p className="text-xl text-gray-600 mb-2">AI-Powered Hospital Queue Management System</p>
          <p className="text-gray-500">Optimize patient flow and reduce waiting times with intelligent healthcare management</p>
        </div>

        {/* Key Features */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">AI Patient Flow</h3>
              <p className="text-sm text-gray-600">Smart patient routing and treatment time predictions</p>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Smartphone className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">Smart Notifications</h3>
              <p className="text-sm text-gray-600">Automated patient alerts and appointment reminders</p>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Monitor className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">Real-time Monitoring</h3>
              <p className="text-sm text-gray-600">Live patient queue and department status tracking</p>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-6 w-6 text-orange-600" />
              </div>
              <h3 className="font-semibold mb-2">Healthcare Analytics</h3>
              <p className="text-sm text-gray-600">Patient flow insights and resource optimization</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Navigation */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* Patient Registration */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5 text-blue-600" />
                  <span>Patient Registration</span>
                </CardTitle>
                <Badge variant="secondary">Patients</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-600">Register for medical services and join digital queues</p>
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  Select medical department
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  AI-powered wait time prediction
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  Smart appointment notifications
                </div>
              </div>
              <Link to="/queue">
                <Button className="w-full">
                  Register for Service
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Hospital Dashboard */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <Monitor className="h-5 w-5 text-green-600" />
                  <span>Hospital Dashboard</span>
                </CardTitle>
                <Badge variant="outline">Medical Staff</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-600">Monitor patient flow and department operations</p>
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  Real-time patient queues
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  AI treatment time predictions
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  Department status monitoring
                </div>
              </div>
              <Link to="/dashboard">
                <Button variant="outline" className="w-full">
                  View Dashboard
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Admin Control */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5 text-purple-600" />
                  <span>Admin Control</span>
                </CardTitle>
                <Badge variant="destructive">Administrators</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-600">Manage hospital resources and AI optimization</p>
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  Medical staff management
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  Service area configuration
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  AI analytics and insights
                </div>
              </div>
              <Link to="/admin">
                <Button variant="secondary" className="w-full">
                  Admin Panel
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Hospital Departments */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Available Departments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-red-600 mx-auto mb-2" />
                <p className="text-sm font-medium">Emergency</p>
                <p className="text-xs text-gray-600">24/7 Care</p>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <Heart className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                <p className="text-sm font-medium">Cardiology</p>
                <p className="text-xs text-gray-600">Heart Care</p>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <Stethoscope className="h-6 w-6 text-green-600 mx-auto mb-2" />
                <p className="text-sm font-medium">General</p>
                <p className="text-xs text-gray-600">Primary Care</p>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <Activity className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                <p className="text-sm font-medium">Laboratory</p>
                <p className="text-xs text-gray-600">Diagnostics</p>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg">
                <Monitor className="h-6 w-6 text-orange-600 mx-auto mb-2" />
                <p className="text-sm font-medium">Radiology</p>
                <p className="text-xs text-gray-600">Imaging</p>
              </div>
              <div className="text-center p-3 bg-pink-50 rounded-lg">
                <Users className="h-6 w-6 text-pink-600 mx-auto mb-2" />
                <p className="text-sm font-medium">Pediatrics</p>
                <p className="text-xs text-gray-600">Child Care</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Current Status */}
        <Card className="bg-white/80 backdrop-blur-sm mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-blue-600" />
              <span>AI-Powered Hospital Status</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">12</div>
                <div className="text-sm text-gray-600">Patients Waiting</div>
                <div className="text-xs text-blue-500">AI Optimized</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">6</div>
                <div className="text-sm text-gray-600">Active Departments</div>
                <div className="text-xs text-green-500">Fully Operational</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">18m</div>
                <div className="text-sm text-gray-600">Avg Wait Time</div>
                <div className="text-xs text-purple-500">AI Predicted</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">92%</div>
                <div className="text-sm text-gray-600">Efficiency Score</div>
                <div className="text-xs text-orange-500">AI Optimized</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Features Highlight */}
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4 mb-4">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Advanced AI Integration</h3>
                <p className="text-sm text-gray-600">
                  Our AI system continuously learns from patient patterns to optimize healthcare delivery
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-white p-3 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-1">Predictive Analytics</h4>
                <p className="text-blue-700">Forecasts patient flow and resource needs</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <h4 className="font-medium text-purple-900 mb-1">Smart Scheduling</h4>
                <p className="text-purple-700">Optimizes appointments and reduces wait times</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <h4 className="font-medium text-green-900 mb-1">Resource Optimization</h4>
                <p className="text-green-700">Balances staff workload and equipment usage</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Access Points for Different User Types */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">Patient Access</h3>
              <p className="text-sm text-gray-600 mb-4">Join queue, check status, emergency access</p>
              <div className="space-y-2">
                <Link to="/register">
                  <Button className="w-full">Register as Patient</Button>
                </Link>
                <Link to="/login">
                  <Button variant="outline" className="w-full">Patient Login</Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Stethoscope className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Medical Staff</h3>
              <p className="text-sm text-gray-600 mb-4">Manage queues, patient flow, triage</p>
              <div className="space-y-2">
                <Link to="/login?role=staff">
                  <Button variant="outline" className="w-full bg-blue-50 hover:bg-blue-100">
                    Staff Login
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Settings className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">Administration</h3>
              <p className="text-sm text-gray-600 mb-4">System management, analytics, reports</p>
              <div className="space-y-2">
                <Link to="/login?role=admin">
                  <Button variant="outline" className="w-full bg-purple-50 hover:bg-purple-100">
                    Admin Login
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p className="text-sm">SwiftQueue Hospital - AI-Powered Healthcare Management System</p>
          <p className="text-xs mt-1">Improving patient care through intelligent queue management</p>
        </div>
      </div>
    </div>
  );
}