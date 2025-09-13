import React, { useState, useEffect } from "react";
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
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  BarChart3,
  LineChart,
  PieChart,
  Activity,
  Users,
  Clock,
  TrendingUp,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Info,
  Zap,
  Loader2
} from "lucide-react";
import { analyticsService } from "@/services/analyticsService";
import type { WaitTimeAnalytics, PeakHourAnalytics, ServiceDistribution, AIRecommendation } from "@/services/analyticsService";

const QueueAnalyticsView: React.FC = () => {
  const [waitTimes, setWaitTimes] = useState<WaitTimeAnalytics[]>([]);
  const [peakHours, setPeakHours] = useState<PeakHourAnalytics[]>([]);
  const [serviceDistribution, setServiceDistribution] = useState<ServiceDistribution[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(),
    to: new Date(),
  });
  const [serviceFilter, setServiceFilter] = useState<string>("all");

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const [waitTimesData, peakHoursData, serviceDistData, recommendationsData] = await Promise.all([
          analyticsService.getWaitTimes(),
          analyticsService.getPeakHours(),
          analyticsService.getServiceDistribution(),
          analyticsService.getAIRecommendations()
        ]);

        setWaitTimes(waitTimesData);
        setPeakHours(peakHoursData);
        setServiceDistribution(serviceDistData);
        setRecommendations(recommendationsData);
        setError(null);
      } catch (err) {
        setError("Failed to fetch analytics data. Please try again later.");
        console.error("Analytics fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
    const pollInterval = setInterval(fetchAnalytics, 60000); // Poll every minute
    return () => clearInterval(pollInterval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading analytics data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  const avgWaitTime = waitTimes.length > 0
    ? Math.round(waitTimes.reduce((acc, item) => acc + item.avgWait, 0) / waitTimes.length)
    : 0;

  const peakHour = peakHours.reduce(
    (max, hour) => (hour.count > max.count ? hour : max),
    { hour: 0, count: 0 }
  );

  const totalServices = serviceDistribution.reduce((sum, service) => sum + service.count, 0);
  const mostRequestedService = serviceDistribution.reduce(
    (max, service) => (service.count > max.count ? service : max),
    { serviceId: 0, count: 0 }
  );

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
          <DatePickerWithRange 
            value={dateRange}
            onChange={(newRange: any) => setDateRange(newRange)}
          />
          <Select value={serviceFilter} onValueChange={setServiceFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Service Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Services</SelectItem>
              {serviceDistribution.map((service) => (
                <SelectItem key={service.serviceId} value={service.serviceId.toString()}>
                  Service {service.serviceId}
                </SelectItem>
              ))}
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
              <CardDescription>Historical wait time trends</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                {/* Chart will be implemented using a charting library */}
                <div className="text-center">
                  <LineChart className="h-16 w-16 mx-auto text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Current average wait time: {avgWaitTime} minutes
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
                    <p className="text-3xl font-bold">{avgWaitTime} min</p>
                    <p className="text-xs text-muted-foreground">Current wait time</p>
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
              <CardDescription>Customer traffic patterns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                {/* Chart will be implemented using a charting library */}
                <div className="text-center">
                  <BarChart3 className="h-16 w-16 mx-auto text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Peak hour: {peakHour.hour}:00 with {peakHour.count} customers
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="service-distribution">
          <Card>
            <CardHeader>
              <CardTitle>Service Distribution</CardTitle>
              <CardDescription>Service utilization breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                {/* Chart will be implemented using a charting library */}
                <div className="text-center">
                  <PieChart className="h-16 w-16 mx-auto text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Most requested: Service {mostRequestedService.serviceId} (
                    {Math.round((mostRequestedService.count / totalServices) * 100)}% of total)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4">
          {recommendations.map((rec, index) => (
            <Alert key={index} variant={
              rec.type === 'critical' ? 'destructive' :
              rec.type === 'warning' ? 'default' :
              rec.type === 'info' ? 'default' : 'default'
            }>
              {rec.type === 'critical' && <AlertTriangle className="h-4 w-4" />}
              {rec.type === 'warning' && <Info className="h-4 w-4" />}
              {rec.type === 'info' && <Info className="h-4 w-4" />}
              {rec.type === 'improvement' && <Zap className="h-4 w-4" />}
              <AlertTitle>{rec.message}</AlertTitle>
              <AlertDescription>
                Action: {rec.action}
              </AlertDescription>
            </Alert>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QueueAnalyticsView;
