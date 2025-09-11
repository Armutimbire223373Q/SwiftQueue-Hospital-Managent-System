import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Clock, Users, AlertCircle, CheckCircle } from "lucide-react";

interface QueueItem {
  id: string;
  customerName: string;
  serviceType: string;
  queueNumber: number;
  estimatedWaitTime: number;
  status: "waiting" | "called" | "serving" | "completed";
  joinedAt: Date;
}

interface ServiceCounter {
  id: string;
  name: string;
  serviceType: string;
  isActive: boolean;
  currentCustomer?: QueueItem;
  staffMember?: string;
}

export default function QueueDashboard() {
  const [queues, setQueues] = useState<QueueItem[]>([
    {
      id: "1",
      customerName: "John Doe",
      serviceType: "Banking",
      queueNumber: 1,
      estimatedWaitTime: 5,
      status: "serving",
      joinedAt: new Date(Date.now() - 10 * 60 * 1000)
    },
    {
      id: "2",
      customerName: "Jane Smith",
      serviceType: "Banking",
      queueNumber: 2,
      estimatedWaitTime: 12,
      status: "waiting",
      joinedAt: new Date(Date.now() - 5 * 60 * 1000)
    },
    {
      id: "3",
      customerName: "Mike Johnson",
      serviceType: "Loans",
      queueNumber: 3,
      estimatedWaitTime: 18,
      status: "waiting",
      joinedAt: new Date(Date.now() - 2 * 60 * 1000)
    },
    {
      id: "4",
      customerName: "Sarah Wilson",
      serviceType: "Customer Service",
      queueNumber: 4,
      estimatedWaitTime: 25,
      status: "called",
      joinedAt: new Date(Date.now() - 1 * 60 * 1000)
    }
  ]);

  const [serviceCounters, setServiceCounters] = useState<ServiceCounter[]>([
    {
      id: "counter1",
      name: "Counter 1",
      serviceType: "Banking",
      isActive: true,
      staffMember: "Alice Johnson",
      currentCustomer: queues.find(q => q.status === "serving")
    },
    {
      id: "counter2",
      name: "Counter 2",
      serviceType: "Loans",
      isActive: true,
      staffMember: "Bob Smith"
    },
    {
      id: "counter3",
      name: "Counter 3",
      serviceType: "Customer Service",
      isActive: false
    }
  ]);

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
      case "serving": return <Users className="h-4 w-4" />;
      case "completed": return <CheckCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const totalWaiting = queues.filter(q => q.status === "waiting").length;
  const totalServing = queues.filter(q => q.status === "serving").length;
  const averageWaitTime = Math.round(queues.reduce((acc, q) => acc + q.estimatedWaitTime, 0) / queues.length);

  return (
    <div className="bg-white min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">SwiftQueue Dashboard</h1>
          <p className="text-gray-600">Real-time queue management and monitoring</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Waiting</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalWaiting}</div>
              <p className="text-xs text-muted-foreground">customers in queue</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Currently Serving</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalServing}</div>
              <p className="text-xs text-muted-foreground">customers being served</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Wait Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{averageWaitTime}m</div>
              <p className="text-xs text-muted-foreground">estimated average</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Counters</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{serviceCounters.filter(c => c.isActive).length}</div>
              <p className="text-xs text-muted-foreground">out of {serviceCounters.length} total</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Current Queue */}
          <Card>
            <CardHeader>
              <CardTitle>Current Queue</CardTitle>
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
                        <p className="font-medium">{item.customerName}</p>
                        <p className="text-sm text-gray-500">{item.serviceType}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline" className="flex items-center space-x-1">
                        {getStatusIcon(item.status)}
                        <span className="capitalize">{item.status}</span>
                      </Badge>
                      <div className="text-right">
                        <p className="text-sm font-medium">{item.estimatedWaitTime}m</p>
                        <p className="text-xs text-gray-500">wait time</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Service Counters */}
          <Card>
            <CardHeader>
              <CardTitle>Service Counters</CardTitle>
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
                    <div className="text-sm text-gray-600 mb-2">
                      Service: {counter.serviceType}
                    </div>
                    {counter.staffMember && (
                      <div className="text-sm text-gray-600 mb-2">
                        Staff: {counter.staffMember}
                      </div>
                    )}
                    {counter.currentCustomer && (
                      <div className="bg-blue-50 p-2 rounded text-sm">
                        Currently serving: {counter.currentCustomer.customerName}
                      </div>
                    )}
                    {counter.isActive && !counter.currentCustomer && (
                      <div className="bg-green-50 p-2 rounded text-sm text-green-700">
                        Available for next customer
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
            <CardTitle>AI Insights & Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Peak Hour Prediction</h4>
                <p className="text-sm text-blue-700">Expected busy period: 2:00 PM - 4:00 PM</p>
                <Progress value={75} className="mt-2" />
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-2">Staff Recommendation</h4>
                <p className="text-sm text-yellow-700">Consider opening Counter 3 in 15 minutes</p>
                <Button size="sm" className="mt-2">Apply Suggestion</Button>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">Efficiency Score</h4>
                <p className="text-sm text-green-700">Current efficiency: 87% (Good)</p>
                <Progress value={87} className="mt-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}