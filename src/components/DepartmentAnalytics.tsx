import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import { 
  Building2, Users, Clock, TrendingUp, AlertTriangle, 
  Activity, Stethoscope, Calendar, Zap
} from 'lucide-react';

interface DepartmentMetrics {
  department: string;
  totalPatients: number;
  avgWaitTime: number;
  avgTotalTime: number;
  occupancyRate: number;
  efficiency: number;
  bottleneckStage: string;
  providersCount: number;
  nursesCount: number;
  completionRate: number;
}

interface WorkflowStage {
  stage: string;
  avgTime: number;
  patientCount: number;
  bottleneck: boolean;
  [key: string]: any;
}

interface DepartmentAnalyticsProps {
  selectedDepartment?: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function DepartmentAnalytics({ selectedDepartment }: DepartmentAnalyticsProps) {
  const [departments, setDepartments] = useState<DepartmentMetrics[]>([]);
  const [workflowStages, setWorkflowStages] = useState<WorkflowStage[]>([]);
  const [hourlyData, setHourlyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDept, setSelectedDept] = useState(selectedDepartment || 'All');

  useEffect(() => {
    loadDepartmentData();
    loadWorkflowData();
    loadHourlyData();
  }, [selectedDept]);

  const loadDepartmentData = async () => {
    try {
      // Simulate API call - replace with actual API
      const mockData: DepartmentMetrics[] = [
        {
          department: 'Emergency',
          totalPatients: 245,
          avgWaitTime: 15.2,
          avgTotalTime: 122.2,
          occupancyRate: 0.85,
          efficiency: 0.78,
          bottleneckStage: 'Provider',
          providersCount: 8,
          nursesCount: 12,
          completionRate: 0.92
        },
        {
          department: 'Cardiology',
          totalPatients: 198,
          avgWaitTime: 28.5,
          avgTotalTime: 165.8,
          occupancyRate: 0.72,
          efficiency: 0.65,
          bottleneckStage: 'Tests',
          providersCount: 6,
          nursesCount: 8,
          completionRate: 0.88
        },
        {
          department: 'Orthopedics',
          totalPatients: 156,
          avgWaitTime: 22.1,
          avgTotalTime: 162.7,
          occupancyRate: 0.68,
          efficiency: 0.71,
          bottleneckStage: 'Registration',
          providersCount: 4,
          nursesCount: 6,
          completionRate: 0.85
        },
        {
          department: 'Neurology',
          totalPatients: 134,
          avgWaitTime: 35.8,
          avgTotalTime: 175.9,
          occupancyRate: 0.81,
          efficiency: 0.58,
          bottleneckStage: 'Provider',
          providersCount: 3,
          nursesCount: 5,
          completionRate: 0.82
        },
        {
          department: 'Pediatrics',
          totalPatients: 189,
          avgWaitTime: 18.3,
          avgTotalTime: 160.5,
          occupancyRate: 0.74,
          efficiency: 0.69,
          bottleneckStage: 'Triage',
          providersCount: 5,
          nursesCount: 7,
          completionRate: 0.90
        }
      ];

      setDepartments(mockData);
    } catch (error) {
      console.error('Error loading department data:', error);
    }
  };

  const loadWorkflowData = async () => {
    try {
      const mockStages: WorkflowStage[] = [
        { stage: 'Registration', avgTime: 6.0, patientCount: 45, bottleneck: false },
        { stage: 'Check-in', avgTime: 3.2, patientCount: 42, bottleneck: false },
        { stage: 'Triage', avgTime: 4.0, patientCount: 38, bottleneck: true },
        { stage: 'Provider', avgTime: 51.7, patientCount: 35, bottleneck: true },
        { stage: 'Tests', avgTime: 18.7, patientCount: 28, bottleneck: false },
        { stage: 'Discharge', avgTime: 8.5, patientCount: 25, bottleneck: false }
      ];

      setWorkflowStages(mockStages);
    } catch (error) {
      console.error('Error loading workflow data:', error);
    }
  };

  const loadHourlyData = async () => {
    try {
      const mockHourlyData = [
        { hour: '8:00', patients: 45, waitTime: 25, occupancy: 0.7 },
        { hour: '9:00', patients: 52, waitTime: 28, occupancy: 0.8 },
        { hour: '10:00', patients: 48, waitTime: 22, occupancy: 0.75 },
        { hour: '11:00', patients: 38, waitTime: 18, occupancy: 0.65 },
        { hour: '12:00', patients: 65, waitTime: 35, occupancy: 0.9 },
        { hour: '13:00', patients: 58, waitTime: 32, occupancy: 0.85 },
        { hour: '14:00', patients: 42, waitTime: 20, occupancy: 0.7 },
        { hour: '15:00', patients: 35, waitTime: 15, occupancy: 0.6 },
        { hour: '16:00', patients: 28, waitTime: 12, occupancy: 0.5 },
        { hour: '17:00', patients: 32, waitTime: 18, occupancy: 0.55 }
      ];

      setHourlyData(mockHourlyData);
    } catch (error) {
      console.error('Error loading hourly data:', error);
    }
  };

  const getEfficiencyColor = (efficiency: number) => {
    if (efficiency >= 0.8) return 'text-green-600';
    if (efficiency >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getEfficiencyBadge = (efficiency: number) => {
    if (efficiency >= 0.8) return <Badge className="bg-green-100 text-green-800">Excellent</Badge>;
    if (efficiency >= 0.6) return <Badge className="bg-yellow-100 text-yellow-800">Good</Badge>;
    return <Badge className="bg-red-100 text-red-800">Needs Improvement</Badge>;
  };

  const filteredDepartments = selectedDept === 'All' 
    ? departments 
    : departments.filter(dept => dept.department === selectedDept);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Department Analytics</h2>
          <p className="text-gray-600">Performance metrics and optimization insights</p>
        </div>
        <div className="flex items-center space-x-2">
          <Building2 className="h-5 w-5 text-blue-600" />
          <span className="text-sm font-medium text-gray-700">
            {filteredDepartments.length} Departments
          </span>
        </div>
      </div>

      {/* Department Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {filteredDepartments.map((dept) => (
          <Card key={dept.department} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold">{dept.department}</CardTitle>
                {getEfficiencyBadge(dept.efficiency)}
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Patients Today</span>
                <span className="font-semibold">{dept.totalPatients}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Avg Wait Time</span>
                <span className="font-semibold">{dept.avgWaitTime} min</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Occupancy</span>
                <span className="font-semibold">{(dept.occupancyRate * 100).toFixed(0)}%</span>
              </div>
              <Progress value={dept.occupancyRate * 100} className="h-2" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detailed Analytics Tabs */}
      <Tabs defaultValue="workflow" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="workflow">Workflow Analysis</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="bottlenecks">Bottlenecks</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="workflow" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Workflow Stages Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="h-5 w-5" />
                  <span>Workflow Stages</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={workflowStages}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="stage" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="avgTime" fill="#3B82F6" name="Avg Time (min)" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Stage Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>Current Stage Distribution</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    {/** Map workflowStages to ChartDataInput shape: { name, value } */}
                    {(() => {
                      const pieData = workflowStages.map((s) => ({ name: s.stage, value: s.patientCount }));
                      return (
                        <>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, value }) => `${name}: ${value}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </>
                      );
                    })()}
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Workflow Stages Table */}
          <Card>
            <CardHeader>
              <CardTitle>Workflow Stage Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Stage</th>
                      <th className="text-left py-2">Avg Time</th>
                      <th className="text-left py-2">Patients</th>
                      <th className="text-left py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workflowStages.map((stage) => (
                      <tr key={stage.stage} className="border-b">
                        <td className="py-2 font-medium">{stage.stage}</td>
                        <td className="py-2">{stage.avgTime} min</td>
                        <td className="py-2">{stage.patientCount}</td>
                        <td className="py-2">
                          {stage.bottleneck ? (
                            <Badge className="bg-red-100 text-red-800">
                              <AlertTriangle className="h-3 w-3 mr-1" />
                              Bottleneck
                            </Badge>
                          ) : (
                            <Badge className="bg-green-100 text-green-800">Normal</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Department Performance Comparison */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Department Performance</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={filteredDepartments}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="department" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="avgWaitTime" fill="#EF4444" name="Wait Time (min)" />
                    <Bar dataKey="avgTotalTime" fill="#3B82F6" name="Total Time (min)" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Efficiency Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span>Efficiency Metrics</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={filteredDepartments}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="department" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="efficiency" fill="#10B981" name="Efficiency" />
                    <Bar dataKey="completionRate" fill="#8B5CF6" name="Completion Rate" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="bottlenecks" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Bottleneck Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5" />
                  <span>Bottleneck Analysis</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {workflowStages.filter(stage => stage.bottleneck).map((stage) => (
                    <div key={stage.stage} className="p-4 border rounded-lg bg-red-50">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-red-800">{stage.stage}</h4>
                        <Badge className="bg-red-100 text-red-800">Critical</Badge>
                      </div>
                      <p className="text-sm text-red-600 mt-1">
                        Average time: {stage.avgTime} minutes
                      </p>
                      <p className="text-sm text-red-600">
                        Patients waiting: {stage.patientCount}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Resource Utilization */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Stethoscope className="h-5 w-5" />
                  <span>Resource Utilization</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredDepartments.map((dept) => (
                    <div key={dept.department} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{dept.department}</span>
                        <span className="text-sm text-gray-600">
                          {dept.providersCount} providers, {dept.nursesCount} nurses
                        </span>
                      </div>
                      <Progress value={dept.occupancyRate * 100} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="h-5 w-5" />
                <span>Hourly Trends</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="patients" 
                    stackId="1" 
                    stroke="#3B82F6" 
                    fill="#3B82F6" 
                    name="Patients"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="waitTime" 
                    stackId="2" 
                    stroke="#EF4444" 
                    fill="#EF4444" 
                    name="Wait Time (min)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
