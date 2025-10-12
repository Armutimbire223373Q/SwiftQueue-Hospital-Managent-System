import React, { useState, useEffect } from 'react';
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
  Users,
  Settings,
  Shield,
  BarChart3,
  Database,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  UserCheck,
  UserX,
  Crown,
  Key,
  Plus,
  Edit,
  Trash2,
  RefreshCw
} from "lucide-react";
import { authService } from "@/services/authService";
import { apiService } from "@/services/apiService";

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
  active_queues: number;
  total_appointments_today: number;
  completed_appointments_today: number;
  avg_wait_time: number;
  system_health: string;
}

interface UserManagement {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
  has_staff_profile: boolean;
  department: string | null;
}

interface SystemSetting {
  setting_key: string;
  setting_value: string;
  setting_type: string;
  category: string;
  description: string | null;
}

interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  resource_type: string;
  resource_id: number | null;
  timestamp: string;
  success: boolean;
  error_message: string | null;
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
      const response = await apiService.get('/api/admin/dashboard/stats');
      setStats(response.data);
    } catch (err) {
      console.error("Error loading dashboard stats:", err);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await apiService.get('/api/admin/users');
      setUsers(response.data);
    } catch (err) {
      console.error("Error loading users:", err);
    }
  };

  const loadSystemSettings = async () => {
    try {
      const response = await apiService.get('/api/admin/settings');
      setSettings(response.data);
    } catch (err) {
      console.error("Error loading system settings:", err);
    }
  };

  const loadAuditLogs = async () => {
    try {
      const response = await apiService.get('/api/admin/audit-logs');
      setAuditLogs(response.data);
    } catch (err) {
      console.error("Error loading audit logs:", err);
    }
  };

  const loadDepartments = async () => {
    try {
      const response = await apiService.get('/api/admin/departments');
      setDepartments(response.data);
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Comprehensive system management and monitoring</p>
        </div>

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Overview</span>
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>Users</span>
            </TabsTrigger>
            <TabsTrigger value="departments" className="flex items-center space-x-2">
              <Database className="h-4 w-4" />
              <span>Departments</span>
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center space-x-2">
              <Shield className="h-4 w-4" />
              <span>Security</span>
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center space-x-2">
              <Activity className="h-4 w-4" />
              <span>System</span>
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

                {/* Today's Activity */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Today's Appointments</CardTitle>
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
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Staff Overview</CardTitle>
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
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </>
            )}
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader className="flex justify-between items-center">
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>User Management</span>
                </CardTitle>
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
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Department</TableHead>
                      <TableHead>Last Login</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </TableCell>
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
                        <TableCell>
                          <div className="flex space-x-2">
                            <Switch
                              checked={user.is_active}
                              onCheckedChange={(checked) => handleUpdateUserStatus(user.id, checked)}
                              size="sm"
                            />
                            <Select onValueChange={(value) => handleUpdateUserRole(user.id, value)}>
                              <SelectTrigger className="w-24">
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
