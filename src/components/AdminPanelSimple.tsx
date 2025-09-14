import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Settings, 
  Users, 
  Monitor, 
  BarChart3, 
  UserCheck, 
  Shield,
  RefreshCw,
  Save
} from 'lucide-react';

interface StaffMember {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  isActive: boolean;
  shift: 'morning' | 'afternoon' | 'night';
  rating: number;
}

interface ServiceArea {
  id: string;
  name: string;
  serviceType: string;
  department: string;
  isActive: boolean;
  status: 'available' | 'busy' | 'offline' | 'maintenance';
  capacity: number;
  currentLoad: number;
  waitTime: number;
  efficiency: number;
}

const AdminPanelSimple: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [services, setServices] = useState<ServiceArea[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setStaff([
      {
        id: '1',
        name: 'Dr. Sarah Johnson',
        email: 'sarah.johnson@hospital.com',
        role: 'Chief Medical Officer',
        department: 'Emergency',
        isActive: true,
        shift: 'morning',
        rating: 4.9
      },
      {
        id: '2',
        name: 'Dr. Michael Chen',
        email: 'michael.chen@hospital.com',
        role: 'Cardiologist',
        department: 'Cardiology',
        isActive: true,
        shift: 'afternoon',
        rating: 4.8
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
      }
    ]);

    setLoading(false);
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'text-green-600 bg-green-100';
      case 'busy': return 'text-orange-600 bg-orange-100';
      case 'offline': return 'text-red-600 bg-red-100';
      case 'maintenance': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
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
        <div className="mb-8">
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
        </div>

        {/* System Status */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
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
              icon: Shield,
              color: 'text-purple-600',
              bgColor: 'bg-purple-50'
            },
            {
              title: 'AI Optimization',
              value: 'ON',
              icon: Settings,
              color: 'text-green-600',
              bgColor: 'bg-green-50'
            }
          ].map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.title} className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-white/80 backdrop-blur-sm">
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
            );
          })}
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white/80 backdrop-blur-sm">
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
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Staff Overview */}
              <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="h-6 w-6 mr-2 text-blue-600" />
                    Staff Overview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {staff.map((member) => (
                      <div key={member.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-3">
                            <Users className="h-5 w-5 text-white" />
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
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Service Status */}
              <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Monitor className="h-6 w-6 mr-2 text-green-600" />
                    Service Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {services.map((service) => (
                      <div key={service.id} className="p-3 rounded-lg border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            <Monitor className="h-5 w-5 text-gray-600 mr-2" />
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
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Staff Management Tab */}
          <TabsContent value="staff" className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="h-6 w-6 mr-2 text-blue-600" />
                  Staff Management
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {staff.map((member) => (
                    <div key={member.id} className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-300">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-4">
                            <Users className="h-6 w-6 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">{member.name}</h3>
                            <p className="text-sm text-gray-600">{member.email}</p>
                            <div className="flex items-center space-x-4 mt-1">
                              <Badge variant="outline">{member.role}</Badge>
                              <Badge className={getShiftColor(member.shift)}>
                                {member.shift}
                              </Badge>
                              <div className="text-sm text-gray-500">
                                Rating: {member.rating}
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Switch
                            checked={member.isActive}
                            onCheckedChange={() => handleStaffToggle(member.id)}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Services Management Tab */}
          <TabsContent value="services" className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Monitor className="h-6 w-6 mr-2 text-green-600" />
                  Service Management
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {services.map((service) => (
                    <div key={service.id} className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-300">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center">
                          <Monitor className="h-6 w-6 text-gray-600 mr-2" />
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
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
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
                          <span>Auto-assign patients</span>
                          <Switch defaultChecked />
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Emergency priority</span>
                          <Switch defaultChecked />
                        </div>
                        <div className="flex items-center justify-between">
                          <span>AI optimization</span>
                          <Switch defaultChecked />
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">System Configuration</h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Max wait time (minutes)
                          </label>
                          <input
                            type="number"
                            defaultValue={60}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Peak hour threshold
                          </label>
                          <input
                            type="number"
                            defaultValue={20}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminPanelSimple;
