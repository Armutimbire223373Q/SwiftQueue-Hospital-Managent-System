import React, { useState, useEffect } from 'react';
import { wsService } from '@/services/wsService';
import { apiService } from '@/services/apiService';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Switch } from "@/components/ui/switch";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Crown,
  UserPlus,
  Calendar,
  CheckCircle,
  Clock,
  Database,
  Download,
  Edit,
  MapPin,
  Menu,
  Plus,
  RefreshCw,
  Search,
  Shield,
  Settings,
  User,
  UserCheck,
  Users,
  X,
  XCircle
} from 'lucide-react';

// Type definitions
interface DashboardStats {
  total_users: number;
  active_users: number;
  total_staff: number;
  active_staff: number;
  total_patients: number;
  active_patients: number;
  total_services: number;
  active_services: number;
  total_queues: number;
  total_queue_entries: number;
  avg_wait_time: number;
  patient_satisfaction: number;
  system_uptime: number;
  system_health: string;
  total_appointments_today: number;
  completed_appointments_today: number;
}

interface UserManagement {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
  department?: string;
}

interface SystemSetting {
  id: number;
  setting_key: string;
  setting_value: any;
  setting_type: string;
  category?: string;
  description?: string;
  updated_at: string;
}

interface AuditLog {
  id: number;
  user_id: number;
  action: string;
  resource_type: string;
  resource_id?: number;
  changes?: any;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
  timestamp?: string;
  success?: boolean;
  error_message?: string;
}
              
interface Department {
  id: number;
  name: string;
  description: string | null;
  head_id: number | null;
  staff_count: number;
  is_active: boolean;
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Dashboard data
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [users, setUsers] = useState<UserManagement[]>([]);
  const [settings, setSettings] = useState<SystemSetting[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);

  // UI state
  const [showUserDialog, setShowUserDialog] = useState(false);
  const [showSettingDialog, setShowSettingDialog] = useState(false);
  const [showDepartmentDialog, setShowDepartmentDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserManagement | null>(null);
  const [selectedSetting, setSelectedSetting] = useState<SystemSetting | null>(null);

  // Search and filter state
  const [userSearchTerm, setUserSearchTerm] = useState("");
  const [userRoleFilter, setUserRoleFilter] = useState<string>("all");
  const [userStatusFilter, setUserStatusFilter] = useState<string>("all");
  const [userDepartmentFilter, setUserDepartmentFilter] = useState<string>("all");

  // Real-time updates
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [liveNotifications, setLiveNotifications] = useState<any[]>([]);
  // Mock live queue items for quick dev view
  const [liveQueueItems, setLiveQueueItems] = useState<Array<any>>([
    { id: 1, ticket: 'A101', patient_name: 'John Smith', service: 'Registration', wait_seconds: 120 },
    { id: 2, ticket: 'A102', patient_name: 'Jane Doe', service: 'Triage', wait_seconds: 300 },
    { id: 3, ticket: 'A103', patient_name: 'Sam Lee', service: 'Consultation', wait_seconds: 45 }
  ]);

  // Mobile responsiveness
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Form state
  const [userForm, setUserForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'patient',
    is_active: true
  });

  const [settingForm, setSettingForm] = useState({
    setting_key: '',
    setting_value: '',
    setting_type: 'string',
    category: 'system',
    description: ''
  });

  const [departmentForm, setDepartmentForm] = useState({
    name: '',
    description: '',
    head_id: '',
    budget_allocated: '',
    color_code: '',
    icon_name: ''
  });

  useEffect(() => {
    loadInitialData();

    // Check if mobile device
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      setSidebarCollapsed(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    // Set up WebSocket connection for real-time updates
    const connectWebSocket = async () => {
      // Try to connect, but don't throw — we want the UI to work even if WS is down.
      try {
        await wsService.connect();
      } catch (err) {
        // connection failed; backend may not be running. Keep UI functional.
        console.debug('wsService.connect() failed:', err);
      }

      // Subscribe to updates regardless; wsService will handle background reconnect attempts.
      const unsubscribe = wsService.subscribe((data) => {
        if (data.type === 'stats_update') {
          setStats(data.stats);
          setLastUpdate(new Date());
        } else if (data.type === 'notification') {
          setLiveNotifications(prev => [data.notification, ...prev.slice(0, 9)]); // Keep last 10
        } else if (data.type === 'user_update') {
          loadUsers(); // Refresh user list
        } else if (data.type === 'queue_update') {
          loadDashboardStats(); // Refresh stats
        }
      });

      // Update connection indicator based on wsService state
      setIsConnected(wsService.isConnected);

      // Set up periodic refresh as fallback (single interval)
      const interval = setInterval(() => {
        if (!wsService.isConnected) {
          loadDashboardStats();
          setLastUpdate(new Date());
        }
      }, 30000); // 30 seconds fallback

      return () => {
        clearInterval(interval);
        window.removeEventListener('resize', checkMobile);
        unsubscribe();
        wsService.disconnect();
      };
    };

    const cleanup = connectWebSocket();
    return () => {
      cleanup?.then(cleanupFn => cleanupFn?.());
    };
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      await Promise.all([
        loadDashboardStats(),
        loadUsers(),
        loadSystemSettings(),
        loadAuditLogs(),
        loadDepartments()
      ]);
    } catch (err) {
      setError("Failed to load admin data");
      console.error("Error loading admin data:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardStats = async () => {
    try {
      // Mock data for demonstration since backend endpoints may not be fully implemented
      const mockStats: DashboardStats = {
        total_users: 245,
        active_users: 189,
        total_staff: 42,
        active_staff: 38,
        total_patients: 156,
        active_patients: 89,
        total_services: 12,
        active_services: 10,
        total_queues: 8,
        total_queue_entries: 45,
        total_appointments_today: 67,
        completed_appointments_today: 45,
        avg_wait_time: 18.5,
        patient_satisfaction: 4.5,
        system_uptime: 99.8,
        system_health: 'healthy'
      };
      setStats(mockStats);
    } catch (err) {
      console.error("Error loading dashboard stats:", err);
    }
  };

  const loadUsers = async () => {
    try {
      // Mock user data for demonstration
      const mockUsers = [
        {
          id: 1,
          name: "Dr. Sarah Johnson",
          email: "sarah.johnson@hospital.com",
          role: "staff",
          is_active: true,
          created_at: "2024-01-15T08:00:00Z",
          last_login: "2024-12-12T09:30:00Z",
          has_staff_profile: true,
          department: "Emergency Medicine"
        },
        {
          id: 2,
          name: "Dr. Michael Chen",
          email: "michael.chen@hospital.com",
          role: "staff",
          is_active: true,
          created_at: "2024-02-20T10:15:00Z",
          last_login: "2024-12-12T08:45:00Z",
          has_staff_profile: true,
          department: "Internal Medicine"
        },
        {
          id: 3,
          name: "Nurse Emily Davis",
          email: "emily.davis@hospital.com",
          role: "staff",
          is_active: true,
          created_at: "2024-03-10T14:20:00Z",
          last_login: "2024-12-12T07:15:00Z",
          has_staff_profile: true,
          department: "Emergency Medicine"
        },
        {
          id: 4,
          name: "Admin User",
          email: "admin@hospital.com",
          role: "admin",
          is_active: true,
          created_at: "2024-01-01T00:00:00Z",
          last_login: "2024-12-12T10:00:00Z",
          has_staff_profile: true,
          department: "Administration"
        },
        {
          id: 5,
          name: "John Smith",
          email: "john.smith@email.com",
          role: "patient",
          is_active: true,
          created_at: "2024-06-15T16:30:00Z",
          last_login: "2024-12-11T14:20:00Z",
          has_staff_profile: false,
          department: null
        },
        {
          id: 6,
          name: "Jane Doe",
          email: "jane.doe@email.com",
          role: "patient",
          is_active: false,
          created_at: "2024-08-22T11:45:00Z",
          last_login: null,
          has_staff_profile: false,
          department: null
        }
      ];
      setUsers(mockUsers);
    } catch (err) {
      console.error("Error loading users:", err);
    }
  };

  const loadSystemSettings = async () => {
    try {
      // Mock system settings for demonstration
      const mockSettings: SystemSetting[] = [
        {
          id: 1,
          setting_key: "maintenance_mode",
          setting_value: "false",
          setting_type: "boolean",
          category: "system",
          description: "Enable maintenance mode",
          updated_at: new Date().toISOString()
        },
        {
          id: 2,
          setting_key: "max_queue_size",
          setting_value: "100",
          setting_type: "integer",
          category: "queue",
          description: "Maximum queue size per service",
          updated_at: new Date().toISOString()
        },
        {
          id: 3,
          setting_key: "auto_call_delay",
          setting_value: "30",
          setting_type: "integer",
          category: "queue",
          description: "Auto-call next patient delay (seconds)",
          updated_at: new Date().toISOString()
        },
        {
          id: 4,
          setting_key: "emergency_response_timeout",
          setting_value: "15",
          setting_type: "integer",
          category: "emergency",
          description: "Emergency response timeout (minutes)",
          updated_at: new Date().toISOString()
        },
        {
          id: 5,
          setting_key: "max_upload_size_mb",
          setting_value: "10",
          setting_type: "integer",
          category: "system",
          description: "Maximum file upload size in MB",
          updated_at: new Date().toISOString()
        },
        {
          id: 6,
          setting_key: "session_timeout_minutes",
          setting_value: "60",
          setting_type: "integer",
          category: "security",
          description: "User session timeout in minutes",
          updated_at: new Date().toISOString()
        }
      ];
      setSettings(mockSettings);
    } catch (err) {
      console.error("Error loading system settings:", err);
    }
  };

  const loadAuditLogs = async () => {
    try {
      // Mock audit logs for demonstration
      const mockAuditLogs: AuditLog[] = [
        {
          id: 1,
          user_id: 4,
          action: "LOGIN",
          resource_type: "auth",
          resource_id: undefined,
          created_at: "2024-12-12T10:00:00Z",
          timestamp: "2024-12-12T10:00:00Z",
          success: true,
          error_message: undefined
        },
        {
          id: 2,
          user_id: 1,
          action: "CREATE",
          resource_type: "appointment",
          resource_id: 123,
          created_at: "2024-12-12T09:30:00Z",
          timestamp: "2024-12-12T09:30:00Z",
          success: true,
          error_message: undefined
        },
        {
          id: 3,
          user_id: 2,
          action: "UPDATE",
          resource_type: "patient",
          resource_id: 456,
          created_at: "2024-12-12T09:15:00Z",
          timestamp: "2024-12-12T09:15:00Z",
          success: true,
          error_message: undefined
        },
        {
          id: 4,
          user_id: 3,
          action: "DELETE",
          resource_type: "queue_entry",
          resource_id: 789,
          created_at: "2024-12-12T08:45:00Z",
          timestamp: "2024-12-12T08:45:00Z",
          success: false,
          error_message: "Permission denied"
        },
        {
          id: 5,
          user_id: 4,
          action: "UPDATE",
          resource_type: "system_settings",
          resource_id: undefined,
          created_at: "2024-12-12T08:30:00Z",
          timestamp: "2024-12-12T08:30:00Z",
          success: true,
          error_message: undefined
        }
      ];
      setAuditLogs(mockAuditLogs);
    } catch (err) {
      console.error("Error loading audit logs:", err);
    }
  };

  const loadDepartments = async () => {
    try {
      // Mock departments for demonstration
      const mockDepartments = [
        {
          id: 1,
          name: "Emergency Medicine",
          description: "Emergency and critical care services",
          head_id: 1,
          staff_count: 8,
          is_active: true
        },
        {
          id: 2,
          name: "Internal Medicine",
          description: "General internal medicine and diagnostics",
          head_id: 2,
          staff_count: 6,
          is_active: true
        },
        {
          id: 3,
          name: "Surgery",
          description: "Surgical procedures and post-operative care",
          head_id: null,
          staff_count: 4,
          is_active: true
        },
        {
          id: 4,
          name: "Pediatrics",
          description: "Child healthcare and development",
          head_id: null,
          staff_count: 3,
          is_active: true
        },
        {
          id: 5,
          name: "Radiology",
          description: "Medical imaging and diagnostics",
          head_id: null,
          staff_count: 2,
          is_active: true
        },
        {
          id: 6,
          name: "Laboratory",
          description: "Medical testing and pathology",
          head_id: null,
          staff_count: 3,
          is_active: true
        }
      ];
      setDepartments(mockDepartments);
    } catch (err) {
      console.error("Error loading departments:", err);
    }
  };

  const handleCreateUser = async () => {
    if (!userForm.name.trim() || !userForm.email.trim() || !userForm.password.trim()) {
      setError("Please fill in all required fields");
      return;
    }

    try {
      await apiService.post('/api/auth/register', userForm);
      setUserForm({ name: '', email: '', password: '', role: 'patient', is_active: true });
      setShowUserDialog(false);
      await loadUsers();
    } catch (err) {
      setError("Failed to create user");
      console.error("Error creating user:", err);
    }
  };

  const handleUpdateUserStatus = async (userId: number, isActive: boolean) => {
    try {
      await apiService.put(`/api/admin/users/${userId}/status`, { is_active: isActive });
      await loadUsers();
    } catch (err) {
      setError("Failed to update user status");
      console.error("Error updating user status:", err);
    }
  };

  const handleUpdateUserRole = async (userId: number, newRole: string) => {
    try {
      await apiService.put(`/api/admin/users/${userId}/role`, { new_role: newRole });
      await loadUsers();
    } catch (err) {
      setError("Failed to update user role");
      console.error("Error updating user role:", err);
    }
  };

  const handleUpdateSetting = async () => {
    if (!settingForm.setting_key.trim()) {
      setError("Please enter a setting key");
      return;
    }

    try {
      await apiService.put('/api/admin/settings', settingForm);
      setSettingForm({
        setting_key: '',
        setting_value: '',
        setting_type: 'string',
        category: 'system',
        description: ''
      });
      setShowSettingDialog(false);
      await loadSystemSettings();
    } catch (err) {
      setError("Failed to update system setting");
      console.error("Error updating system setting:", err);
    }
  };

  const handleCreateDepartment = async () => {
    if (!departmentForm.name.trim()) {
      setError("Please enter a department name");
      return;
    }

    try {
      await apiService.post('/api/admin/departments', departmentForm);
      setDepartmentForm({
        name: '',
        description: '',
        head_id: '',
        budget_allocated: '',
        color_code: '',
        icon_name: ''
      });
      setShowDepartmentDialog(false);
      await loadDepartments();
    } catch (err) {
      setError("Failed to create department");
      console.error("Error creating department:", err);
    }
  };

  // Filter and search functions
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(userSearchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(userSearchTerm.toLowerCase());
    const matchesRole = userRoleFilter === "all" || user.role === userRoleFilter;
    const matchesStatus = userStatusFilter === "all" ||
                         (userStatusFilter === "active" && user.is_active) ||
                         (userStatusFilter === "inactive" && !user.is_active);
    const matchesDepartment = userDepartmentFilter === "all" || user.department === userDepartmentFilter;

    return matchesSearch && matchesRole && matchesStatus && matchesDepartment;
  });

  const handleExportUsers = () => {
    const csvContent = [
      ["Name", "Email", "Role", "Status", "Department", "Last Login", "Created At"],
      ...filteredUsers.map(user => [
        user.name,
        user.email,
        user.role,
        user.is_active ? "Active" : "Inactive",
        user.department || "N/A",
        user.last_login ? new Date(user.last_login).toLocaleDateString() : "Never",
        new Date(user.created_at).toLocaleDateString()
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `users_export_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return <Crown className="h-4 w-4 text-purple-600" />;
      case 'staff': return <UserCheck className="h-4 w-4 text-blue-600" />;
      case 'patient': return <Users className="h-4 w-4 text-green-600" />;
      default: return <Users className="h-4 w-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="lg" text="Loading admin dashboard..." />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
            <p className="text-gray-600">Comprehensive system management and monitoring</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Live' : 'Offline'}
              </span>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">Last Update</div>
              <div className="text-sm font-medium">{lastUpdate.toLocaleTimeString()}</div>
            </div>
            <div className="flex items-center">
              <Button size="sm" variant="ghost" onClick={async () => {
                try {
                  await wsService.connect();
                  setIsConnected(wsService.isConnected);
                } catch (err) {
                  console.debug('Reconnect attempt failed', err);
                }
              }}>
                Reconnect
              </Button>
            </div>
          </div>
        </div>

        {/* Live Notifications Banner */}
        {liveNotifications.length > 0 && (
          <div className="mb-6">
            <Alert className="border-blue-200 bg-blue-50">
              <AlertTriangle className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <div className="flex items-center justify-between">
                  <span>
                    <strong>Live Update:</strong> {liveNotifications[0].message || 'System notification received'}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setLiveNotifications([])}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    Dismiss All
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          </div>
        )}

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className={`grid w-full ${isMobile ? 'grid-cols-3' : 'grid-cols-6'} gap-1`}>
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              {!isMobile && <span>Overview</span>}
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              {!isMobile && <span>Users</span>}
            </TabsTrigger>
            <TabsTrigger value="departments" className="flex items-center space-x-2">
              <Database className="h-4 w-4" />
              {!isMobile && <span>Departments</span>}
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              {!isMobile && <span>Settings</span>}
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center space-x-2">
              <Shield className="h-4 w-4" />
              {!isMobile && <span>Security</span>}
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center space-x-2">
              <Activity className="h-4 w-4" />
              {!isMobile && <span>System</span>}
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {stats && (
              <>
                {/* System Health */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Activity className="h-5 w-5" />
                      <span>System Health</span>
                      <Badge className={`ml-auto ${getHealthColor(stats.system_health)}`}>
                        {stats.system_health.toUpperCase()}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{stats.total_users}</div>
                        <div className="text-sm text-gray-600">Total Users</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{stats.active_users}</div>
                        <div className="text-sm text-gray-600">Active Users</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">{stats.total_queues}</div>
                        <div className="text-sm text-gray-600">Active Queues</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">{stats.avg_wait_time.toFixed(1)}m</div>
                        <div className="text-sm text-gray-600">Avg Wait Time</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Analytics Charts */}
                <div className={`grid gap-6 ${isMobile ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-2'}`}>
                  {/* Live Queue Panel - quick dev view */}
                  <div>
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                          <Activity className="h-5 w-5 text-indigo-600" />
                          <span>Live Queue</span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {liveQueueItems.slice(0,5).map(item => (
                            <div key={item.id} className="flex justify-between items-center border rounded p-2">
                              <div>
                                <div className="font-medium">{item.ticket} — {item.patient_name}</div>
                                <div className="text-sm text-gray-500">{item.service}</div>
                              </div>
                              <div className="text-sm text-gray-700">{Math.round(item.wait_seconds/60)}m {item.wait_seconds%60}s</div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                  {/* User Growth Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <TrendingUp className="h-5 w-5 text-green-600" />
                        <span>User Growth Trend</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <UserPlus className="h-4 w-4 text-green-600" />
                            <span className="text-sm font-medium">New Users This Month</span>
                          </div>
                          <span className="text-lg font-bold text-green-600">+12</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <TrendingUp className="h-4 w-4 text-blue-600" />
                            <span className="text-sm font-medium">Growth Rate</span>
                          </div>
                          <span className="text-lg font-bold text-blue-600">+8.5%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Calendar className="h-4 w-4 text-purple-600" />
                            <span className="text-sm font-medium">Active This Week</span>
                          </div>
                          <span className="text-lg font-bold text-purple-600">{stats.active_users}</span>
                        </div>
                      </div>
                      <div className={`mt-4 h-32 bg-gradient-to-r from-green-100 to-blue-100 rounded-lg flex items-center justify-center ${isMobile ? 'hidden' : ''}`}>
                        <div className="text-center">
                          <TrendingUp className="h-8 w-8 text-green-600 mx-auto mb-2" />
                          <p className="text-sm text-gray-600">Growth Chart</p>
                          <p className="text-xs text-gray-500">(Interactive chart would go here)</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Queue Performance Chart */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Clock className="h-5 w-5 text-orange-600" />
                        <span>Queue Performance</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Clock className="h-4 w-4 text-orange-600" />
                            <span className="text-sm font-medium">Avg Wait Time</span>
                          </div>
                          <span className="text-lg font-bold text-orange-600">{stats.avg_wait_time.toFixed(1)}m</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-sm font-medium">Queues Served Today</span>
                          </div>
                          <span className="text-lg font-bold text-green-600">{stats.total_queues}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <TrendingDown className="h-4 w-4 text-red-600" />
                            <span className="text-sm font-medium">Wait Time Trend</span>
                          </div>
                          <span className="text-lg font-bold text-red-600">-2.3%</span>
                        </div>
                      </div>
                      <div className={`mt-4 h-32 bg-gradient-to-r from-orange-100 to-red-100 rounded-lg flex items-center justify-center ${isMobile ? 'hidden' : ''}`}>
                        <div className="text-center">
                          <Clock className="h-8 w-8 text-orange-600 mx-auto mb-2" />
                          <p className="text-sm text-gray-600">Performance Chart</p>
                          <p className="text-xs text-gray-500">(Interactive chart would go here)</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Today's Activity */}
                <div className={`grid gap-6 ${isMobile ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2'}`}>
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Calendar className="h-5 w-5 text-blue-600" />
                        <span>Today's Appointments</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Total Scheduled</span>
                          <span className="text-lg font-semibold">{stats.total_appointments_today}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Completed</span>
                          <span className="text-lg font-semibold text-green-600">{stats.completed_appointments_today}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Completion Rate</span>
                          <span className="text-lg font-semibold">
                            {stats.total_appointments_today > 0
                              ? ((stats.completed_appointments_today / stats.total_appointments_today) * 100).toFixed(1)
                              : 0}%
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Pending</span>
                          <span className="text-lg font-semibold text-orange-600">
                            {stats.total_appointments_today - stats.completed_appointments_today}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <UserCheck className="h-5 w-5 text-green-600" />
                        <span>Staff Overview</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Total Staff</span>
                          <span className="text-lg font-semibold">{stats.total_staff}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Active Staff</span>
                          <span className="text-lg font-semibold text-green-600">{stats.active_staff}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Services</span>
                          <span className="text-lg font-semibold">{stats.active_services}/{stats.total_services}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Utilization</span>
                          <span className="text-lg font-semibold text-blue-600">
                            {stats.total_staff > 0 ? ((stats.active_staff / stats.total_staff) * 100).toFixed(1) : 0}%
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Quick Insights */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-indigo-600" />
                      <span>Quick Insights</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`grid gap-4 ${isMobile ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-3'}`}>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <CheckCircle className="h-5 w-5 text-green-600" />
                          <span className="font-medium text-green-800">Efficiency</span>
                        </div>
                        <p className="text-sm text-green-700">
                          System operating at {stats.total_appointments_today > 0 ? ((stats.completed_appointments_today / stats.total_appointments_today) * 100).toFixed(1) : 0}% completion rate
                        </p>
                      </div>
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Activity className="h-5 w-5 text-blue-600" />
                          <span className="font-medium text-blue-800">Activity</span>
                        </div>
                        <p className="text-sm text-blue-700">
                          {stats.active_users} active users with {stats.total_queues} queues in progress
                        </p>
                      </div>
                      <div className="bg-orange-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Clock className="h-5 w-5 text-orange-600" />
                          <span className="font-medium text-orange-800">Performance</span>
                        </div>
                        <p className="text-sm text-orange-700">
                          Average wait time of {stats.avg_wait_time.toFixed(1)} minutes across all services
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader className="space-y-4">
                <div className="flex justify-between items-center">
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="h-5 w-5" />
                    <span>User Management</span>
                  </CardTitle>
                  <div className="flex space-x-2">
                    <Button onClick={handleExportUsers} variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Export CSV
                    </Button>
                    <Dialog open={showUserDialog} onOpenChange={setShowUserDialog}>
                      <DialogTrigger asChild>
                        <Button>
                          <Plus className="h-4 w-4 mr-2" />
                          Add User
                        </Button>
                      </DialogTrigger>

                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Create New User</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <Label htmlFor="name">Name *</Label>
                              <Input
                                id="name"
                                placeholder="Full name"
                                value={userForm.name}
                                onChange={(e) => setUserForm({...userForm, name: e.target.value})}
                                required
                              />
                            </div>
                            <div>
                              <Label htmlFor="email">Email *</Label>
                              <Input
                                id="email"
                                type="email"
                                placeholder="user@example.com"
                                value={userForm.email}
                                onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                                required
                              />
                            </div>
                          </div>
                          <div>
                            <Label htmlFor="password">Password *</Label>
                            <Input
                              id="password"
                              type="password"
                              placeholder="Secure password"
                              value={userForm.password}
                              onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                              required
                            />
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <Label htmlFor="role">Role</Label>
                              <Select value={userForm.role} onValueChange={(value) => setUserForm({...userForm, role: value})}>
                                <SelectTrigger>
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="patient">Patient</SelectItem>
                                  <SelectItem value="staff">Staff</SelectItem>
                                  <SelectItem value="admin">Admin</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Switch
                                id="is_active"
                                checked={userForm.is_active}
                                onCheckedChange={(checked) => setUserForm({...userForm, is_active: checked})}
                              />
                              <Label htmlFor="is_active">Active</Label>
                            </div>
                          </div>
                          <div className="flex justify-end space-x-2">
                            <Button variant="outline" onClick={() => setShowUserDialog(false)}>
                              Cancel
                            </Button>
                            <Button onClick={handleCreateUser}>
                              <Plus className="h-4 w-4 mr-2" />
                              Create User
                            </Button>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>

                {/* Search and Filter Controls */}
                <div className={`flex gap-4 ${isMobile ? 'flex-col' : 'flex-col lg:flex-row'}`}>
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        placeholder="Search users by name or email..."
                        value={userSearchTerm}
                        onChange={(e) => setUserSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <div className={`flex gap-2 ${isMobile ? 'flex-wrap' : ''}`}>
                    <Select value={userRoleFilter} onValueChange={setUserRoleFilter}>
                      <SelectTrigger className={`${isMobile ? 'flex-1 min-w-0' : 'w-32'}`}>
                        <SelectValue placeholder="Role" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Roles</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                        <SelectItem value="staff">Staff</SelectItem>
                        <SelectItem value="patient">Patient</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={userStatusFilter} onValueChange={setUserStatusFilter}>
                      <SelectTrigger className={`${isMobile ? 'flex-1 min-w-0' : 'w-32'}`}>
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={userDepartmentFilter} onValueChange={setUserDepartmentFilter}>
                      <SelectTrigger className={`${isMobile ? 'flex-1 min-w-0' : 'w-40'}`}>
                        <SelectValue placeholder="Department" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Departments</SelectItem>
                        <SelectItem value="Emergency Medicine">Emergency Medicine</SelectItem>
                        <SelectItem value="Internal Medicine">Internal Medicine</SelectItem>
                        <SelectItem value="Administration">Administration</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Results Summary */}
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Showing {filteredUsers.length} of {users.length} users</span>
                  {(userSearchTerm || userRoleFilter !== "all" || userStatusFilter !== "all" || userDepartmentFilter !== "all") && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setUserSearchTerm("");
                        setUserRoleFilter("all");
                        setUserStatusFilter("all");
                        setUserDepartmentFilter("all");
                      }}
                    >
                      Clear Filters
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className={`${isMobile ? 'overflow-x-auto' : ''}`}>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>User</TableHead>
                        {!isMobile && <TableHead>Role</TableHead>}
                        {!isMobile && <TableHead>Status</TableHead>}
                        {!isMobile && <TableHead>Department</TableHead>}
                        {!isMobile && <TableHead>Last Login</TableHead>}
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredUsers.map((user) => (
                        <TableRow key={user.id}>
                          <TableCell>
                            <div>
                              <div className="font-medium">{user.name}</div>
                              <div className="text-sm text-gray-500">{user.email}</div>
                              {isMobile && (
                                <div className="flex items-center space-x-4 mt-2">
                                  <div className="flex items-center space-x-1">
                                    {getRoleIcon(user.role)}
                                    <span className="text-xs capitalize">{user.role}</span>
                                  </div>
                                  <Badge variant={user.is_active ? "default" : "secondary"} className="text-xs">
                                    {user.is_active ? "Active" : "Inactive"}
                                  </Badge>
                                  {user.department && (
                                    <span className="text-xs text-gray-600">{user.department}</span>
                                  )}
                                </div>
                              )}
                            </div>
                          </TableCell>
                          {!isMobile && (
                            <>
                              <TableCell>
                                <div className="flex items-center space-x-2">
                                  {getRoleIcon(user.role)}
                                  <span className="capitalize">{user.role}</span>
                                </div>
                              </TableCell>
                              <TableCell>
                                <Badge variant={user.is_active ? "default" : "secondary"}>
                                  {user.is_active ? "Active" : "Inactive"}
                                </Badge>
                              </TableCell>
                              <TableCell>{user.department || "N/A"}</TableCell>
                              <TableCell>
                                {user.last_login ? new Date(user.last_login).toLocaleDateString() : "Never"}
                              </TableCell>
                            </>
                          )}
                          <TableCell>
                            <div className={`flex space-x-2 ${isMobile ? 'justify-end' : ''}`}>
                              <Switch
                                checked={user.is_active}
                                onCheckedChange={(checked) => handleUpdateUserStatus(user.id, checked)}
                              />
                              <Select onValueChange={(value) => handleUpdateUserRole(user.id, value)}>
                                <SelectTrigger className={`${isMobile ? 'w-20' : 'w-24'}`}>
                                  <SelectValue placeholder="Role" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="patient">Patient</SelectItem>
                                  <SelectItem value="staff">Staff</SelectItem>
                                  <SelectItem value="admin">Admin</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Departments Tab */}
          <TabsContent value="departments" className="space-y-6">
            <Card>
              <CardHeader className="flex justify-between items-center">
                <CardTitle className="flex items-center space-x-2">
                  <Database className="h-5 w-5" />
                  <span>Department Management</span>
                </CardTitle>
                <Dialog open={showDepartmentDialog} onOpenChange={setShowDepartmentDialog}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Department
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Department</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="dept_name">Name *</Label>
                        <Input
                          id="dept_name"
                          placeholder="Department name"
                          value={departmentForm.name}
                          onChange={(e) => setDepartmentForm({...departmentForm, name: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="dept_description">Description</Label>
                        <Textarea
                          id="dept_description"
                          placeholder="Department description"
                          value={departmentForm.description}
                          onChange={(e) => setDepartmentForm({...departmentForm, description: e.target.value})}
                          rows={3}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="head_id">Department Head</Label>
                          <Input
                            id="head_id"
                            placeholder="Head user ID"
                            value={departmentForm.head_id}
                            onChange={(e) => setDepartmentForm({...departmentForm, head_id: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="budget">Budget Allocated</Label>
                          <Input
                            id="budget"
                            type="number"
                            placeholder="Budget amount"
                            value={departmentForm.budget_allocated}
                            onChange={(e) => setDepartmentForm({...departmentForm, budget_allocated: e.target.value})}
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="color_code">Color Code</Label>
                          <Input
                            id="color_code"
                            placeholder="#FF5733"
                            value={departmentForm.color_code}
                            onChange={(e) => setDepartmentForm({...departmentForm, color_code: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="icon_name">Icon Name</Label>
                          <Input
                            id="icon_name"
                            placeholder="stethoscope"
                            value={departmentForm.icon_name}
                            onChange={(e) => setDepartmentForm({...departmentForm, icon_name: e.target.value})}
                          />
                        </div>
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" onClick={() => setShowDepartmentDialog(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleCreateDepartment}>
                          <Plus className="h-4 w-4 mr-2" />
                          Create Department
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {departments.map((dept) => (
                    <Card key={dept.id}>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">{dept.name}</CardTitle>
                        <Badge variant={dept.is_active ? "default" : "secondary"}>
                          {dept.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <p className="text-sm text-gray-600">{dept.description || "No description"}</p>
                          <div className="flex justify-between text-sm">
                            <span>Staff:</span>
                            <span className="font-medium">{dept.staff_count}</span>
                          </div>
                          {dept.head_id && (
                            <div className="flex justify-between text-sm">
                              <span>Head ID:</span>
                              <span className="font-medium">{dept.head_id}</span>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader className="flex justify-between items-center">
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>System Settings</span>
                </CardTitle>
                <Dialog open={showSettingDialog} onOpenChange={setShowSettingDialog}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Setting
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Update System Setting</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="setting_key">Setting Key *</Label>
                        <Input
                          id="setting_key"
                          placeholder="setting_key"
                          value={settingForm.setting_key}
                          onChange={(e) => setSettingForm({...settingForm, setting_key: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="setting_value">Value</Label>
                        <Input
                          id="setting_value"
                          placeholder="Setting value"
                          value={settingForm.setting_value}
                          onChange={(e) => setSettingForm({...settingForm, setting_value: e.target.value})}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="setting_type">Type</Label>
                          <Select value={settingForm.setting_type} onValueChange={(value) => setSettingForm({...settingForm, setting_type: value})}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="string">String</SelectItem>
                              <SelectItem value="integer">Integer</SelectItem>
                              <SelectItem value="float">Float</SelectItem>
                              <SelectItem value="boolean">Boolean</SelectItem>
                              <SelectItem value="json">JSON</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="category">Category</Label>
                          <Select value={settingForm.category} onValueChange={(value) => setSettingForm({...settingForm, category: value})}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="system">System</SelectItem>
                              <SelectItem value="queue">Queue</SelectItem>
                              <SelectItem value="emergency">Emergency</SelectItem>
                              <SelectItem value="staff">Staff</SelectItem>
                              <SelectItem value="security">Security</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          placeholder="Setting description"
                          value={settingForm.description}
                          onChange={(e) => setSettingForm({...settingForm, description: e.target.value})}
                          rows={2}
                        />
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" onClick={() => setShowSettingDialog(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleUpdateSetting}>
                          <Edit className="h-4 w-4 mr-2" />
                          Update Setting
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {settings.map((setting) => (
                    <div key={setting.setting_key} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-medium">{setting.setting_key}</h3>
                          <p className="text-sm text-gray-600">{setting.description || "No description"}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{setting.category}</Badge>
                          <Badge variant="secondary">{setting.setting_type}</Badge>
                        </div>
                      </div>
                      <div className="bg-gray-50 p-2 rounded text-sm font-mono">
                        {setting.setting_value}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Audit Logs</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Resource</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {auditLogs.slice(0, 50).map((log) => (
                      <TableRow key={log.id}>
                        <TableCell>
                          {new Date(log.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>{log.user_id || "System"}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{log.action}</Badge>
                        </TableCell>
                        <TableCell>{log.resource_type}</TableCell>
                        <TableCell>
                          {log.success ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-600" />
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Activity className="h-5 w-5" />
                    <span>System Health</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Button onClick={loadDashboardStats} variant="outline" className="w-full">
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh Health Status
                    </Button>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getHealthColor(stats?.system_health || 'unknown')}`}>
                        {stats?.system_health.toUpperCase() || 'UNKNOWN'}
                      </div>
                      <div className="text-sm text-gray-600">System Status</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full justify-start">
                      <Database className="h-4 w-4 mr-2" />
                      Trigger Database Backup
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Clear System Cache
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Settings className="h-4 w-4 mr-2" />
                      Restart Services
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
