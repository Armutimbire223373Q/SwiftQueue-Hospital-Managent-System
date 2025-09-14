/**
 * Notification Service for Queue Management System
 * Handles real-time notifications and alerts
 */

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
}

export interface QueueNotification extends Notification {
  queueNumber: number;
  serviceName: string;
  status: 'waiting' | 'called' | 'serving' | 'completed';
  estimatedWait?: number;
}

class NotificationService {
  private notifications: Notification[] = [];
  private listeners: ((notifications: Notification[]) => void)[] = [];

  /**
   * Add a new notification
   */
  addNotification(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>): void {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    };

    this.notifications.unshift(newNotification);
    this.notifyListeners();
  }

  /**
   * Add a queue-specific notification
   */
  addQueueNotification(notification: Omit<QueueNotification, 'id' | 'timestamp' | 'read'>): void {
    const queueNotification: QueueNotification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    };

    this.notifications.unshift(queueNotification);
    this.notifyListeners();
  }

  /**
   * Mark notification as read
   */
  markAsRead(notificationId: string): void {
    const notification = this.notifications.find(n => n.id === notificationId);
    if (notification) {
      notification.read = true;
      this.notifyListeners();
    }
  }

  /**
   * Mark all notifications as read
   */
  markAllAsRead(): void {
    this.notifications.forEach(n => n.read = true);
    this.notifyListeners();
  }

  /**
   * Remove notification
   */
  removeNotification(notificationId: string): void {
    this.notifications = this.notifications.filter(n => n.id !== notificationId);
    this.notifyListeners();
  }

  /**
   * Get all notifications
   */
  getNotifications(): Notification[] {
    return [...this.notifications];
  }

  /**
   * Get unread notifications
   */
  getUnreadNotifications(): Notification[] {
    return this.notifications.filter(n => !n.read);
  }

  /**
   * Get unread count
   */
  getUnreadCount(): number {
    return this.notifications.filter(n => !n.read).length;
  }

  /**
   * Subscribe to notification changes
   */
  subscribe(listener: (notifications: Notification[]) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  /**
   * Notify all listeners
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => listener([...this.notifications]));
  }

  /**
   * Clear all notifications
   */
  clearAll(): void {
    this.notifications = [];
    this.notifyListeners();
  }

  /**
   * Simulate queue status notifications
   */
  simulateQueueNotification(queueNumber: number, serviceName: string, status: string): void {
    let type: Notification['type'] = 'info';
    let title = '';
    let message = '';

    switch (status) {
      case 'called':
        type = 'success';
        title = 'You\'re Next!';
        message = `Queue #${queueNumber} - Please proceed to ${serviceName}`;
        break;
      case 'serving':
        type = 'info';
        title = 'Being Served';
        message = `Queue #${queueNumber} - You are now being served at ${serviceName}`;
        break;
      case 'completed':
        type = 'success';
        title = 'Service Complete';
        message = `Queue #${queueNumber} - Your service at ${serviceName} is complete`;
        break;
      case 'waiting':
        type = 'info';
        title = 'In Queue';
        message = `Queue #${queueNumber} - You are in the queue for ${serviceName}`;
        break;
    }

    this.addQueueNotification({
      type,
      title,
      message,
      queueNumber,
      serviceName,
      status: status as any
    });
  }

  /**
   * Simulate system notifications
   */
  simulateSystemNotification(): void {
    const notifications = [
      {
        type: 'info' as const,
        title: 'System Update',
        message: 'Queue management system has been updated with new features'
      },
      {
        type: 'warning' as const,
        title: 'High Wait Times',
        message: 'Current wait times are longer than usual. Thank you for your patience.'
      },
      {
        type: 'success' as const,
        title: 'Service Optimized',
        message: 'AI has optimized your queue position for faster service'
      }
    ];

    const randomNotification = notifications[Math.floor(Math.random() * notifications.length)];
    this.addNotification(randomNotification);
  }
}

// Export singleton instance
export const notificationService = new NotificationService();
export default notificationService;
