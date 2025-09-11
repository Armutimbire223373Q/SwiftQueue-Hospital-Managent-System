import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  Shield
} from "lucide-react";

interface StaffMember {
  id: string;
  name: string;
  role: string;
  department: string;
  isActive: boolean;
  assignedRoom?: string;
  currentPatient?: string;
  specialization?: string;
}

interface ServiceArea {
  id: string;
  name: string;
  serviceType: string;
  department: string;
  isActive: boolean;
  staffMember?: StaffMember;
  status: "available" | "busy" | "offline";
  capacity: number;
  currentLoad: number;
}

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState("overview");
  
  const [staff, setStaff] = useState<StaffMember[]>([
    { 
      id: "1", 
      name: "Dr. Alice Johnson", 
      role: "Senior Physician", 
      department: "Internal Medicine",
      specialization: "General Practice",
      isActive: true, 
      assignedRoom: "Room 101", 
      currentPatient: "John Smith" 
    },
    { 
      id: "2", 
      name: "Dr. Bob Smith", 
      role: "Cardiologist", 
      department: "Cardiology",
      specialization: "Interventional Cardiology",
      isActive: true, 
      assignedRoom: "Room 205" 
    },
    { 
      id: "3", 
      name: "Nurse Carol Davis", 
      role: "Registered Nurse", 
      department: "Emergency",
      specialization: "Emergency Care",
      isActive: false 
    },
    { 
      id: "4", 
      name: "Dr. David Wilson", 
      role: "Radiologist", 
      department: "Radiology",
      specialization: "Diagnostic Imaging",
      isActive: true, 
      assignedRoom: "Radiology Suite 1" 
    }
  ]);

  const [serviceAreas, setServiceAreas] = useState<ServiceArea[]>([
    { 
      id: "area1", 
      name: "Room 101", 
      serviceType: "General Consultation", 
      department: "Internal Medicine",
      isActive: true, 
      status: "busy",
      capacity: 1,
      currentLoad: 1
    },
    { 
      id: "area2", 
      name: "Room 205", 
      serviceType: "Cardiology", 
      department: "Cardiology",
      isActive: true, 
      status: "available",
      capacity: 1,
      currentLoad: 0
    },
    { 
      id: "area3", 
      name: "Emergency Bay 1", 
      serviceType: "Emergency Care", 
      department: "Emergency",
      isActive: false, 
      status: "offline",
      capacity: 2,
      currentLoad: 0
    },
    { 
      id: "area4", 
      name: "Lab Station 1", 
      serviceType: "Laboratory", 
      department: "Laboratory",
      isActive: true, 
      status: "available",
      capacity: 3,
      currentLoad: 1
    }
  ]);

  const toggleAreaStatus = (areaId: string) => {
    setServiceAreas(serviceAreas.map(area => 
      area.id === areaId 
        ? { ...area, isActive: !area.isActive, status: area.isActive ? "offline" : "available" }
        : area
    ));
  };

  const toggleStaffStatus = (staffId: string) => {
    setStaff(staff.map(member => 
      member.id === staffId 
        ? { ...member, isActive: !member.isActive }
        : member
    ));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "available": return "bg-green-500";
      case "busy": return "bg-yellow-500";
      case "offline": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "available": return <CheckCircle className="h-4 w-4" />;
      case "busy": return <Clock className="h-4 w-4" />;
      case "offline": return <XCircle className="h-4 w-4" />;
      default: return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getDepartmentIcon = (department: string) => {
    switch (department) {
      case "Cardiology": return <Heart className="h-4 w-4" />;
      case "Emergency": return <AlertTriangle className="h-4 w-4" />;
      case "Laboratory": return <Activity className="h-4 w-4" />;
      case "Radiology": return <Monitor className="h-4 w-4" />;
      default: return <Stethoscope className="h-4 w-4" />;
    }
  };

  return (
    <div className="bg-white min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Hospital Admin Control Panel</h1>
          <p className="text-gray-600">AI-powered hospital management and resource optimization</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <Monitor className="h-4 w-4" />
              <span>Overview</span>
            </TabsTrigger>
            <TabsTrigger value="staff" className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>Medical Staff</span>
            </TabsTrigger>
            <TabsTrigger value="areas" className="flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              <span>Service Areas</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>AI Analytics</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Medical Staff</CardTitle>
                  <UserCheck className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{staff.filter(s => s.isActive).length}</div>
                  <p className="text-xs text-muted-foreground">out of {staff.length} total</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Service Areas</CardTitle>
                  <Monitor className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{serviceAreas.filter(c => c.isActive).length}</div>
                  <p className="text-xs text-muted-foreground">out of {serviceAreas.length} total</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Patients in Queue</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">12</div>
                  <p className="text-xs text-muted-foreground">across all departments</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">AI Efficiency Score</CardTitle>
                  <Brain className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-600">92%</div>
                  <p className="text-xs text-muted-foreground">AI-optimized operations</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Emergency Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button className="w-full justify-start" variant="destructive">
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Emergency Protocol Activation
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Users className="h-4 w-4 mr-2" />
                    Call Next Patient
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Shield className="h-4 w-4 mr-2" />
                    System Maintenance Mode
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Brain className="h-4 w-4 mr-2" />
                    AI Optimization Override
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-blue-600" />
                    <span>AI Recommendations</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-red-50 p-3 rounded-lg">
                    <p className="text-sm font-medium text-red-900">Critical Alert</p>
                    <p className="text-xs text-red-700">Emergency Bay 1 should be activated - 2 urgent cases incoming</p>
                    <Button size="sm" className="mt-2" variant="destructive">Apply Immediately</Button>
                  </div>
                  <div className="bg-yellow-50 p-3 rounded-lg">
                    <p className="text-sm font-medium text-yellow-900">Resource Optimization</p>
                    <p className="text-xs text-yellow-700">Redistribute cardiology patients - Dr. Smith available in 15 min</p>
                    <Button size="sm" variant="outline" className="mt-2">Review Suggestion</Button>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-sm font-medium text-blue-900">Predictive Insight</p>
                    <p className="text-xs text-blue-700">Expected patient surge at 3:00 PM - prepare additional staff</p>
                    <Button size="sm" variant="outline" className="mt-2">Schedule Staff</Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="staff" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Medical Staff Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {staff.map((member) => (
                    <div key={member.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full ${member.isActive ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <div className="flex items-center space-x-2">
                          {getDepartmentIcon(member.department)}
                          <div>
                            <p className="font-medium">{member.name}</p>
                            <p className="text-sm text-gray-500">{member.role} - {member.department}</p>
                            {member.specialization && (
                              <p className="text-xs text-blue-600">{member.specialization}</p>
                            )}
                            {member.assignedRoom && (
                              <p className="text-xs text-purple-600">Assigned to {member.assignedRoom}</p>
                            )}
                            {member.currentPatient && (
                              <p className="text-xs text-green-600">Currently treating: {member.currentPatient}</p>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge variant={member.isActive ? "default" : "secondary"}>
                          {member.isActive ? "On Duty" : "Off Duty"}
                        </Badge>
                        <Switch
                          checked={member.isActive}
                          onCheckedChange={() => toggleStaffStatus(member.id)}
                        />
                        <Select defaultValue={member.assignedRoom || ""}>
                          <SelectTrigger className="w-40">
                            <SelectValue placeholder="Assign Room" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">Unassigned</SelectItem>
                            <SelectItem value="Room 101">Room 101</SelectItem>
                            <SelectItem value="Room 205">Room 205</SelectItem>
                            <SelectItem value="Emergency Bay 1">Emergency Bay 1</SelectItem>
                            <SelectItem value="Lab Station 1">Lab Station 1</SelectItem>
                            <SelectItem value="Radiology Suite 1">Radiology Suite 1</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="areas" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Service Area Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {serviceAreas.map((area) => (
                    <div key={area.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className={`w-4 h-4 rounded-full ${getStatusColor(area.status)}`}></div>
                          <div className="flex items-center space-x-2">
                            {getDepartmentIcon(area.department)}
                            <h3 className="font-medium">{area.name}</h3>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="flex items-center space-x-1">
                            {getStatusIcon(area.status)}
                            <span className="capitalize">{area.status}</span>
                          </Badge>
                          <Switch
                            checked={area.isActive}
                            onCheckedChange={() => toggleAreaStatus(area.id)}
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-gray-600">Department: {area.department}</p>
                        <p className="text-sm text-gray-600">Service: {area.serviceType}</p>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Capacity:</span>
                          <span className="font-medium">{area.currentLoad}/{area.capacity}</span>
                        </div>
                        <Select defaultValue={area.serviceType}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="General Consultation">General Consultation</SelectItem>
                            <SelectItem value="Cardiology">Cardiology</SelectItem>
                            <SelectItem value="Emergency Care">Emergency Care</SelectItem>
                            <SelectItem value="Laboratory">Laboratory</SelectItem>
                            <SelectItem value="Radiology">Radiology</SelectItem>
                            <SelectItem value="Pediatrics">Pediatrics</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Today's Performance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Patients Treated</span>
                    <span className="font-medium">73</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Avg Treatment Time</span>
                    <span className="font-medium">18.5m</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Peak Department</span>
                    <span className="font-medium">Emergency</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">AI Efficiency Score</span>
                    <span className="font-medium text-green-600">92%</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <Brain className="h-4 w-4 mr-2 text-blue-500" />
                    AI Patient Insights
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Longest Wait</span>
                    <span className="font-medium">32m</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Shortest Wait</span>
                    <span className="font-medium">4m</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">No-shows</span>
                    <span className="font-medium">3</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Patient Satisfaction</span>
                    <span className="font-medium text-green-600">4.6/5</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <Brain className="h-4 w-4 mr-2 text-purple-500" />
                    AI Predictions
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-blue-50 p-3 rounded">
                    <p className="text-sm font-medium text-blue-900">Next Rush Period</p>
                    <p className="text-xs text-blue-700">Expected at 3:00 PM - Emergency Dept</p>
                  </div>
                  <div className="bg-yellow-50 p-3 rounded">
                    <p className="text-sm font-medium text-yellow-900">Staff Optimization</p>
                    <p className="text-xs text-yellow-700">+2 nurses needed in 45 minutes</p>
                  </div>
                  <div className="bg-green-50 p-3 rounded">
                    <p className="text-sm font-medium text-green-900">Resource Allocation</p>
                    <p className="text-xs text-green-700">Lab capacity optimal until 5:00 PM</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <span>Advanced AI Analytics Dashboard</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">Real-time AI Monitoring</h4>
                    <div className="space-y-2 text-sm">
                      <p className="text-blue-700">• Patient flow pattern analysis</p>
                      <p className="text-blue-700">• Treatment duration predictions</p>
                      <p className="text-blue-700">• Resource utilization optimization</p>
                      <p className="text-blue-700">• Emergency case prioritization</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">Predictive Insights</h4>
                    <div className="space-y-2 text-sm">
                      <p className="text-purple-700">• Staff workload balancing</p>
                      <p className="text-purple-700">• Equipment maintenance scheduling</p>
                      <p className="text-purple-700">• Patient satisfaction forecasting</p>
                      <p className="text-purple-700">• Capacity planning recommendations</p>
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
}