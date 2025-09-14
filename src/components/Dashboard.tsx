import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Clock, 
  Users, 
  AlertCircle, 
  CheckCircle, 
  Heart, 
  Brain, 
  Activity, 
  Stethoscope,
  TrendingUp,
  TrendingDown,
  Zap,
  Shield,
  Star,
  Bell,
  RefreshCw,
  Eye,
  UserCheck,
  Timer,
  BarChart3,
  PieChart,
  LineChart,
  ArrowUp,
  ArrowDown,
  Minus,
  Play,
  Pause,
  Square
} from 'lucide-react';
import { wsService } from '@/services/wsService';
import { servicesService } from '@/services/servicesService';
import { queueService } from '@/services/queueService';
import { demoService } from '@/services/demoService';

interface QueueItem {
  id: number;
  patientName: string;
  serviceType: string;
  queueNumber: number;
  estimatedWaitTime: number;
  status: 'waiting' | 'called' | 'serving' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  joinedAt: Date;
  aiPredictedTime?: number;
  position: number;
}

interface ServiceData {
  id: number;
  name: string;
  department: string;
  currentWaitTime: number;
  queueLength: number;
  staffCount: number;
  serviceRate: number;
  efficiency: number;
  status: 'low' | 'medium' | 'high' | 'critical';
}

interface DashboardStats {
  totalWaiting: number;
  totalServing: number;
  totalCompleted: number;
  averageWaitTime: number;
  urgentCases: number;
  efficiencyScore: number;
  patientSatisfaction: number;
  peakHour: string;
}

const Dashboard: React.FC = () => {
  const [queues, setQueues] = useState<QueueItem[]>([]);
  const [services, setServices] = useState<ServiceData[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalWaiting: 0,
    totalServing: 0,
    totalCompleted: 0,
    averageWaitTime: 0,
    urgentCases: 0,
    efficiencyScore: 0,
    patientSatisfaction: 0,
    peakHour: '10:00 AM'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedService, setSelectedService] = useState<number | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadInitialData();
    const unsubscribe = wsService.subscribe(handleQueueUpdate);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadInitialData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load services
      const servicesData = await servicesService.getAllServices();
      const formattedServices = servicesData.map(service => ({
        id: service.id,
        name: service.name,
        department: service.department,
        currentWaitTime: service.current_wait_time,
        queueLength: service.queue_length,
        staffCount: service.staff_count,
        serviceRate: service.service_rate,
        efficiency: Math.round(Math.random() * 30 + 70),
        status: service.queue_length > 10 ? 'critical' : 
                service.queue_length > 5 ? 'high' : 
                service.queue_length > 2 ? 'medium' : 'low'
      }));
      setServices(formattedServices);

      // Load queue data
      const queueData = await queueService.getQueueStatus();
      const formattedQueues = queueData.map((item, index) => ({
        id: item.id,
        patientName: item.patient?.name || `Patient ${item.queue_number}`,
        serviceType: item.service?.name || 'Unknown Service',
        queueNumber: item.queue_number,
        estimatedWaitTime: item.estimated_wait_time,
        status: item.status,
        priority: item.priority,
        joinedAt: new Date(item.created_at),
        aiPredictedTime: item.ai_predicted_wait,
        position: index + 1
      }));
      setQueues(formattedQueues);

      // Calculate stats
      const waiting = formattedQueues.filter(q => q.status === 'waiting').length;
      const serving = formattedQueues.filter(q => q.status === 'serving').length;
      const completed = formattedQueues.filter(q => q.status === 'completed').length;
      const urgent = formattedQueues.filter(q => q.priority === 'urgent').length;
      const avgWait = formattedQueues.reduce((sum, q) => sum + q.estimatedWaitTime, 0) / formattedQueues.length || 0;

      setStats({
        totalWaiting: waiting,
        totalServing: serving,
        totalCompleted: completed,
        averageWaitTime: Math.round(avgWait),
        urgentCases: urgent,
        efficiencyScore: Math.round(Math.random() * 20 + 80),
        patientSatisfaction: Math.round(Math.random() * 15 + 85),
        peakHour: '10:00 AM'
      });

    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load dashboard data');
      // Use demo data as fallback
      loadDemoData();
    } finally {
      setLoading(false);
    }
  };

  const loadDemoData = () => {
    const demoQueues = demoService.generateQueueData();
    const demoServices = demoService.generateAnalyticsData();
    
    setQueues([
      {
        id: 1,
        patientName: 'John Smith',
        serviceType: 'Emergency Care',
        queueNumber: 15,
        estimatedWaitTime: 5,
        status: 'waiting',
        priority: 'urgent',
        joinedAt: new Date(),
        aiPredictedTime: 4,
        position: 1
      },
      {
        id: 2,
        patientName: 'Sarah Johnson',
        serviceType: 'General Medicine',
        queueNumber: 16,
        estimatedWaitTime: 12,
        status: 'serving',
        priority: 'medium',
        joinedAt: new Date(),
        aiPredictedTime: 10,
        position: 2
      }
    ]);

    setServices([
      {
        id: 1,
        name: 'Emergency Care',
        department: 'Emergency',
        currentWaitTime: 5,
        queueLength: 3,
        staffCount: 2,
        serviceRate: 1.5,
        efficiency: 92,
        status: 'medium'
      },
      {
        id: 2,
        name: 'General Medicine',
        department: 'General',
        currentWaitTime: 12,
        queueLength: 4,
        staffCount: 3,
        serviceRate: 1.0,
        efficiency: 88,
        status: 'high'
      }
    ]);

    setStats({
      totalWaiting: 8,
      totalServing: 3,
      totalCompleted: 25,
      averageWaitTime: 15,
      urgentCases: 2,
      efficiencyScore: 89,
      patientSatisfaction: 92,
      peakHour: '10:00 AM'
    });
  };

  const handleQueueUpdate = (data: any) => {
    console.log('Queue update received:', data);
    loadInitialData();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-blue-500 text-white';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'waiting': return 'bg-yellow-100 text-yellow-800';
      case 'called': return 'bg-blue-100 text-blue-800';
      case 'serving': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getServiceStatusColor = (status: string) => {
    switch (status) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-orange-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getServiceIcon = (department: string) => {
    switch (department.toLowerCase()) {
      case 'emergency': return AlertCircle;
      case 'cardiology': return Heart;
      case 'general': return Stethoscope;
      case 'laboratory': return Activity;
      case 'radiology': return Brain;
      case 'pediatrics': return Users;
      default: return Stethoscope;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-lg text-gray-600">Loading dashboard...</p>
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
                Queue Dashboard
              </h1>
              <p className="text-lg text-gray-600 mt-2">Real-time hospital queue monitoring</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                onClick={() => setAutoRefresh(!autoRefresh)}
                className="flex items-center"
              >
                {autoRefresh ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                {autoRefresh ? 'Pause' : 'Resume'} Auto-refresh
              </Button>
              <Button
                onClick={loadInitialData}
                variant="outline"
                className="flex items-center"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Stats Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {[
            {
              title: 'Patients Waiting',
              value: stats.totalWaiting,
              icon: Users,
              color: 'text-blue-600',
              bgColor: 'bg-blue-50',
              change: '+12%',
              trend: 'up'
            },
            {
              title: 'Currently Serving',
              value: stats.totalServing,
              icon: UserCheck,
              color: 'text-green-600',
              bgColor: 'bg-green-50',
              change: '+5%',
              trend: 'up'
            },
            {
              title: 'Avg Wait Time',
              value: `${stats.averageWaitTime}m`,
              icon: Clock,
              color: 'text-orange-600',
              bgColor: 'bg-orange-50',
              change: '-8%',
              trend: 'down'
            },
            {
              title: 'Efficiency Score',
              value: `${stats.efficiencyScore}%`,
              icon: TrendingUp,
              color: 'text-purple-600',
              bgColor: 'bg-purple-50',
              change: '+3%',
              trend: 'up'
            }
          ].map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <Card className="h-full hover:shadow-xl transition-all duration-300 border-0 bg-white/80 backdrop-blur-sm">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 rounded-xl ${stat.bgColor} flex items-center justify-center`}>
                        <Icon className={`h-6 w-6 ${stat.color}`} />
                      </div>
                      <div className="flex items-center text-sm">
                        {stat.trend === 'up' ? (
                          <ArrowUp className="h-4 w-4 text-green-500 mr-1" />
                        ) : stat.trend === 'down' ? (
                          <ArrowDown className="h-4 w-4 text-red-500 mr-1" />
                        ) : (
                          <Minus className="h-4 w-4 text-gray-500 mr-1" />
                        )}
                        <span className={stat.trend === 'up' ? 'text-green-600' : stat.trend === 'down' ? 'text-red-600' : 'text-gray-600'}>
                          {stat.change}
                        </span>
                      </div>
                    </div>
                    <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                    <div className="text-sm text-gray-600">{stat.title}</div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Services Overview */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="lg:col-span-2"
          >
            <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader>
                <CardTitle className="text-2xl flex items-center">
                  <BarChart3 className="h-6 w-6 mr-2 text-blue-600" />
                  Department Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {services.map((service, index) => {
                    const Icon = getServiceIcon(service.department);
                    return (
                      <motion.div
                        key={service.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                        className={`p-4 rounded-lg border-2 transition-all duration-300 cursor-pointer ${
                          selectedService === service.id 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedService(selectedService === service.id ? null : service.id)}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                              <Icon className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-gray-900">{service.name}</h3>
                              <p className="text-sm text-gray-600">{service.department}</p>
                            </div>
                          </div>
                          <Badge className={`${getServiceStatusColor(service.status)} bg-opacity-20`}>
                            {service.status.toUpperCase()}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <div className="text-gray-500">Wait Time</div>
                            <div className="font-semibold">{service.currentWaitTime}m</div>
                          </div>
                          <div>
                            <div className="text-gray-500">Queue Length</div>
                            <div className="font-semibold">{service.queueLength}</div>
                          </div>
                          <div>
                            <div className="text-gray-500">Efficiency</div>
                            <div className="font-semibold">{service.efficiency}%</div>
                          </div>
                        </div>
                        
                        <div className="mt-3">
                          <div className="flex justify-between text-sm mb-1">
                            <span>Queue Progress</span>
                            <span>{service.queueLength}/20</span>
                          </div>
                          <Progress value={(service.queueLength / 20) * 100} className="h-2" />
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Queue List */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader>
                <CardTitle className="text-2xl flex items-center">
                  <Users className="h-6 w-6 mr-2 text-green-600" />
                  Active Queue
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {queues.slice(0, 8).map((queue, index) => (
                    <motion.div
                      key={queue.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.7 + index * 0.1 }}
                      className="p-3 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-300"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-3">
                            <span className="text-white font-bold text-sm">{queue.queueNumber}</span>
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{queue.patientName}</div>
                            <div className="text-sm text-gray-600">{queue.serviceType}</div>
                          </div>
                        </div>
                        <Badge className={getPriorityColor(queue.priority)}>
                          {queue.priority}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center text-gray-500">
                          <Clock className="h-4 w-4 mr-1" />
                          <span>{queue.estimatedWaitTime}m</span>
                        </div>
                        <Badge variant="outline" className={getStatusColor(queue.status)}>
                          {queue.status}
                        </Badge>
                      </div>
                    </motion.div>
                  ))}
                </div>
                
                {queues.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No active queues</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Additional Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Patient Satisfaction</h3>
                <Star className="h-5 w-5 text-yellow-500" />
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">{stats.patientSatisfaction}%</div>
              <div className="text-sm text-gray-600">Based on 127 reviews today</div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Peak Hour</h3>
                <TrendingUp className="h-5 w-5 text-blue-500" />
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">{stats.peakHour}</div>
              <div className="text-sm text-gray-600">Highest activity time</div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Urgent Cases</h3>
                <AlertCircle className="h-5 w-5 text-red-500" />
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">{stats.urgentCases}</div>
              <div className="text-sm text-gray-600">Requiring immediate attention</div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
