import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface NotificationData {
  type: 'queue_update' | 'appointment_reminder' | 'emergency_alert' | 'general';
  title: string;
  message: string;
  data?: any;
  priority?: 'default' | 'high' | 'max';
}

class NotificationService {
  constructor() {
    this.initialize();
  }

  // Initialize notifications
  async initialize(): Promise<void> {
    // Request permissions
    const { status } = await Notifications.requestPermissionsAsync();
    if (status !== 'granted') {
      console.warn('Notification permissions not granted');
      return;
    }

    // Configure notification handler
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
        shouldShowBanner: true,
        shouldShowList: true,
      }),
    });

    // Configure for Android
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'Default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });

      await Notifications.setNotificationChannelAsync('emergency', {
        name: 'Emergency',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 1000, 500, 1000],
        lightColor: '#FF0000',
        sound: 'emergency.wav', // Add custom sound file
      });
    }
  }

  // Send local notification
  async sendLocalNotification(notificationData: NotificationData): Promise<string> {
    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title: notificationData.title,
          body: notificationData.message,
          data: notificationData.data || {},
          sound: notificationData.type === 'emergency_alert' ? 'default' : undefined,
        },
        trigger: null, // Send immediately
      });

      console.log('Local notification sent:', notificationId);
      return notificationId;
    } catch (error) {
      console.error('Error sending local notification:', error);
      throw error;
    }
  }

  // Schedule notification
  async scheduleNotification(
    notificationData: NotificationData,
    secondsFromNow: number
  ): Promise<string> {
    try {
      const trigger: Notifications.TimeIntervalTriggerInput = {
        type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL,
        seconds: secondsFromNow,
      };

      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title: notificationData.title,
          body: notificationData.message,
          data: notificationData.data || {},
        },
        trigger: trigger,
      });

      console.log('Scheduled notification:', notificationId);
      return notificationId;
    } catch (error) {
      console.error('Error scheduling notification:', error);
      throw error;
    }
  }

  // Cancel notification
  async cancelNotification(notificationId: string): Promise<void> {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId);
      console.log('Notification cancelled:', notificationId);
    } catch (error) {
      console.error('Error cancelling notification:', error);
    }
  }

  // Cancel all notifications
  async cancelAllNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      console.log('All notifications cancelled');
    } catch (error) {
      console.error('Error cancelling all notifications:', error);
    }
  }

  // Get notification history
  async getNotificationHistory(): Promise<any[]> {
    try {
      const history = await AsyncStorage.getItem('notificationHistory');
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.error('Error getting notification history:', error);
      return [];
    }
  }

  // Save notification to history
  private async saveToHistory(notification: NotificationData): Promise<void> {
    try {
      const history = await this.getNotificationHistory();
      history.unshift({
        ...notification,
        timestamp: new Date().toISOString(),
        id: Date.now().toString(),
      });

      // Keep only last 100 notifications
      const trimmedHistory = history.slice(0, 100);

      await AsyncStorage.setItem('notificationHistory', JSON.stringify(trimmedHistory));
    } catch (error) {
      console.error('Error saving notification to history:', error);
    }
  }

  // Send queue update notification
  async sendQueueUpdateNotification(
    queueNumber: string,
    position: number,
    estimatedWait: number,
    department: string
  ): Promise<void> {
    const notification: NotificationData = {
      type: 'queue_update',
      title: 'Queue Update',
      message: `Your queue position: ${position}. Estimated wait: ${estimatedWait} minutes.`,
      data: {
        queueNumber,
        position,
        estimatedWait,
        department,
      },
      priority: 'default',
    };

    await this.sendLocalNotification(notification);
    await this.saveToHistory(notification);
  }

  // Send appointment reminder
  async sendAppointmentReminder(
    appointmentTime: string,
    department: string,
    doctorName?: string
  ): Promise<void> {
    const title = doctorName ? `Appointment with Dr. ${doctorName}` : 'Appointment Reminder';
    const message = `You have an appointment at ${appointmentTime} in ${department}. Please arrive 15 minutes early.`;

    const notification: NotificationData = {
      type: 'appointment_reminder',
      title: title,
      message: message,
      data: {
        appointmentTime,
        department,
        doctorName,
      },
      priority: 'high',
    };

    await this.sendLocalNotification(notification);
    await this.saveToHistory(notification);
  }

  // Send emergency alert
  async sendEmergencyAlert(
    title: string,
    message: string,
    emergencyData?: any
  ): Promise<void> {
    const notification: NotificationData = {
      type: 'emergency_alert',
      title: title,
      message: message,
      data: emergencyData || {},
      priority: 'max',
    };

    await this.sendLocalNotification(notification);
    await this.saveToHistory(notification);
  }


  // Get badge count
  async getBadgeCount(): Promise<number> {
    try {
      const badge = await Notifications.getBadgeCountAsync();
      return badge;
    } catch (error) {
      console.error('Error getting badge count:', error);
      return 0;
    }
  }

  // Set badge count
  async setBadgeCount(count: number): Promise<void> {
    try {
      await Notifications.setBadgeCountAsync(count);
    } catch (error) {
      console.error('Error setting badge count:', error);
    }
  }

  // Clear badge
  async clearBadge(): Promise<void> {
    await this.setBadgeCount(0);
  }

  // Check notification permissions
  async checkPermissions(): Promise<boolean> {
    try {
      const { status } = await Notifications.getPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error checking permissions:', error);
      return false;
    }
  }

  // Request permissions
  async requestPermissions(): Promise<boolean> {
    try {
      const { status } = await Notifications.requestPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('Error requesting permissions:', error);
      return false;
    }
  }
}

export const notificationService = new NotificationService();