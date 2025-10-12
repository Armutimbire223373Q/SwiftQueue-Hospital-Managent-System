import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import {
  Users,
  Calendar,
  MessageSquare,
  CheckSquare,
  BarChart3,
  Clock,
  UserCheck,
  AlertTriangle,
  Send,
  Plus,
  Eye,
  EyeOff
} from "lucide-react";
import { authService } from "@/services/authService";
import { apiService } from "@/services/apiService";

interface StaffProfile {
  id: number;
  user_id: number;
  employee_id: string;
  department: string;
  specialization: string;
  performance_rating: number;
  is_supervisor: boolean;
  contract_type: string;
  languages_spoken: string[];
  emergency_certified: boolean;
}

interface StaffSchedule {
  id: number;
  shift_date: string;
  shift_type: string;
  start_time: string;
  end_time: string;
  assigned_service_id?: number;
  notes?: string;
}

interface StaffMessage {
  id: number;
  sender_id: number;
  subject: string;
  message: string;
  message_type: string;
  priority: string;
  is_read: boolean;
  created_at: string;
  sender_name: string;
}

interface StaffTask {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  due_date?: string;
  assigned_by: number;
  created_at: string;
  assigner_name: string;
}

interface StaffStats {
  total_staff: number;
  active_staff: number;
  supervisors: number;
  departments: Record<string, number>;
  avg_performance: number;
  emergency_certified: number;
}

export default function StaffPortal() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Staff data
  const [profile, setProfile] = useState<StaffProfile | null>(null);
  const [schedule, setSchedule] = useState<StaffSchedule[]>([]);
  const [messages, setMessages] = useState<StaffMessage[]>([]);
  const [tasks, setTasks] = useState<StaffTask[]>([]);
  const [stats, setStats] = useState<StaffStats | null>(null);

  // UI state
  const [showMessageDialog, setShowMessageDialog] = useState(false);
  const [showTaskDialog, setShowTaskDialog] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState<StaffMessage | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);

  // Form state
  const [messageForm, setMessageForm] = useState({
    recipient_id: '',
    subject: '',
    message: '',
    priority: 'normal'
  });

  const [taskForm, setTaskForm] = useState({
    title: '',
    description: '',
    priority: 'normal',
    due_date: ''
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      await Promise.all([
        loadStaffProfile(),
        loadSchedule(),
        loadMessages(),
        loadTasks(),
        loadStats()
      ]);
    } catch (err) {
      setError("Failed to load staff data");
      console.error("Error loading staff data:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadStaffProfile = async () => {
    try {
      const response = await apiService.get('/api/staff/profile');
      setProfile(response.data);
    } catch (err) {
      console.error("Error loading staff profile:", err);
    }
  };

  const loadSchedule = async () => {
    try {
      const startDate = new Date();
      const endDate = new Date();
      endDate.setDate(endDate.getDate() + 30); // Next 30 days

      const response = await apiService.get('/api/staff/schedule/1', {
        params: {
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        }
      });
      setSchedule(response.data);
    } catch (err) {
      console.error("Error loading schedule:", err);
    }
  };

  const loadMessages = async () => {
    try {
      const response = await apiService.get('/api/staff/messages');
      setMessages(response.data);
      setUnreadCount(response.data.filter((msg: StaffMessage) => !msg.is_read).length);
    } catch (err) {
      console.error("Error loading messages:", err);
    }
  };

  const loadTasks = async () => {
    try {
      const response = await apiService.get('/api/staff/tasks');
      setTasks(response.data);
    } catch (err) {
      console.error("Error loading tasks:", err);
    }
  };

  const loadStats = async () => {
    try {
      const response = await apiService.get('/api/staff/stats');
      setStats(response.data);
    } catch (err) {
      console.error("Error loading stats:", err);
    }
  };

  const handleSendMessage = async () => {
    if (!messageForm.subject.trim() || !messageForm.message.trim()) {
      setError("Please fill in all required fields");
      return;
    }

    try {
      await apiService.post('/api/staff/messages', messageForm);
      setMessageForm({ recipient_id: '', subject: '', message: '', priority: 'normal' });
      setShowMessageDialog(false);
      await loadMessages();
    } catch (err) {
      setError("Failed to send message");
      console.error("Error sending message:", err);
    }
  };

  const handleCreateTask = async () => {
    if (!taskForm.title.trim()) {
      setError("Please enter a task title");
      return;
    }

    try {
      await apiService.post('/api/staff/tasks', taskForm);
      setTaskForm({ title: '', description: '', priority: 'normal', due_date: '' });
      setShowTaskDialog(false);
      await loadTasks();
    } catch (err) {
      setError("Failed to create task");
      console.error("Error creating task:", err);
    }
  };

  const handleMarkMessageRead = async (messageId: number) => {
    try {
      await apiService.put(`/api/staff/messages/${messageId}/read`);
      await loadMessages();
    } catch (err) {
      console.error("Error marking message as read:", err);
    }
  };

  const handleUpdateTaskStatus = async (taskId: number, status: string) => {
    try {
      await apiService.put(`/api/staff/tasks/${taskId}/status`, { status });
      await loadTasks();
    } catch (err) {
      setError("Failed to update task status");
      console.error("Error updating task status:", err);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'normal': return 'bg-blue-500';
      case 'low': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'in_progress': return 'bg-blue-500';
      case 'pending': return 'bg-yellow-500';
      case 'cancelled': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="lg" text="Loading staff portal..." />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Staff Portal</h1>
          <p className="text-gray-600">Manage your schedule, communications, and tasks</p>
        </div>

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="schedule" className="flex items-center space-x-2">
              <Calendar className="h-4 w-4" />
              <span>Schedule</span>
            </TabsTrigger>
            <TabsTrigger value="messages" className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4" />
              <span>Messages {unreadCount > 0 && `(${unreadCount})`}</span>
            </TabsTrigger>
            <TabsTrigger value="tasks" className="flex items-center space-x-2">
              <CheckSquare className="h-4 w-4" />
              <span>Tasks</span>
            </TabsTrigger>
            <TabsTrigger value="profile" className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>Profile</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">My Performance</CardTitle>
                  <BarChart3 className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-600">
                    {profile?.performance_rating || 0}/5
                  </div>
                  <p className="text-xs text-muted-foreground">Performance rating</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Tasks</CardTitle>
                  <CheckSquare className="h-4 w-4 text-orange-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">
                    {tasks.filter(t => t.status !== 'completed').length}
                  </div>
                  <p className="text-xs text-muted-foreground">Pending tasks</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Unread Messages</CardTitle>
                  <MessageSquare className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{unreadCount}</div>
                  <p className="text-xs text-muted-foreground">New messages</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Today's Shifts</CardTitle>
                  <Clock className="h-4 w-4 text-purple-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-purple-600">
                    {schedule.filter(s => {
                      const shiftDate = new Date(s.shift_date).toDateString();
                      const today = new Date().toDateString();
                      return shiftDate === today;
                    }).length}
                  </div>
                  <p className="text-xs text-muted-foreground">Scheduled shifts</p>
                </CardContent>
              </Card>
            </div>

            {/* Department Stats */}
            {stats && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="h-5 w-5" />
                    <span>Department Overview</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{stats.total_staff}</div>
                      <div className="text-sm text-gray-600">Total Staff</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{stats.active_staff}</div>
                      <div className="text-sm text-gray-600">Active Staff</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">{stats.supervisors}</div>
                      <div className="text-sm text-gray-600">Supervisors</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{stats.emergency_certified}</div>
                      <div className="text-sm text-gray-600">Emergency Certified</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Schedule Tab */}
          <TabsContent value="schedule" className="space-y-6">
            <Card>
              <CardHeader className="flex justify-between items-center">
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5" />
                  <span>My Schedule</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {schedule.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No scheduled shifts found</p>
                    </div>
                  ) : (
                    schedule.map((shift) => (
                      <div key={shift.id} className="border rounded-lg p-4 bg-white">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="font-medium text-gray-900">
                              {new Date(shift.shift_date).toLocaleDateString()}
                            </h3>
                            <p className="text-sm text-gray-600 capitalize">{shift.shift_type} Shift</p>
                          </div>
                          <Badge variant="outline" className="capitalize">
                            {shift.shift_type}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <div className="flex items-center space-x-2 mb-2">
                              <Clock className="h-4 w-4 text-gray-500" />
                              <span className="text-sm">
                                {new Date(shift.start_time).toLocaleTimeString()} - {new Date(shift.end_time).toLocaleTimeString()}
                              </span>
                            </div>
                            {shift.assigned_service_id && (
                              <div className="flex items-center space-x-2">
                                <UserCheck className="h-4 w-4 text-gray-500" />
                                <span className="text-sm">Service ID: {shift.assigned_service_id}</span>
                              </div>
                            )}
                          </div>
                          {shift.notes && (
                            <div className="bg-gray-50 p-3 rounded border">
                              <p className="text-sm text-gray-700">{shift.notes}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Messages Tab */}
          <TabsContent value="messages" className="space-y-6">
            <Card>
              <CardHeader className="flex justify-between items-center">
                <CardTitle className="flex items-center space-x-2">
                  <MessageSquare className="h-5 w-5" />
                  <span>Messages</span>
                </CardTitle>
                <Dialog open={showMessageDialog} onOpenChange={setShowMessageDialog}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      New Message
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Send New Message</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="recipient">Recipient (Optional - leave empty for broadcast)</Label>
                        <Input
                          id="recipient"
                          placeholder="Recipient ID"
                          value={messageForm.recipient_id}
                          onChange={(e) => setMessageForm({...messageForm, recipient_id: e.target.value})}
                        />
                      </div>
                      <div>
                        <Label htmlFor="subject">Subject *</Label>
                        <Input
                          id="subject"
                          placeholder="Message subject"
                          value={messageForm.subject}
                          onChange={(e) => setMessageForm({...messageForm, subject: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="priority">Priority</Label>
                        <Select value={messageForm.priority} onValueChange={(value) => setMessageForm({...messageForm, priority: value})}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="low">Low</SelectItem>
                            <SelectItem value="normal">Normal</SelectItem>
                            <SelectItem value="high">High</SelectItem>
                            <SelectItem value="urgent">Urgent</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="message">Message *</Label>
                        <Textarea
                          id="message"
                          placeholder="Type your message here..."
                          value={messageForm.message}
                          onChange={(e) => setMessageForm({...messageForm, message: e.target.value})}
                          rows={4}
                          required
                        />
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" onClick={() => setShowMessageDialog(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleSendMessage}>
                          <Send className="h-4 w-4 mr-2" />
                          Send Message
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {messages.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No messages found</p>
                    </div>
                  ) : (
                    messages.map((message) => (
                      <div key={message.id} className={`border rounded-lg p-4 ${!message.is_read ? 'bg-blue-50 border-blue-200' : 'bg-white'}`}>
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <h3 className="font-medium text-gray-900">{message.subject}</h3>
                              {!message.is_read && (
                                <Badge variant="secondary" className="text-xs">Unread</Badge>
                              )}
                            </div>
                            <p className="text-sm text-gray-600">From: {message.sender_name}</p>
                            <p className="text-xs text-gray-500">
                              {new Date(message.created_at).toLocaleString()}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={`${getPriorityColor(message.priority)} text-white`}>
                              {message.priority}
                            </Badge>
                            {!message.is_read && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleMarkMessageRead(message.id)}
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                        <div className="bg-gray-50 p-3 rounded border">
                          <p className="text-sm text-gray-700 whitespace-pre-wrap">{message.message}</p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tasks Tab */}
          <TabsContent value="tasks" className="space-y-6">
            <Card>
              <CardHeader className="flex justify-between items-center">
                <CardTitle className="flex items-center space-x-2">
                  <CheckSquare className="h-5 w-5" />
                  <span>My Tasks</span>
                </CardTitle>
                <Dialog open={showTaskDialog} onOpenChange={setShowTaskDialog}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      New Task
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Task</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="title">Title *</Label>
                        <Input
                          id="title"
                          placeholder="Task title"
                          value={taskForm.title}
                          onChange={(e) => setTaskForm({...taskForm, title: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          placeholder="Task description"
                          value={taskForm.description}
                          onChange={(e) => setTaskForm({...taskForm, description: e.target.value})}
                          rows={3}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="priority">Priority</Label>
                          <Select value={taskForm.priority} onValueChange={(value) => setTaskForm({...taskForm, priority: value})}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="low">Low</SelectItem>
                              <SelectItem value="normal">Normal</SelectItem>
                              <SelectItem value="high">High</SelectItem>
                              <SelectItem value="urgent">Urgent</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="due_date">Due Date</Label>
                          <Input
                            id="due_date"
                            type="datetime-local"
                            value={taskForm.due_date}
                            onChange={(e) => setTaskForm({...taskForm, due_date: e.target.value})}
                          />
                        </div>
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" onClick={() => setShowTaskDialog(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleCreateTask}>
                          <Plus className="h-4 w-4 mr-2" />
                          Create Task
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {tasks.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <CheckSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No tasks found</p>
                    </div>
                  ) : (
                    tasks.map((task) => (
                      <div key={task.id} className="border rounded-lg p-4 bg-white">
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <h3 className="font-medium text-gray-900">{task.title}</h3>
                              <Badge className={`${getPriorityColor(task.priority)} text-white`}>
                                {task.priority}
                              </Badge>
                              <Badge className={`${getStatusColor(task.status)} text-white`}>
                                {task.status.replace('_', ' ')}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600">Assigned by: {task.assigner_name}</p>
                            {task.due_date && (
                              <p className="text-xs text-gray-500">
                                Due: {new Date(task.due_date).toLocaleString()}
                              </p>
                            )}
                          </div>
                          {task.status !== 'completed' && (
                            <Select onValueChange={(value) => handleUpdateTaskStatus(task.id, value)}>
                              <SelectTrigger className="w-32">
                                <SelectValue placeholder="Update status" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="pending">Pending</SelectItem>
                                <SelectItem value="in_progress">In Progress</SelectItem>
                                <SelectItem value="completed">Completed</SelectItem>
                                <SelectItem value="cancelled">Cancelled</SelectItem>
                              </SelectContent>
                            </Select>
                          )}
                        </div>
                        {task.description && (
                          <div className="bg-gray-50 p-3 rounded border">
                            <p className="text-sm text-gray-700 whitespace-pre-wrap">{task.description}</p>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            {profile && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="h-5 w-5" />
                    <span>Staff Profile</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Employee ID</Label>
                        <p className="text-sm text-gray-900">{profile.employee_id}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Department</Label>
                        <p className="text-sm text-gray-900">{profile.department}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Specialization</Label>
                        <p className="text-sm text-gray-900">{profile.specialization || 'Not specified'}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Contract Type</Label>
                        <p className="text-sm text-gray-900 capitalize">{profile.contract_type.replace('_', ' ')}</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Performance Rating</Label>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-900">{profile.performance_rating}/5</span>
                          <div className="flex">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <span
                                key={star}
                                className={`text-lg ${star <= profile.performance_rating ? 'text-yellow-400' : 'text-gray-300'}`}
                              >
                                ★
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Supervisor</Label>
                        <p className="text-sm text-gray-900">{profile.is_supervisor ? 'Yes' : 'No'}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Emergency Certified</Label>
                        <p className="text-sm text-gray-900">{profile.emergency_certified ? 'Yes' : 'No'}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium text-gray-700">Languages</Label>
                        <p className="text-sm text-gray-900">
                          {profile.languages_spoken.length > 0 ? profile.languages_spoken.join(', ') : 'Not specified'}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}