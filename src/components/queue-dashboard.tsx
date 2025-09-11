import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Clock, Users, AlertCircle, CheckCircle, Heart, Brain, Activity, Stethoscope } from "lucide-react";

interface QueueItem {
  id: string;
  patientName: string;
  serviceType: string;
  queueNumber: number;
  estimatedWaitTime: number;
  status: "waiting" | "called" | "serving" | "completed";
  priority: "low" | "medium" | "high" | "urgent";
  joinedAt: Date;
  aiPredictedTime?: number;
}

interface ServiceCounter {
  id: string;
  name: string;
  serviceType: string;
  isActive: boolean;
  currentPatient?: QueueItem;
  staffMember?: string;
  department: string;
}

export default function QueueDashboard() {
  const [queues, setQueues] = useState<QueueItem[]>([
    {
      id: "1",
      patientName: "John Smith",
      serviceType: "General Consultation",
      queueNumber: 1,
      estimatedWaitTime: 15,
      status: "serving",
      priority: "medium",
      joinedAt: new Date(Date.now() - 10 * 60 * 1000),
      aiPredictedTime: 12
    },
    {
      id: "2",
      patientName: "Maria Garcia",
      serviceType: "Cardiology",
      queueNumber: 2,
      estimatedWaitTime: 25,
      status: "waiting",
      priority: "high",
      joinedAt: new Date(Date.now() - 5 * 60 * 1000),
      aiPredictedTime: 18
    },
    {
      id: "3",
      patientName: "Robert Johnson",
      serviceType: "Laboratory",
      queueNumber: 3,
      estimatedWaitTime: 8,
      status: "waiting",
      priority: "low",
      joinedAt: new Date(Date.now() - 2 * 60 * 1000),
      aiPredictedTime: 10
    },
    {
      id: "4",
      patientName: "Sarah Wilson",
      serviceType: "Emergency",
      queueNumber: 4,
      estimatedWaitTime: 5,
      status: "called",
      priority: "urgent",
      joinedAt: new Date(Date.now() - 1 * 60 * 1000),
      aiPredictedTime: 3
    }
  ]);

  const [serviceCounters, setServiceCounters] = useState<ServiceCounter[]>([
    {
      id: "counter1",
      name: "Room 101",
      serviceType: "General Consultation",
      department: "Internal Medicine",
      isActive: true,
      staffMember: "Dr. Alice Johnson",
      currentPatient: queues.find(q => q.status === "serving")
    },
    {
      id: "counter2",
      name: "Room 205",
      serviceType: "Cardiology",
      department: "Cardiology",
      isActive: true,
      staffMember: "Dr. Bob Smith"
    },
    {
      id: "counter3",
      name: "Lab Station 1",
      serviceType: "Laboratory",
      department: "Laboratory",
      isActive: false
    },
    {
      id: "counter4",
      name: "Emergency Bay 1",
      serviceType: "Emergency",
      department: "Emergency",
      isActive: true,
      staffMember: "Dr. Carol Davis"
    }
  ]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent": return "bg-red-500";
      case "high": return "bg-orange-500";
      case "medium": return "bg-yellow-500";
      case "low": return "bg-green-500";
      default: return "bg-gray-500";
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case "urgent": return <AlertCircle className="h-4 w-4" />;
      case "high": return <Heart className="h-4 w-4" />;
      case "medium": return <Activity className="h-4 w-4" />;
      case "low": return <CheckCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "waiting": return "bg-yellow-500";
      case "called": return "bg-blue-500";
      case "serving": return "bg-green-500";
      case "completed": return "bg-gray-500";
      default: return "bg-gray-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "waiting": return <Clock className="h-4 w-4" />;
      case "called": return <AlertCircle className="h-4 w-4" />;
      case "serving": return <Stethoscope className="h-4 w-4" />;
      case "completed": return <CheckCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const totalWaiting = queues.filter(q => q.status === "waiting").length;
  const totalServing = queues.filter(q => q.status === "serving").length;
  const urgentCases = queues.filter(q => q.priority === "urgent").length;
  const averageWaitTime = Math.round(queues.reduce((acc, q) => acc + (q.aiPredictedTime || q.estimatedWaitTime), 0) / queues.length);

  return (
    <div className="bg-white min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Hospital Queue Management</h1>
          <p className="text-gray-600">AI-powered patient flow monitoring and optimization</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Patients Waiting</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalWaiting}</div>
              <p className="text-xs text-muted-foreground">in queue</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Currently Serving</CardTitle>
              <Stethoscope className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalServing}</div>
              <p className="text-xs text-muted-foreground">patients being seen</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI Predicted Wait</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{averageWaitTime}m</div>
              <p className="text-xs text-muted-foreground">average prediction</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Urgent Cases</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{urgentCases}</div>
              <p className="text-xs text-muted-foreground">require immediate attention</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Current Queue */}
          <Card>
            <CardHeader>
              <CardTitle>Patient Queue</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {queues.map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`w-8 h-8 rounded-full ${getStatusColor(item.status)} flex items-center justify-center text-white text-sm font-bold`}>
                        {item.queueNumber}
                      </div>
                      <div>
                        <p className="font-medium">{item.patientName}</p>
                        <p className="text-sm text-gray-500">{item.serviceType}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className={`flex items-center space-x-1 ${item.priority === 'urgent' ? 'border-red-500 text-red-700' : ''}`}>
                            {getPriorityIcon(item.priority)}
                            <span className="capitalize">{item.priority}</span>
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline" className="flex items-center space-x-1">
                        {getStatusIcon(item.status)}
                        <span className="capitalize">{item.status}</span>
                      </Badge>
                      <div className="text-right">
                        <div className="flex items-center space-x-1">
                          <Brain className="h-3 w-3 text-blue-500" />
                          <p className="text-sm font-medium text-blue-600">{item.aiPredictedTime}m</p>
                        </div>
                        <p className="text-xs text-gray-500">AI prediction</p>
                        <p className="text-xs text-gray-400">Est: {item.estimatedWaitTime}m</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Service Areas */}
          <Card>
            <CardHeader>
              <CardTitle>Service Areas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {serviceCounters.map((counter) => (
                  <div key={counter.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${counter.isActive ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <h3 className="font-medium">{counter.name}</h3>
                      </div>
                      <Badge variant={counter.isActive ? "default" : "secondary"}>
                        {counter.isActive ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p>Department: {counter.department}</p>
                      <p>Service: {counter.serviceType}</p>
                      {counter.staffMember && (
                        <p>Staff: {counter.staffMember}</p>
                      )}
                    </div>
                    {counter.currentPatient && (
                      <div className="bg-blue-50 p-2 rounded text-sm mt-2">
                        Currently treating: {counter.currentPatient.patientName}
                      </div>
                    )}
                    {counter.isActive && !counter.currentPatient && (
                      <div className="bg-green-50 p-2 rounded text-sm text-green-700 mt-2">
                        Available for next patient
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Insights */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-blue-600" />
              <span>AI-Powered Insights & Recommendations</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Patient Flow Prediction</h4>
                <p className="text-sm text-blue-700 mb-2">Expected busy period: 2:00 PM - 4:00 PM</p>
                <p className="text-xs text-blue-600">AI confidence: 87%</p>
                <Progress value={87} className="mt-2" />
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-2">Resource Optimization</h4>
                <p className="text-sm text-yellow-700 mb-2">Open Lab Station 1 in 15 minutes</p>
                <p className="text-xs text-yellow-600">Predicted 3 lab appointments incoming</p>
                <Button size="sm" className="mt-2">Apply AI Suggestion</Button>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">Efficiency Score</h4>
                <p className="text-sm text-green-700 mb-2">Current efficiency: 92% (Excellent)</p>
                <p className="text-xs text-green-600">AI-optimized scheduling active</p>
                <Progress value={92} className="mt-2" />
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
              <h4 className="font-medium text-purple-900 mb-2 flex items-center">
                <Brain className="h-4 w-4 mr-2" />
                Real-time AI Analysis
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-purple-700">• Analyzing patient arrival patterns</p>
                  <p className="text-purple-700">• Optimizing appointment scheduling</p>
                  <p className="text-purple-700">• Predicting service completion times</p>
                </div>
                <div>
                  <p className="text-blue-700">• Monitoring staff workload distribution</p>
                  <p className="text-blue-700">• Identifying bottlenecks in real-time</p>
                  <p className="text-blue-700">• Suggesting resource reallocation</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}