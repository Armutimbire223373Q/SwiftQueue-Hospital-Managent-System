import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Settings, 
  Users, 
  Monitor, 
  BarChart3, 
  UserCheck, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Brain,
  Heart,
  Stethoscope,
  Activity,
  Shield,
  Plus,
  Edit,
  Trash2,
  Save,
  RefreshCw,
  Eye,
  UserPlus,
  UserMinus,
  Zap,
  TrendingUp,
  TrendingDown,
  Star,
  Bell,
  Lock,
  Unlock,
  Play,
  Pause,
  Square,
  ArrowUp,
  ArrowDown,
  Minus,
  Target,
  Calendar,
  FileText,
  Database,
  Server,
  Wifi,
  WifiOff
} from 'lucide-react';
import { demoService } from '@/services/demoService';

interface StaffMember {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  isActive: boolean;
  assignedRoom?: string;
  currentPatient?: string;
  specialization?: string;
  shift: 'morning' | 'afternoon' | 'night';
  experience: number;
  rating: number;
  lastActive: Date;
}

interface ServiceArea {
  id: string;
  name: string;
  serviceType: string;
  department: string;
  isActive: boolean;
  staffMember?: StaffMember;
  status: 'available' | 'busy' | 'offline' | 'maintenance';
  capacity: number;
  currentLoad: number;
  waitTime: number;
  efficiency: number;
}

interface SystemSettings {
  autoAssign: boolean;
  notifications: boolean;
  aiOptimization: boolean;
  emergencyPriority: boolean;
  maintenanceMode: boolean;
  dataRetention: number;
  maxWaitTime: number;
  peakHourThreshold: number;
}

const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [services, setServices] = useState<ServiceArea[]>([]);
  const [settings, setSettings] = useState<SystemSettings>({
    autoAssign: true,
    notifications: true,
    aiOptimization: true,
    emergencyPriority: true,
    maintenanceMode: false,
    dataRetention: 30,
    maxWaitTime: 60,
    peakHourThreshold: 20
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingStaff, setEditingStaff] = useState<StaffMember | null>(null);
  const [editingService, setEditingService] = useState<ServiceArea | null>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      // Load demo data
      loadDemoData();
    } catch (err) {
      setError('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const loadDemoData = () => {
    setStaff([
      {
        id: '1',
        name: 'Dr. Sarah Johnson',
        email: 'sarah.johnson@hospital.com',
        role: 'Chief Medical Officer',
        department: 'Emergency',
        isActive: true,
        assignedRoom: 'ER-1',
        currentPatient: 'Patient #15',
        specialization: 'Emergency Medicine',
        shift: 'morning',
        experience: 8,
        rating: 4.9,
        lastActive: new Date()
      },
      {
        id: '2',
        name: 'Dr. Michael Chen',
        email: 'michael.chen@hospital.com',
        role: 'Cardiologist',
        department: 'Cardiology',
        isActive: true,
        assignedRoom: 'CARD-2',
        currentPatient: 'Patient #12',
        specialization: 'Cardiovascular Surgery',
        shift: 'afternoon',
        experience: 12,
        rating: 4.8,
        lastActive: new Date()
      },
      {
        id: '3',
        name: 'Nurse Lisa Rodriguez',
        email: 'lisa.rodriguez@hospital.com',
        role: 'Senior Nurse',
        department: 'General Medicine',
        isActive: true,
        assignedRoom: 'GM-3',
        currentPatient: 'Patient #8',
        specialization: 'Patient Care',
        shift: 'night',
        experience: 6,
        rating: 4.7,
        lastActive: new Date()
      }
    ]);

    setServices([
      {
        id: '1',
        name: 'Emergency Room 1',
        serviceType: 'Emergency Care',
        department: 'Emergency',
        isActive: true,
        status: 'busy',
        capacity: 4,
        currentLoad: 3,
        waitTime: 5,
        efficiency: 92
      },
      {
        id: '2',
        name: 'Cardiology Unit',
        serviceType: 'Cardiology',
        department: 'Cardiology',
        isActive: true,
        status: 'available',
        capacity: 6,
        currentLoad: 2,
        waitTime: 15,
        efficiency: 88
      },
      {
        id: '3',
        name: 'General Medicine Ward',
        serviceType: 'General Medicine',
        department: 'General',
        isActive: true,
        status: 'busy',
        capacity: 8,
        currentLoad: 6,
        waitTime: 12,
        efficiency: 85
      }
    ]);
  };

  const handleStaffToggle = (staffId: string) => {
    setStaff(prev => prev.map(s => 
      s.id === staffId ? { ...s, isActive: !s.isActive } : s
    ));
  };

  const handleServiceToggle = (serviceId: string) => {
    setServices(prev => prev.map(s => 
      s.id === serviceId ? { ...s, isActive: !s.isActive } : s
    ));
  };

  const handleSettingsChange = (key: keyof SystemSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'text-green-600 bg-green-100';
      case 'busy': return 'text-orange-600 bg-orange-100';
      case 'offline': return 'text-red-600 bg-red-100';
      case 'maintenance': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getDepartmentIcon = (department: string) => {
    switch (department.toLowerCase()) {
      case 'emergency': return AlertTriangle;
      case 'cardiology': return Heart;
      case 'general': return Stethoscope;
      case 'laboratory': return Activity;
      case 'radiology': return Brain;
      case 'pediatrics': return Users;
      default: return Stethoscope;
    }
  };

  const getShiftColor = (shift: string) => {
    switch (shift) {
      case 'morning': return 'bg-yellow-100 text-yellow-800';
      case 'afternoon': return 'bg-blue-100 text-blue-800';
      case 'night': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-lg text-gray-600">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Admin Panel
              </h1>
              <p className="text-lg text-gray-600 mt-2">Hospital management and system control</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                onClick={loadData}
                variant="outline"
                className="flex items-center"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </Button>
            </div>
          </div>
        </motion.div>

        {/* System Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          {[
            {
              title: 'Active Staff',
              value: staff.filter(s => s.isActive).length,
              total: staff.length,
              icon: UserCheck,
              color: 'text-green-600',
              bgColor: 'bg-green-50'
            },
            {
              title: 'Active Services',
              value: services.filter(s => s.isActive).length,
              total: services.length,
              icon: Monitor,
              color: 'text-blue-600',
              bgColor: 'bg-blue-50'
            },
            {
              title: 'System Uptime',
              value: '99.9%',
              icon: Server,
              color: 'text-purple-600',
              bgColor: 'bg-purple-50'
            },
            {
              title: 'AI Optimization',
              value: settings.aiOptimization ? 'ON' : 'OFF',
              icon: Brain,
              color: settings.aiOptimization ? 'text-green-600' : 'text-red-600',
              bgColor: settings.aiOptimization ? 'bg-green-50' : 'bg-red-50'
            }
          ].map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-white/80 backdrop-blur-sm">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 rounded-xl ${stat.bgColor} flex items-center justify-center`}>
                        <Icon className={`h-6 w-6 ${stat.color}`} />
                      </div>
                      {stat.total && (
                        <div className="text-sm text-gray-600">
                          {stat.value}/{stat.total}
                        </div>
                      )}
                    </div>
                    <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                    <div className="text-sm text-gray-600">{stat.title}</div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-white/80 backdrop-blur-sm">
            <TabsTrigger value="overview" className="flex items-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="staff" className="flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Staff
            </TabsTrigger>
            <TabsTrigger value="services" className="flex items-center">
              <Monitor className="h-4 w-4 mr-2" />
              Services
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center">
              <Shield className="h-4 w-4 mr-2" />
              System
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Staff Overview */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Users className="h-6 w-6 mr-2 text-blue-600" />
                      Staff Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {staff.slice(0, 5).map((member, index) => {
                        const Icon = getDepartmentIcon(member.department);
                        return (
                          <div key={member.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                            <div className="flex items-center">
                              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-3">
                                <Icon className="h-5 w-5 text-white" />
                              </div>
                              <div>
                                <div className="font-semibold">{member.name}</div>
                                <div className="text-sm text-gray-600">{member.role} • {member.department}</div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge className={getShiftColor(member.shift)}>
                                {member.shift}
                              </Badge>
                              <Switch
                                checked={member.isActive}
                                onCheckedChange={() => handleStaffToggle(member.id)}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Service Status */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Monitor className="h-6 w-6 mr-2 text-green-600" />
                      Service Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {services.map((service, index) => {
                        const Icon = getDepartmentIcon(service.department);
                        return (
                          <div key={service.id} className="p-3 rounded-lg border border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center">
                                <Icon className="h-5 w-5 text-gray-600 mr-2" />
                                <span className="font-medium">{service.name}</span>
                              </div>
                              <Badge className={getStatusColor(service.status)}>
                                {service.status}
                              </Badge>
                            </div>
                            <div className="grid grid-cols-3 gap-4 text-sm">
                              <div>
                                <div className="text-gray-500">Load</div>
                                <div className="font-semibold">{service.currentLoad}/{service.capacity}</div>
                              </div>
                              <div>
                                <div className="text-gray-500">Wait Time</div>
                                <div className="font-semibold">{service.waitTime}m</div>
                              </div>
                              <div>
                                <div className="text-gray-500">Efficiency</div>
                                <div className="font-semibold">{service.efficiency}%</div>
                              </div>
                            </div>
                            <div className="mt-2">
                              <Progress value={(service.currentLoad / service.capacity) * 100} className="h-2" />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </TabsContent>

          {/* Staff Management Tab */}
          <TabsContent value="staff" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center">
                      <Users className="h-6 w-6 mr-2 text-blue-600" />
                      Staff Management
                    </CardTitle>
                    <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                      <UserPlus className="h-4 w-4 mr-2" />
                      Add Staff
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {staff.map((member, index) => {
                      const Icon = getDepartmentIcon(member.department);
                      return (
                        <motion.div
                          key={member.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                          className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-300"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-4">
                                <Icon className="h-6 w-6 text-white" />
                              </div>
                              <div>
                                <h3 className="font-semibold text-gray-900">{member.name}</h3>
                                <p className="text-sm text-gray-600">{member.email}</p>
                                <div className="flex items-center space-x-4 mt-1">
                                  <Badge variant="outline">{member.role}</Badge>
                                  <Badge className={getShiftColor(member.shift)}>
                                    {member.shift}
                                  </Badge>
                                  <div className="flex items-center text-sm text-gray-500">
                                    <Star className="h-4 w-4 mr-1" />
                                    {member.rating}
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Button size="sm" variant="outline">
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Switch
                                checked={member.isActive}
                                onCheckedChange={() => handleStaffToggle(member.id)}
                              />
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          {/* Services Management Tab */}
          <TabsContent value="services" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center">
                      <Monitor className="h-6 w-6 mr-2 text-green-600" />
                      Service Management
                    </CardTitle>
                    <Button className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Service
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {services.map((service, index) => {
                      const Icon = getDepartmentIcon(service.department);
                      return (
                        <motion.div
                          key={service.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                          className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-300"
                        >
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center">
                              <Icon className="h-6 w-6 text-gray-600 mr-2" />
                              <span className="font-semibold">{service.name}</span>
                            </div>
                            <Badge className={getStatusColor(service.status)}>
                              {service.status}
                            </Badge>
                          </div>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-500">Department:</span>
                              <span>{service.department}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">Capacity:</span>
                              <span>{service.currentLoad}/{service.capacity}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">Wait Time:</span>
                              <span>{service.waitTime}m</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">Efficiency:</span>
                              <span>{service.efficiency}%</span>
                            </div>
                          </div>
                          <div className="mt-3 flex items-center justify-between">
                            <Switch
                              checked={service.isActive}
                              onCheckedChange={() => handleServiceToggle(service.id)}
                            />
                            <Button size="sm" variant="outline">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Settings className="h-6 w-6 mr-2 text-purple-600" />
                    System Settings
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold">Queue Management</h3>
                        <div className="space-y-4">
                          <div className="flex items-center justify-between">
                            <Label htmlFor="autoAssign">Auto-assign patients</Label>
                            <Switch
                              id="autoAssign"
                              checked={settings.autoAssign}
                              onCheckedChange={(checked) => handleSettingsChange('autoAssign', checked)}
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <Label htmlFor="emergencyPriority">Emergency priority</Label>
                            <Switch
                              id="emergencyPriority"
                              checked={settings.emergencyPriority}
                              onCheckedChange={(checked) => handleSettingsChange('emergencyPriority', checked)}
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <Label htmlFor="aiOptimization">AI optimization</Label>
                            <Switch
                              id="aiOptimization"
                              checked={settings.aiOptimization}
                              onCheckedChange={(checked) => handleSettingsChange('aiOptimization', checked)}
                            />
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold">System Configuration</h3>
                        <div className="space-y-4">
                          <div>
                            <Label htmlFor="maxWaitTime">Max wait time (minutes)</Label>
                            <Input
                              id="maxWaitTime"
                              type="number"
                              value={settings.maxWaitTime}
                              onChange={(e) => handleSettingsChange('maxWaitTime', parseInt(e.target.value))}
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="peakHourThreshold">Peak hour threshold</Label>
                            <Input
                              id="peakHourThreshold"
                              type="number"
                              value={settings.peakHourThreshold}
                              onChange={(e) => handleSettingsChange('peakHourThreshold', parseInt(e.target.value))}
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="dataRetention">Data retention (days)</Label>
                            <Input
                              id="dataRetention"
                              type="number"
                              value={settings.dataRetention}
                              onChange={(e) => handleSettingsChange('dataRetention', parseInt(e.target.value))}
                              className="mt-1"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="h-6 w-6 mr-2 text-red-600" />
                    System Control
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold">System Status</h3>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between p-3 rounded-lg bg-green-50">
                            <div className="flex items-center">
                              <Wifi className="h-5 w-5 text-green-600 mr-2" />
                              <span>Database Connection</span>
                            </div>
                            <Badge className="bg-green-100 text-green-800">Connected</Badge>
                          </div>
                          <div className="flex items-center justify-between p-3 rounded-lg bg-green-50">
                            <div className="flex items-center">
                              <Server className="h-5 w-5 text-green-600 mr-2" />
                              <span>API Server</span>
                            </div>
                            <Badge className="bg-green-100 text-green-800">Running</Badge>
                          </div>
                          <div className="flex items-center justify-between p-3 rounded-lg bg-green-50">
                            <div className="flex items-center">
                              <Brain className="h-5 w-5 text-green-600 mr-2" />
                              <span>AI Services</span>
                            </div>
                            <Badge className="bg-green-100 text-green-800">Active</Badge>
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold">System Actions</h3>
                        <div className="space-y-3">
                          <Button className="w-full justify-start" variant="outline">
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Restart Services
                          </Button>
                          <Button className="w-full justify-start" variant="outline">
                            <Database className="h-4 w-4 mr-2" />
                            Backup Database
                          </Button>
                          <Button className="w-full justify-start" variant="outline">
                            <FileText className="h-4 w-4 mr-2" />
                            View Logs
                          </Button>
                          <Button className="w-full justify-start" variant="outline">
                            <Shield className="h-4 w-4 mr-2" />
                            Security Scan
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>

        {/* Success/Error Messages */}
        <AnimatePresence>
          {success && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="fixed bottom-4 right-4 z-50"
            >
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">{success}</AlertDescription>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AdminPanel;
