import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  BarChart3,
  Users,
  Clock,
  Settings,
  Bell,
  LayoutDashboard,
  UserCog,
} from "lucide-react";
import QueueAnalytics from "./QueueAnalytics";
import StaffManagement from "./StaffManagement";

interface AdminDashboardProps {
  username?: string;
  organization?: string;
}

const AdminDashboard = ({
  username = "Admin User",
  organization = "SwiftQueue Organization",
}: AdminDashboardProps) => {
  const [activeTab, setActiveTab] = useState("overview");

  // Mock data for the dashboard
  const queueStats = {
    totalInQueue: 42,
    averageWaitTime: "12 mins",
    servedToday: 128,
    activeCounters: 5,
  };

  const recentCustomers = [
    {
      id: "A123",
      name: "John Smith",
      service: "Account Services",
      waitTime: "5 mins",
      status: "waiting",
    },
    {
      id: "B456",
      name: "Sarah Johnson",
      service: "Loan Consultation",
      waitTime: "10 mins",
      status: "waiting",
    },
    {
      id: "C789",
      name: "Michael Brown",
      service: "General Inquiry",
      waitTime: "2 mins",
      status: "serving",
    },
    {
      id: "D012",
      name: "Emily Davis",
      service: "Account Services",
      waitTime: "15 mins",
      status: "waiting",
    },
  ];

  const activeStaff = [
    {
      id: 1,
      name: "Alex Morgan",
      counter: "Counter 1",
      service: "Account Services",
      status: "serving",
    },
    {
      id: 2,
      name: "Taylor Reed",
      counter: "Counter 2",
      service: "Loan Consultation",
      status: "serving",
    },
    {
      id: 3,
      name: "Jordan Lee",
      counter: "Counter 3",
      service: "General Inquiry",
      status: "available",
    },
    {
      id: 4,
      name: "Casey Kim",
      counter: "Counter 4",
      service: "Account Services",
      status: "break",
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "waiting":
        return <Badge variant="secondary">Waiting</Badge>;
      case "serving":
        return <Badge variant="default">Serving</Badge>;
      case "available":
        return <Badge className="bg-green-500">Available</Badge>;
      case "break":
        return <Badge variant="outline">On Break</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  return (
    <div className="bg-background min-h-screen p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">{organization}</p>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon">
            <Bell className="h-5 w-5" />
          </Button>
          <Button variant="outline" size="icon">
            <Settings className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-2">
            <Avatar>
              <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=admin" />
              <AvatarFallback>AU</AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{username}</p>
              <p className="text-xs text-muted-foreground">Administrator</p>
            </div>
          </div>
        </div>
      </div>

      <Tabs
        defaultValue="overview"
        value={activeTab}
        onValueChange={setActiveTab}
        className="w-full"
      >
        <TabsList className="mb-6">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <LayoutDashboard className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="queue" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Queue Management
          </TabsTrigger>
          <TabsTrigger value="staff" className="flex items-center gap-2">
            <UserCog className="h-4 w-4" />
            Staff Management
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total in Queue
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Users className="h-5 w-5 text-primary mr-2" />
                  <div className="text-2xl font-bold">
                    {queueStats.totalInQueue}
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Average Wait Time
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Clock className="h-5 w-5 text-primary mr-2" />
                  <div className="text-2xl font-bold">
                    {queueStats.averageWaitTime}
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Served Today
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Users className="h-5 w-5 text-primary mr-2" />
                  <div className="text-2xl font-bold">
                    {queueStats.servedToday}
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Active Counters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <LayoutDashboard className="h-5 w-5 text-primary mr-2" />
                  <div className="text-2xl font-bold">
                    {queueStats.activeCounters}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Customers</CardTitle>
                <CardDescription>
                  Customers currently in queue or being served
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentCustomers.map((customer) => (
                    <div
                      key={customer.id}
                      className="flex items-center justify-between border-b pb-2 last:border-0"
                    >
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarImage
                            src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${customer.id}`}
                          />
                          <AvatarFallback>
                            {customer.name.substring(0, 2)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{customer.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {customer.service}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p className="text-sm">Wait: {customer.waitTime}</p>
                          <p>{getStatusBadge(customer.status)}</p>
                        </div>
                        <Button variant="ghost" size="sm">
                          Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Active Staff</CardTitle>
                <CardDescription>
                  Staff currently serving customers
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {activeStaff.map((staff) => (
                    <div
                      key={staff.id}
                      className="flex items-center justify-between border-b pb-2 last:border-0"
                    >
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarImage
                            src={`https://api.dicebear.com/7.x/avataaars/svg?seed=staff${staff.id}`}
                          />
                          <AvatarFallback>
                            {staff.name.substring(0, 2)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{staff.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {staff.counter} - {staff.service}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div>{getStatusBadge(staff.status)}</div>
                        <Button variant="ghost" size="sm">
                          Manage
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="queue" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Queue Management</CardTitle>
              <CardDescription>
                Manage customer queues and service counters
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Queue management interface would be implemented here.
              </p>
              <div className="flex flex-col gap-4">
                <Button>Add Customer to Queue</Button>
                <Button variant="outline">Manage Service Counters</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="staff" className="space-y-6">
          <StaffManagement />
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <QueueAnalytics />
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>System Settings</CardTitle>
              <CardDescription>
                Configure system parameters and notification settings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Settings interface would be implemented here.
              </p>
              <div className="flex flex-col gap-4">
                <Button>Notification Settings</Button>
                <Button variant="outline">AI Configuration</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminDashboard;
