import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Monitor,
  Users,
  Clock,
  CheckCircle,
  AlertTriangle,
  Calendar,
  Phone,
  UserCheck,
  Activity,
  TrendingUp,
  Bell,
  Search,
  Filter,
  RefreshCw,
  Plus,
  Edit,
  Eye,
  X,
  Zap,
  Timer,
  UserPlus,
  FileText,
  BarChart3,
  Settings,
  Volume2,
  VolumeX
} from "lucide-react";
import { queueService } from '@/services/queueService';
import { aiService } from '@/services/aiService';

interface QueueItem {
  id: number;
  patientName: string;
  queueNumber: number;
  estimatedWait: number;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  department: string;
  checkInTime: string;
  status: 'waiting' | 'being_served' | 'completed';
}

interface QueueStats {
  totalWaiting: number;
  totalBeingServed: number;
  avgWaitTime: number;
  urgentCases: number;
}

const ReceptionistPortal: React.FC = () => {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [filteredQueue, setFilteredQueue] = useState<QueueItem[]>([]);
  const [stats, setStats] = useState<QueueStats>({
    totalWaiting: 0,
    totalBeingServed: 0,
    avgWaitTime: 0,
    urgentCases: 0
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [urgentAlerts, setUrgentAlerts] = useState<QueueItem[]>([]);
  const [showCheckInDialog, setShowCheckInDialog] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<QueueItem | null>(null);

  useEffect(() => {
    loadQueueData();
    const interval = setInterval(loadQueueData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Filter queue items based on search and filters
    let filtered = queueItems;

    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.queueNumber.toString().includes(searchTerm)
      );
    }

    if (priorityFilter !== 'all') {
      filtered = filtered.filter(item => item.priority === priorityFilter);
    }

    if (departmentFilter !== 'all') {
      filtered = filtered.filter(item => item.department.toLowerCase().includes(departmentFilter.toLowerCase()));
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(item => item.status === statusFilter);
    }

    setFilteredQueue(filtered);

    // Check for urgent cases
    const urgent = queueItems.filter(item => item.priority === 'urgent');
    setUrgentAlerts(urgent);

    // Sound alert for new urgent cases
    if (soundEnabled && urgent.length > 0) {
      // Play alert sound (would implement actual audio in production)
      console.log('🚨 URGENT PATIENT ALERT!');
    }
  }, [queueItems, searchTerm, priorityFilter, departmentFilter, statusFilter, soundEnabled]);

  const loadQueueData = async () => {
    try {
      console.log('ReceptionistPortal: Loading queue data...');

      // Try to load real data first
      const [queueStats, queueData] = await Promise.all([
        queueService.getQueueStatistics(),
        queueService.getAllQueues()
      ]);

      console.log('ReceptionistPortal: Real data loaded:', { queueStats, queueData });

      setStats({
        totalWaiting: queueStats.total_waiting || 0,
        totalBeingServed: queueStats.total_being_served || 0,
        avgWaitTime: queueStats.avg_wait_time_today || 0,
        urgentCases: queueStats.urgent_cases || 0
      });

      // Transform queue data
      const transformedQueue = queueData.map((item: any) => ({
        id: item.id,
        patientName: item.patient?.name || 'Unknown Patient',
        queueNumber: item.queue_number || item.queueNumber,
        estimatedWait: item.estimated_wait_time || item.estimatedWaitTime || 0,
        priority: item.priority || 'medium',
        department: item.service?.department || 'General',
        checkInTime: item.created_at || new Date().toISOString(),
        status: item.status || 'waiting'
      }));

      setQueueItems(transformedQueue);
    } catch (error) {
      console.error('ReceptionistPortal: Failed to load real data, using mock data:', error);

      // Mock data fallback
      setStats({
        totalWaiting: 8,
        totalBeingServed: 3,
        avgWaitTime: 15,
        urgentCases: 2
      });

      setQueueItems([
        {
          id: 1,
          patientName: 'John Smith',
          queueNumber: 101,
          estimatedWait: 25,
          priority: 'medium',
          department: 'General Medicine',
          checkInTime: new Date().toISOString(),
          status: 'waiting'
        },
        {
          id: 2,
          patientName: 'Sarah Johnson',
          queueNumber: 102,
          estimatedWait: 5,
          priority: 'urgent',
          department: 'Emergency',
          checkInTime: new Date().toISOString(),
          status: 'waiting'
        },
        {
          id: 3,
          patientName: 'Mike Davis',
          queueNumber: 103,
          estimatedWait: 45,
          priority: 'low',
          department: 'Cardiology',
          checkInTime: new Date().toISOString(),
          status: 'being_served'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-yellow-500 text-black';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'waiting': return 'bg-blue-500 text-white';
      case 'being_served': return 'bg-purple-500 text-white';
      case 'completed': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white shadow-lg border-b"
      >
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center">
                <Monitor className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Receptionist Portal</h1>
                <p className="text-gray-600">Queue Management & Patient Coordination</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {/* Urgent Alerts */}
              <AnimatePresence>
                {urgentAlerts.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="animate-pulse"
                  >
                    <Alert className="border-red-200 bg-red-50">
                      <AlertTriangle className="h-4 w-4 text-red-600" />
                      <AlertDescription className="text-red-800 font-medium">
                        {urgentAlerts.length} Urgent Case{urgentAlerts.length > 1 ? 's' : ''}
                      </AlertDescription>
                    </Alert>
                  </motion.div>
                )}
              </AnimatePresence>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setSoundEnabled(!soundEnabled)}
              >
                {soundEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              </Button>

              <Button variant="outline" size="sm" onClick={loadQueueData}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>

              <Badge variant="outline" className="px-3 py-1">
                <Bell className="h-4 w-4 mr-2" />
                Live Updates
              </Badge>
            </div>
          </div>
        </div>
      </motion.header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="queue">Active Queue</TabsTrigger>
            <TabsTrigger value="checkin">Check-in</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Waiting Patients</p>
                        <p className="text-3xl font-bold text-blue-600">{stats.totalWaiting}</p>
                      </div>
                      <Users className="h-8 w-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Being Served</p>
                        <p className="text-3xl font-bold text-purple-600">{stats.totalBeingServed}</p>
                      </div>
                      <UserCheck className="h-8 w-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 }}
              >
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Avg Wait Time</p>
                        <p className="text-3xl font-bold text-green-600">{stats.avgWaitTime}m</p>
                      </div>
                      <Clock className="h-8 w-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
              >
                <Card className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Urgent Cases</p>
                        <p className="text-3xl font-bold text-red-600">{stats.urgentCases}</p>
                      </div>
                      <AlertTriangle className="h-8 w-8 text-red-600" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="h-5 w-5 mr-2" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button className="h-20 flex flex-col items-center justify-center space-y-2">
                    <UserCheck className="h-6 w-6" />
                    <span>New Patient Check-in</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
                    <Calendar className="h-6 w-6" />
                    <span>Schedule Appointment</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
                    <Phone className="h-6 w-6" />
                    <span>Emergency Call</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Active Queue Tab */}
          <TabsContent value="queue" className="space-y-6">
            {/* Search and Filters */}
            <Card>
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search patients..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Priorities</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Department" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Departments</SelectItem>
                      <SelectItem value="emergency">Emergency</SelectItem>
                      <SelectItem value="cardiology">Cardiology</SelectItem>
                      <SelectItem value="general">General Medicine</SelectItem>
                      <SelectItem value="laboratory">Laboratory</SelectItem>
                      <SelectItem value="radiology">Radiology</SelectItem>
                      <SelectItem value="pediatrics">Pediatrics</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="waiting">Waiting</SelectItem>
                      <SelectItem value="being_served">Being Served</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Queue List */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Active Queue ({filteredQueue.length} patients)</CardTitle>
                  <div className="flex items-center space-x-2">
                    <Dialog open={showCheckInDialog} onOpenChange={setShowCheckInDialog}>
                      <DialogTrigger asChild>
                        <Button size="sm">
                          <Plus className="h-4 w-4 mr-2" />
                          New Check-in
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Patient Check-in</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <Input placeholder="Patient Name" />
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Department" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="emergency">Emergency</SelectItem>
                              <SelectItem value="cardiology">Cardiology</SelectItem>
                              <SelectItem value="general">General Medicine</SelectItem>
                              <SelectItem value="laboratory">Laboratory</SelectItem>
                              <SelectItem value="radiology">Radiology</SelectItem>
                              <SelectItem value="pediatrics">Pediatrics</SelectItem>
                            </SelectContent>
                          </Select>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Priority" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="low">Low</SelectItem>
                              <SelectItem value="medium">Medium</SelectItem>
                              <SelectItem value="high">High</SelectItem>
                              <SelectItem value="urgent">Urgent</SelectItem>
                            </SelectContent>
                          </Select>
                          <div className="flex justify-end space-x-2">
                            <Button variant="outline" onClick={() => setShowCheckInDialog(false)}>
                              Cancel
                            </Button>
                            <Button onClick={() => setShowCheckInDialog(false)}>
                              Check-in Patient
                            </Button>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  <AnimatePresence>
                    {filteredQueue.map((item, index) => (
                      <motion.div
                        key={item.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ delay: index * 0.05 }}
                        className={`flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-all ${
                          item.priority === 'urgent' ? 'border-red-200 bg-red-50' : 'border-gray-200'
                        }`}
                      >
                        <div className="flex items-center space-x-4">
                          <div className={`text-lg font-bold ${
                            item.priority === 'urgent' ? 'text-red-600' : 'text-gray-900'
                          }`}>
                            #{item.queueNumber}
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{item.patientName}</p>
                            <p className="text-sm text-gray-600">{item.department}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <Badge className={getPriorityColor(item.priority)}>
                            {item.priority.toUpperCase()}
                          </Badge>
                          <Badge className={getStatusColor(item.status)}>
                            {item.status.replace('_', ' ').toUpperCase()}
                          </Badge>
                          <div className="text-right">
                            <p className="text-sm font-medium flex items-center">
                              <Timer className="h-3 w-3 mr-1" />
                              {item.estimatedWait} min wait
                            </p>
                            <p className="text-xs text-gray-500">
                              {new Date(item.checkInTime).toLocaleTimeString()}
                            </p>
                          </div>
                          <div className="flex space-x-2">
                            <Button size="sm" variant="outline" onClick={() => setSelectedPatient(item)}>
                              <Eye className="h-3 w-3 mr-1" />
                              View
                            </Button>
                            <Button size="sm" variant="outline">
                              <Edit className="h-3 w-3 mr-1" />
                              Update
                            </Button>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  {filteredQueue.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No patients match the current filters</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Check-in Tab */}
          <TabsContent value="checkin" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Quick Check-in */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Zap className="h-5 w-5 mr-2 text-green-600" />
                    Quick Check-in
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Input placeholder="Patient Name" />
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Department" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="emergency">🚨 Emergency</SelectItem>
                      <SelectItem value="cardiology">❤️ Cardiology</SelectItem>
                      <SelectItem value="general">🩺 General Medicine</SelectItem>
                      <SelectItem value="laboratory">🧪 Laboratory</SelectItem>
                      <SelectItem value="radiology">📺 Radiology</SelectItem>
                      <SelectItem value="pediatrics">👶 Pediatrics</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Priority Level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">🟢 Low</SelectItem>
                      <SelectItem value="medium">🟡 Medium</SelectItem>
                      <SelectItem value="high">🟠 High</SelectItem>
                      <SelectItem value="urgent">🔴 Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button className="w-full" size="lg">
                    <UserPlus className="h-4 w-4 mr-2" />
                    Check-in Patient
                  </Button>
                </CardContent>
              </Card>

              {/* Recent Check-ins */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Clock className="h-5 w-5 mr-2 text-blue-600" />
                    Recent Check-ins
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {queueItems.slice(0, 5).map((item) => (
                      <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium text-sm">{item.patientName}</p>
                          <p className="text-xs text-gray-600">#{item.queueNumber} • {item.department}</p>
                        </div>
                        <Badge className={getPriorityColor(item.priority)} variant="outline">
                          {item.priority}
                        </Badge>
                      </div>
                    ))}
                    {queueItems.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        <UserCheck className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No recent check-ins</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Check-in Statistics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-purple-600" />
                  Today's Check-in Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{queueItems.length}</div>
                    <div className="text-sm text-gray-600">Total Check-ins</div>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">{urgentAlerts.length}</div>
                    <div className="text-sm text-gray-600">Urgent Cases</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {queueItems.filter(item => item.status === 'completed').length}
                    </div>
                    <div className="text-sm text-gray-600">Completed</div>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {Math.round(stats.avgWaitTime)}m
                    </div>
                    <div className="text-sm text-gray-600">Avg Wait Time</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Performance Metrics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
                    Performance Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{stats.avgWaitTime}m</div>
                      <div className="text-sm text-gray-600">Avg Wait Time</div>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {Math.round((queueItems.filter(item => item.status === 'completed').length / Math.max(queueItems.length, 1)) * 100)}%
                      </div>
                      <div className="text-sm text-gray-600">Completion Rate</div>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">{stats.totalBeingServed}</div>
                      <div className="text-sm text-gray-600">Active Staff</div>
                    </div>
                    <div className="p-4 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">{stats.urgentCases}</div>
                      <div className="text-sm text-gray-600">Urgent Cases</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Department Breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2 text-green-600" />
                    Department Breakdown
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {['Emergency', 'Cardiology', 'General Medicine', 'Laboratory', 'Radiology', 'Pediatrics'].map((dept) => {
                      const count = queueItems.filter(item => item.department.toLowerCase().includes(dept.toLowerCase().split(' ')[0])).length;
                      const percentage = Math.round((count / Math.max(queueItems.length, 1)) * 100);
                      return (
                        <div key={dept} className="flex items-center justify-between">
                          <span className="text-sm font-medium">{dept}</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-green-600 h-2 rounded-full"
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600 w-8">{count}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Action Buttons */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-gray-600" />
                  Report Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button variant="outline" className="h-16 flex flex-col items-center justify-center space-y-2">
                    <FileText className="h-6 w-6" />
                    <span>Daily Summary</span>
                  </Button>
                  <Button variant="outline" className="h-16 flex flex-col items-center justify-center space-y-2">
                    <BarChart3 className="h-6 w-6" />
                    <span>Performance Report</span>
                  </Button>
                  <Button variant="outline" className="h-16 flex flex-col items-center justify-center space-y-2">
                    <Settings className="h-6 w-6" />
                    <span>Export Data</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ReceptionistPortal;