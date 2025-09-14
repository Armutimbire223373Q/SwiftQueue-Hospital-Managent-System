/**
 * Demo Service for SwiftQueue Hospital
 * Provides sample data for demonstration purposes
 */

export interface DemoStats {
  totalPatients: number;
  avgWaitTime: number;
  efficiencyScore: number;
  activeDepartments: number;
}

export interface DemoDepartment {
  name: string;
  waitTime: string;
  patients: number;
  status: 'low' | 'medium' | 'high' | 'critical';
}

export interface DemoNotification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timestamp: Date;
  read: boolean;
}

class DemoService {
  private stats: DemoStats = {
    totalPatients: 12,
    avgWaitTime: 18,
    efficiencyScore: 92,
    activeDepartments: 6
  };

  private departments: DemoDepartment[] = [
    { name: 'Emergency Care', waitTime: '5 min', patients: 3, status: 'medium' },
    { name: 'Cardiology', waitTime: '15 min', patients: 2, status: 'low' },
    { name: 'General Medicine', waitTime: '12 min', patients: 4, status: 'medium' },
    { name: 'Laboratory', waitTime: '8 min', patients: 1, status: 'low' },
    { name: 'Radiology', waitTime: '20 min', patients: 2, status: 'high' },
    { name: 'Pediatrics', waitTime: '10 min', patients: 1, status: 'low' }
  ];

  private notifications: DemoNotification[] = [
    {
      id: '1',
      title: 'System Update',
      message: 'Queue management system has been updated with new AI features',
      type: 'info',
      timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
      read: false
    },
    {
      id: '2',
      title: 'High Wait Times',
      message: 'Radiology department is experiencing longer wait times than usual',
      type: 'warning',
      timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
      read: false
    },
    {
      id: '3',
      title: 'Service Optimized',
      message: 'AI has optimized your queue position for faster service',
      type: 'success',
      timestamp: new Date(Date.now() - 1000 * 60 * 5), // 5 minutes ago
      read: true
    }
  ];

  /**
   * Get current statistics
   */
  getStats(): DemoStats {
    return { ...this.stats };
  }

  /**
   * Update statistics with some randomness
   */
  updateStats(): DemoStats {
    this.stats = {
      totalPatients: Math.max(0, this.stats.totalPatients + Math.floor(Math.random() * 3) - 1),
      avgWaitTime: Math.max(5, this.stats.avgWaitTime + Math.floor(Math.random() * 6) - 3),
      efficiencyScore: Math.min(100, Math.max(80, this.stats.efficiencyScore + Math.floor(Math.random() * 6) - 3)),
      activeDepartments: 6
    };
    return this.getStats();
  }

  /**
   * Get department information
   */
  getDepartments(): DemoDepartment[] {
    return [...this.departments];
  }

  /**
   * Update department wait times
   */
  updateDepartments(): DemoDepartment[] {
    this.departments = this.departments.map(dept => ({
      ...dept,
      waitTime: `${Math.max(3, Math.floor(Math.random() * 25) + 5)} min`,
      patients: Math.max(0, dept.patients + Math.floor(Math.random() * 3) - 1),
      status: this.getRandomStatus()
    }));
    return this.getDepartments();
  }

  /**
   * Get notifications
   */
  getNotifications(): DemoNotification[] {
    return [...this.notifications];
  }

  /**
   * Add a new notification
   */
  addNotification(notification: Omit<DemoNotification, 'id' | 'timestamp' | 'read'>): void {
    const newNotification: DemoNotification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    };
    this.notifications.unshift(newNotification);
    this.notifications = this.notifications.slice(0, 10); // Keep only last 10
  }

  /**
   * Mark notification as read
   */
  markAsRead(id: string): void {
    const notification = this.notifications.find(n => n.id === id);
    if (notification) {
      notification.read = true;
    }
  }

  /**
   * Get unread count
   */
  getUnreadCount(): number {
    return this.notifications.filter(n => !n.read).length;
  }

  /**
   * Simulate real-time updates
   */
  startRealTimeUpdates(callback: () => void): () => void {
    const interval = setInterval(() => {
      this.updateStats();
      this.updateDepartments();
      callback();
    }, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }

  /**
   * Get random status based on wait time
   */
  private getRandomStatus(): 'low' | 'medium' | 'high' | 'critical' {
    const statuses = ['low', 'medium', 'high', 'critical'] as const;
    return statuses[Math.floor(Math.random() * statuses.length)];
  }

  /**
   * Generate sample queue data
   */
  generateQueueData() {
    return {
      currentQueue: Math.floor(Math.random() * 50) + 1,
      estimatedWait: Math.floor(Math.random() * 30) + 5,
      position: Math.floor(Math.random() * 10) + 1,
      services: [
        { id: 1, name: 'Emergency Care', waitTime: 5, patients: 3 },
        { id: 2, name: 'General Medicine', waitTime: 12, patients: 4 },
        { id: 3, name: 'Cardiology', waitTime: 15, patients: 2 },
        { id: 4, name: 'Laboratory', waitTime: 8, patients: 1 },
        { id: 5, name: 'Radiology', waitTime: 20, patients: 2 },
        { id: 6, name: 'Pediatrics', waitTime: 10, patients: 1 }
      ]
    };
  }

  /**
   * Generate sample analytics data
   */
  generateAnalyticsData() {
    return {
      dailyStats: {
        totalPatients: Math.floor(Math.random() * 100) + 50,
        avgWaitTime: Math.floor(Math.random() * 20) + 10,
        efficiencyScore: Math.floor(Math.random() * 20) + 80,
        patientSatisfaction: Math.floor(Math.random() * 20) + 80
      },
      hourlyData: Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        patients: Math.floor(Math.random() * 20) + 5,
        waitTime: Math.floor(Math.random() * 15) + 5
      })),
      departmentStats: this.departments.map(dept => ({
        name: dept.name,
        patients: dept.patients,
        avgWaitTime: parseInt(dept.waitTime),
        efficiency: Math.floor(Math.random() * 30) + 70
      }))
    };
  }
}

export const demoService = new DemoService();
export default demoService;
