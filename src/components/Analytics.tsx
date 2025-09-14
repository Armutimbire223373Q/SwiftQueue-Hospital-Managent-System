import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  LineChart, 
  PieChart, 
  Activity, 
  Users, 
  Clock, 
  TrendingUp, 
  TrendingDown,
  Calendar, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  Zap, 
  Loader2,
  RefreshCw,
  Download,
  Filter,
  Eye,
  Brain,
  Heart,
  Stethoscope,
  AlertCircle,
  Star,
  Target,
  ArrowUp,
  ArrowDown,
  Minus,
  Play,
  Pause,
  BarChart,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon
} from 'lucide-react';
import { analyticsService } from '@/services/analyticsService';
import { demoService } from '@/services/demoService';

interface AnalyticsData {
  waitTimeTrends: Array<{
    hour: number;
    avgWaitTime: number;
    patients: number;
    efficiency: number;
  }>;
  serviceDistribution: Array<{
    name: string;
    patients: number;
    waitTime: number;
    efficiency: number;
    color: string;
  }>;
  peakHours: Array<{
    hour: string;
    patients: number;
    waitTime: number;
    efficiency: number;
  }>;
  dailyStats: {
    totalPatients: number;
    avgWaitTime: number;
    efficiencyScore: number;
    patientSatisfaction: number;
    peakHour: string;
    urgentCases: number;
  };
  recommendations: Array<{
    id: string;
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high' | 'critical';
    impact: string;
    status: 'pending' | 'in_progress' | 'completed';
  }>;
}

const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('7d');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadAnalyticsData();
    if (autoRefresh) {
      const interval = setInterval(loadAnalyticsData, 30000);
      return () => clearInterval(interval);
    }
  }, [timeRange, autoRefresh]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Try to load real data first
      const [waitTimeData, serviceData, peakData, dailyData, recommendations] = await Promise.all([
        analyticsService.getWaitTimeAnalytics(),
        analyticsService.getServiceDistribution(),
        analyticsService.getPeakHourAnalytics(),
        analyticsService.getDailyStats(),
        analyticsService.getAIRecommendations()
      ]);

      setData({
        waitTimeTrends: waitTimeData,
        serviceDistribution: serviceData,
        peakHours: peakData,
        dailyStats: dailyData,
        recommendations: recommendations
      });

    } catch (err) {
      console.error('Failed to load analytics data:', err);
      // Use demo data as fallback
      loadDemoData();
    } finally {
      setLoading(false);
    }
  };

  const loadDemoData = () => {
    const demoData = demoService.generateAnalyticsData();
    
    setData({
      waitTimeTrends: demoData.hourlyData.map((item, index) => ({
        hour: item.hour,
        avgWaitTime: item.waitTime,
        patients: item.patients,
        efficiency: Math.round(Math.random() * 30 + 70)
      })),
      serviceDistribution: demoData.departmentStats.map((dept, index) => ({
        name: dept.name,
        patients: dept.patients,
        waitTime: dept.avgWaitTime,
        efficiency: dept.efficiency,
        color: ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'][index % 6]
      })),
      peakHours: [
        { hour: '8:00 AM', patients: 15, waitTime: 8, efficiency: 85 },
        { hour: '9:00 AM', patients: 22, waitTime: 12, efficiency: 78 },
        { hour: '10:00 AM', patients: 28, waitTime: 18, efficiency: 72 },
        { hour: '11:00 AM', patients: 25, waitTime: 15, efficiency: 80 },
        { hour: '2:00 PM', patients: 20, waitTime: 10, efficiency: 88 },
        { hour: '3:00 PM', patients: 18, waitTime: 8, efficiency: 90 }
      ],
      dailyStats: demoData.dailyStats,
      recommendations: [
        {
          id: '1',
          title: 'Increase Staff During Peak Hours',
          description: 'Consider adding 2 additional staff members during 10:00-11:00 AM to reduce wait times',
          priority: 'high',
          impact: 'Could reduce wait times by 25%',
          status: 'pending'
        },
        {
          id: '2',
          title: 'Optimize Emergency Department Flow',
          description: 'Implement priority-based queue management for emergency cases',
          priority: 'critical',
          impact: 'Could improve patient outcomes by 40%',
          status: 'in_progress'
        },
        {
          id: '3',
          title: 'Add AI-Powered Triage',
          description: 'Deploy AI system to automatically prioritize patients based on symptoms',
          priority: 'medium',
          impact: 'Could improve efficiency by 30%',
          status: 'pending'
        }
      ]
    });
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-blue-500 text-white';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-lg text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-lg text-gray-600">Failed to load analytics data</p>
          <Button onClick={loadAnalyticsData} className="mt-4">
            Try Again
          </Button>
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
                Analytics Dashboard
              </h1>
              <p className="text-lg text-gray-600 mt-2">AI-powered insights and performance metrics</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg bg-white"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
              <Button
                variant="outline"
                onClick={() => setAutoRefresh(!autoRefresh)}
                className="flex items-center"
              >
                {autoRefresh ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                {autoRefresh ? 'Pause' : 'Resume'} Auto-refresh
              </Button>
              <Button
                onClick={loadAnalyticsData}
                variant="outline"
                className="flex items-center"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Key Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {[
            {
              title: 'Total Patients',
              value: data.dailyStats.totalPatients,
              icon: Users,
              color: 'text-blue-600',
              bgColor: 'bg-blue-50',
              change: '+12%',
              trend: 'up'
            },
            {
              title: 'Avg Wait Time',
              value: `${data.dailyStats.avgWaitTime}m`,
              icon: Clock,
              color: 'text-orange-600',
              bgColor: 'bg-orange-50',
              change: '-8%',
              trend: 'down'
            },
            {
              title: 'Efficiency Score',
              value: `${data.dailyStats.efficiencyScore}%`,
              icon: TrendingUp,
              color: 'text-green-600',
              bgColor: 'bg-green-50',
              change: '+5%',
              trend: 'up'
            },
            {
              title: 'Patient Satisfaction',
              value: `${data.dailyStats.patientSatisfaction}%`,
              icon: Star,
              color: 'text-purple-600',
              bgColor: 'bg-purple-50',
              change: '+3%',
              trend: 'up'
            }
          ].map((metric, index) => {
            const Icon = metric.icon;
            return (
              <motion.div
                key={metric.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-white/80 backdrop-blur-sm">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 rounded-xl ${metric.bgColor} flex items-center justify-center`}>
                        <Icon className={`h-6 w-6 ${metric.color}`} />
                      </div>
                      <div className="flex items-center text-sm">
                        {metric.trend === 'up' ? (
                          <ArrowUp className="h-4 w-4 text-green-500 mr-1" />
                        ) : metric.trend === 'down' ? (
                          <ArrowDown className="h-4 w-4 text-red-500 mr-1" />
                        ) : (
                          <Minus className="h-4 w-4 text-gray-500 mr-1" />
                        )}
                        <span className={metric.trend === 'up' ? 'text-green-600' : metric.trend === 'down' ? 'text-red-600' : 'text-gray-600'}>
                          {metric.change}
                        </span>
                      </div>
                    </div>
                    <div className="text-3xl font-bold text-gray-900 mb-1">{metric.value}</div>
                    <div className="text-sm text-gray-600">{metric.title}</div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white/80 backdrop-blur-sm">
            <TabsTrigger value="overview" className="flex items-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="trends" className="flex items-center">
              <LineChart className="h-4 w-4 mr-2" />
              Trends
            </TabsTrigger>
            <TabsTrigger value="distribution" className="flex items-center">
              <PieChart className="h-4 w-4 mr-2" />
              Distribution
            </TabsTrigger>
            <TabsTrigger value="recommendations" className="flex items-center">
              <Brain className="h-4 w-4 mr-2" />
              AI Insights
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Peak Hours Chart */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Clock className="h-6 w-6 mr-2 text-blue-600" />
                      Peak Hours Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {data.peakHours.map((hour, index) => (
                        <div key={hour.hour} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                          <div className="flex items-center">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-3">
                              <span className="text-white font-bold text-sm">{index + 1}</span>
                            </div>
                            <div>
                              <div className="font-semibold">{hour.hour}</div>
                              <div className="text-sm text-gray-600">{hour.patients} patients</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">{hour.waitTime}m</div>
                            <div className="text-sm text-gray-600">avg wait</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Service Performance */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Activity className="h-6 w-6 mr-2 text-green-600" />
                      Service Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {data.serviceDistribution.map((service, index) => (
                        <div key={service.name} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <div 
                                className="w-4 h-4 rounded-full mr-3"
                                style={{ backgroundColor: service.color }}
                              />
                              <span className="font-medium">{service.name}</span>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold">{service.efficiency}%</div>
                              <div className="text-sm text-gray-600">efficiency</div>
                            </div>
                          </div>
                          <Progress value={service.efficiency} className="h-2" />
                          <div className="flex justify-between text-sm text-gray-600">
                            <span>{service.patients} patients</span>
                            <span>{service.waitTime}m avg wait</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </TabsContent>

          {/* Trends Tab */}
          <TabsContent value="trends" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <LineChart className="h-6 w-6 mr-2 text-purple-600" />
                    Wait Time Trends (24 Hours)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 flex items-end justify-between space-x-2">
                    {data.waitTimeTrends.map((trend, index) => (
                      <div key={trend.hour} className="flex flex-col items-center space-y-2">
                        <div
                          className="bg-gradient-to-t from-blue-500 to-purple-600 rounded-t-lg w-8 transition-all duration-500 hover:scale-110"
                          style={{ height: `${(trend.avgWaitTime / 30) * 200}px` }}
                        />
                        <div className="text-xs text-gray-600">{trend.hour}:00</div>
                        <div className="text-xs font-semibold">{trend.avgWaitTime}m</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          {/* Distribution Tab */}
          <TabsContent value="distribution" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <PieChart className="h-6 w-6 mr-2 text-orange-600" />
                    Service Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      {data.serviceDistribution.map((service, index) => (
                        <div key={service.name} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                          <div className="flex items-center">
                            <div 
                              className="w-6 h-6 rounded-full mr-3"
                              style={{ backgroundColor: service.color }}
                            />
                            <span className="font-medium">{service.name}</span>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">{service.patients}</div>
                            <div className="text-sm text-gray-600">patients</div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="flex items-center justify-center">
                      <div className="w-48 h-48 relative">
                        <div className="absolute inset-0 rounded-full border-8 border-gray-200"></div>
                        {data.serviceDistribution.map((service, index) => {
                          const percentage = (service.patients / data.serviceDistribution.reduce((sum, s) => sum + s.patients, 0)) * 100;
                          const rotation = data.serviceDistribution.slice(0, index).reduce((sum, s) => sum + (s.patients / data.serviceDistribution.reduce((total, t) => total + t.patients, 0)) * 360, 0);
                          return (
                            <div
                              key={service.name}
                              className="absolute inset-0 rounded-full"
                              style={{
                                background: `conic-gradient(from ${rotation}deg, ${service.color} 0deg ${rotation + (percentage * 3.6)}deg, transparent ${rotation + (percentage * 3.6)}deg)`
                              }}
                            />
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          {/* AI Recommendations Tab */}
          <TabsContent value="recommendations" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Brain className="h-6 w-6 mr-2 text-purple-600" />
                    AI-Powered Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {data.recommendations.map((rec, index) => (
                      <motion.div
                        key={rec.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                        className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-300"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-600 rounded-lg flex items-center justify-center mr-3">
                              <Brain className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                              <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={getPriorityColor(rec.priority)}>
                              {rec.priority}
                            </Badge>
                            <Badge variant="outline" className={getStatusColor(rec.status)}>
                              {rec.status}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="text-sm text-gray-600">
                            <strong>Impact:</strong> {rec.impact}
                          </div>
                          <Button size="sm" variant="outline">
                            <Eye className="h-4 w-4 mr-2" />
                            View Details
                          </Button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Analytics;
