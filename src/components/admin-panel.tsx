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
  XCircle
} from "lucide-react";

interface StaffMember {
  id: string;
  name: string;
  role: string;
  isActive: boolean;
  assignedCounter?: string;
  currentCustomer?: string;
}

interface Counter {
  id: string;
  name: string;
  serviceType: string;
  isActive: boolean;
  staffMember?: StaffMember;
  status: "available" | "busy" | "offline";
}

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState("overview");
  
  const [staff, setStaff] = useState<StaffMember[]>([
    { id: "1", name: "Alice Johnson", role: "Senior Teller", isActive: true, assignedCounter: "Counter 1", currentCustomer: "John Doe" },
    { id: "2", name: "Bob Smith", role: "Loan Officer", isActive: true, assignedCounter: "Counter 2" },
    { id: "3", name: "Carol Davis", role: "Customer Service", isActive: false },
    { id: "4", name: "David Wilson", role: "Teller", isActive: true, assignedCounter: "Counter 4" }
  ]);

  const [counters, setCounters] = useState<Counter[]>([
    { id: "counter1", name: "Counter 1", serviceType: "General Banking", isActive: true, status: "busy" },
    { id: "counter2", name: "Counter 2", serviceType: "Loans", isActive: true, status: "available" },
    { id: "counter3", name: "Counter 3", serviceType: "Customer Service", isActive: false, status: "offline" },
    { id: "counter4", name: "Counter 4", serviceType: "General Banking", isActive: true, status: "available" }
  ]);

  const toggleCounterStatus = (counterId: string) => {
    setCounters(counters.map(counter => 
      counter.id === counterId 
        ? { ...counter, isActive: !counter.isActive, status: counter.isActive ? "offline" : "available" }
        : counter
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

  return (
    <div className="bg-white min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Control Panel</h1>
          <p className="text-gray-600">Manage queues, staff, and system settings</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <Monitor className="h-4 w-4" />
              <span>Overview</span>
            </TabsTrigger>
            <TabsTrigger value="staff" className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>Staff</span>
            </TabsTrigger>
            <TabsTrigger value="counters" className="flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              <span>Counters</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Analytics</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Staff</CardTitle>
                  <UserCheck className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{staff.filter(s => s.isActive).length}</div>
                  <p className="text-xs text-muted-foreground">out of {staff.length} total</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Open Counters</CardTitle>
                  <Monitor className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{counters.filter(c => c.isActive).length}</div>
                  <p className="text-xs text-muted-foreground">out of {counters.length} total</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Queue Length</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">7</div>
                  <p className="text-xs text-muted-foreground">customers waiting</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Wait Time</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">12m</div>
                  <p className="text-xs text-muted-foreground">current average</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button className="w-full justify-start">
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Emergency Queue Clear
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Users className="h-4 w-4 mr-2" />
                    Call Next Customer
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Settings className="h-4 w-4 mr-2" />
                    System Maintenance Mode
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>AI Recommendations</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-yellow-50 p-3 rounded-lg">
                    <p className="text-sm font-medium text-yellow-900">Staff Optimization</p>
                    <p className="text-xs text-yellow-700">Consider opening Counter 3 - expected rush in 20 minutes</p>
                    <Button size="sm" className="mt-2">Apply</Button>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-sm font-medium text-blue-900">Queue Management</p>
                    <p className="text-xs text-blue-700">Redistribute customers from Banking to Business counter</p>
                    <Button size="sm" variant="outline" className="mt-2">Review</Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="staff" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Staff Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {staff.map((member) => (
                    <div key={member.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full ${member.isActive ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <div>
                          <p className="font-medium">{member.name}</p>
                          <p className="text-sm text-gray-500">{member.role}</p>
                          {member.assignedCounter && (
                            <p className="text-xs text-blue-600">Assigned to {member.assignedCounter}</p>
                          )}
                          {member.currentCustomer && (
                            <p className="text-xs text-green-600">Serving: {member.currentCustomer}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge variant={member.isActive ? "default" : "secondary"}>
                          {member.isActive ? "Active" : "Inactive"}
                        </Badge>
                        <Switch
                          checked={member.isActive}
                          onCheckedChange={() => toggleStaffStatus(member.id)}
                        />
                        <Select defaultValue={member.assignedCounter || ""}>
                          <SelectTrigger className="w-32">
                            <SelectValue placeholder="Assign" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">Unassigned</SelectItem>
                            <SelectItem value="Counter 1">Counter 1</SelectItem>
                            <SelectItem value="Counter 2">Counter 2</SelectItem>
                            <SelectItem value="Counter 3">Counter 3</SelectItem>
                            <SelectItem value="Counter 4">Counter 4</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="counters" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Service Counter Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {counters.map((counter) => (
                    <div key={counter.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className={`w-4 h-4 rounded-full ${getStatusColor(counter.status)}`}></div>
                          <h3 className="font-medium">{counter.name}</h3>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="flex items-center space-x-1">
                            {getStatusIcon(counter.status)}
                            <span className="capitalize">{counter.status}</span>
                          </Badge>
                          <Switch
                            checked={counter.isActive}
                            onCheckedChange={() => toggleCounterStatus(counter.id)}
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-gray-600">Service: {counter.serviceType}</p>
                        <Select defaultValue={counter.serviceType}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="General Banking">General Banking</SelectItem>
                            <SelectItem value="Loans">Loans</SelectItem>
                            <SelectItem value="Customer Service">Customer Service</SelectItem>
                            <SelectItem value="Business Banking">Business Banking</SelectItem>
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
                  <CardTitle className="text-lg">Today's Performance</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Customers Served</span>
                    <span className="font-medium">47</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Avg Service Time</span>
                    <span className="font-medium">8.5m</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Peak Hour</span>
                    <span className="font-medium">2:00 PM</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Efficiency Score</span>
                    <span className="font-medium text-green-600">87%</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Queue Insights</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Longest Wait</span>
                    <span className="font-medium">25m</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Shortest Wait</span>
                    <span className="font-medium">3m</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">No-shows</span>
                    <span className="font-medium">2</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Customer Satisfaction</span>
                    <span className="font-medium text-green-600">4.2/5</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Predictions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-blue-50 p-3 rounded">
                    <p className="text-sm font-medium text-blue-900">Next Rush Hour</p>
                    <p className="text-xs text-blue-700">Expected at 4:30 PM</p>
                  </div>
                  <div className="bg-yellow-50 p-3 rounded">
                    <p className="text-sm font-medium text-yellow-900">Staff Needed</p>
                    <p className="text-xs text-yellow-700">+1 teller in 30 minutes</p>
                  </div>
                  <div className="bg-green-50 p-3 rounded">
                    <p className="text-sm font-medium text-green-900">Optimal Closing</p>
                    <p className="text-xs text-green-700">Counter 3 at 4:00 PM</p>
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