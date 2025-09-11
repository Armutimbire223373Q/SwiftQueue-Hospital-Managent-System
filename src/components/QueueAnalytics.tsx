import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import DatePickerWithRange from "@/components/ui/date-picker-with-range";
import { Button } from "@/components/ui/button";
import {
  BarChart,
  LineChart,
  PieChart,
  Activity,
  Users,
  Clock,
  TrendingUp,
  Calendar,
} from "lucide-react";

interface QueueAnalyticsProps {
  data?: {
    waitTimes: Array<{ date: string; avgTime: number }>;
    peakHours: Array<{ hour: number; count: number }>;
    serviceDistribution: Array<{ service: string; count: number }>;
    recommendations: Array<{ title: string; description: string }>;
  };
}

const QueueAnalytics: React.FC<QueueAnalyticsProps> = ({
  data = {
    waitTimes: [
      { date: "2023-06-01", avgTime: 12 },
      { date: "2023-06-02", avgTime: 15 },
      { date: "2023-06-03", avgTime: 10 },
      { date: "2023-06-04", avgTime: 18 },
      { date: "2023-06-05", avgTime: 14 },
      { date: "2023-06-06", avgTime: 9 },
      { date: "2023-06-07", avgTime: 11 },
    ],
    peakHours: [
      { hour: 9, count: 45 },
      { hour: 10, count: 62 },
      { hour: 11, count: 78 },
      { hour: 12, count: 56 },
      { hour: 13, count: 40 },
      { hour: 14, count: 65 },
      { hour: 15, count: 72 },
      { hour: 16, count: 58 },
      { hour: 17, count: 30 },
    ],
    serviceDistribution: [
      { service: "General Inquiry", count: 120 },
      { service: "Account Services", count: 85 },
      { service: "Technical Support", count: 65 },
      { service: "Payments", count: 95 },
      { service: "Complaints", count: 40 },
    ],
    recommendations: [
      {
        title: "Increase Staff at 11 AM",
        description:
          "Add 2 more staff members during the 11 AM peak to reduce wait times by an estimated 35%.",
      },
      {
        title: "Technical Support Training",
        description:
          "Technical support has 20% longer service times than other departments. Consider additional training.",
      },
      {
        title: "Optimize Lunch Breaks",
        description:
          "Stagger lunch breaks between 12-2 PM to maintain service capacity during this busy period.",
      },
      {
        title: "Add Self-Service Kiosk",
        description:
          "Implement self-service kiosks for payment services to reduce queue load by an estimated 25%.",
      },
    ],
  },
}) => {
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(2023, 5, 1),
    to: new Date(2023, 5, 7),
  });
  const [serviceType, setServiceType] = useState<string>("all");

  return (
    <div className="bg-background p-6 rounded-lg w-full">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div>
          <h2 className="text-2xl font-bold">Queue Analytics</h2>
          <p className="text-muted-foreground">
            AI-powered insights and recommendations
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
          <DatePickerWithRange className="w-full sm:w-auto" />
          <Select defaultValue="all" onValueChange={setServiceType}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Service Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Services</SelectItem>
              <SelectItem value="general">General Inquiry</SelectItem>
              <SelectItem value="account">Account Services</SelectItem>
              <SelectItem value="technical">Technical Support</SelectItem>
              <SelectItem value="payments">Payments</SelectItem>
              <SelectItem value="complaints">Complaints</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Calendar className="mr-2 h-4 w-4" /> Export Report
          </Button>
        </div>
      </div>

      <Tabs defaultValue="wait-times" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="wait-times">
            <Clock className="mr-2 h-4 w-4" /> Wait Times
          </TabsTrigger>
          <TabsTrigger value="peak-hours">
            <Activity className="mr-2 h-4 w-4" /> Peak Hours
          </TabsTrigger>
          <TabsTrigger value="service-distribution">
            <PieChart className="mr-2 h-4 w-4" /> Service Distribution
          </TabsTrigger>
          <TabsTrigger value="recommendations">
            <TrendingUp className="mr-2 h-4 w-4" /> Recommendations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="wait-times" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Average Wait Times</CardTitle>
              <CardDescription>
                Historical wait time trends by day
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] flex items-center justify-center border border-dashed rounded-md p-4">
                <div className="text-center">
                  <LineChart className="h-16 w-16 mx-auto text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Line chart visualization of wait times would render here
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Data shows average wait time of{" "}
                    {Math.round(
                      data.waitTimes.reduce(
                        (acc, item) => acc + item.avgTime,
                        0,
                      ) / data.waitTimes.length,
                    )}{" "}
                    minutes over the selected period
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Current Average</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Clock className="h-8 w-8 text-primary mr-2" />
                  <div>
                    <p className="text-3xl font-bold">
                      {data.waitTimes[data.waitTimes.length - 1].avgTime} min
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Today's average wait time
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Weekly Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <TrendingUp className="h-8 w-8 text-green-500 mr-2" />
                  <div>
                    <p className="text-3xl font-bold">-12%</p>
                    <p className="text-xs text-muted-foreground">
                      Improvement from last week
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Customers Served</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Users className="h-8 w-8 text-blue-500 mr-2" />
                  <div>
                    <p className="text-3xl font-bold">405</p>
                    <p className="text-xs text-muted-foreground">
                      Total for selected period
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="peak-hours">
          <Card>
            <CardHeader>
              <CardTitle>Peak Hours Analysis</CardTitle>
              <CardDescription>Customer traffic by hour of day</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px] flex items-center justify-center border border-dashed rounded-md p-4">
                <div className="text-center">
                  <BarChart className="h-16 w-16 mx-auto text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Bar chart visualization of customer traffic by hour would
                    render here
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Peak hour identified at{" "}
                    {
                      data.peakHours.reduce(
                        (max, hour) => (hour.count > max.count ? hour : max),
                        { hour: 0, count: 0 },
                      ).hour
                    }
                    :00 with{" "}
                    {
                      data.peakHours.reduce(
                        (max, hour) => (hour.count > max.count ? hour : max),
                        { hour: 0, count: 0 },
                      ).count
                    }{" "}
                    customers
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="service-distribution">
          <Card>
            <CardHeader>
              <CardTitle>Service Type Distribution</CardTitle>
              <CardDescription>
                Breakdown of services requested by customers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px] flex items-center justify-center border border-dashed rounded-md p-4">
                <div className="text-center">
                  <PieChart className="h-16 w-16 mx-auto text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Pie chart visualization of service distribution would render
                    here
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Most requested service:{" "}
                    {
                      data.serviceDistribution.reduce(
                        (max, service) =>
                          service.count > max.count ? service : max,
                        { service: "", count: 0 },
                      ).service
                    }
                    (
                    {Math.round(
                      (data.serviceDistribution.reduce(
                        (max, service) =>
                          service.count > max.count ? service : max,
                        { service: "", count: 0 },
                      ).count /
                        data.serviceDistribution.reduce(
                          (sum, service) => sum + service.count,
                          0,
                        )) *
                        100,
                    )}
                    % of total)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.recommendations.map((rec, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-lg">{rec.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{rec.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QueueAnalytics;
