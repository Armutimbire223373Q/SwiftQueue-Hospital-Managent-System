import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from './apiService';
import { notificationService } from './notificationService';

export interface OfflineQueueRequest {
  id: string;
  serviceId: number;
  priority: string;
  symptoms?: string;
  timestamp: number;
  synced: boolean;
  retryCount: number;
  lastRetry?: number;
}

export interface QueueStatus {
  queueNumber?: number;
  position?: number;
  estimatedWait?: number;
  status: 'pending' | 'confirmed' | 'error';
  error?: string;
}

class OfflineQueueService {
  private static readonly STORAGE_KEY = 'offlineQueueRequests';
  private static readonly SYNC_INTERVAL = 30000; // 30 seconds
  private syncInterval: NodeJS.Timeout | null = null;
  private isOnline = true;

  constructor() {
    this.initialize();
  }

  // Initialize the service
  async initialize(): Promise<void> {
    // Start periodic sync
    this.startPeriodicSync();

    // Check connectivity periodically
    this.checkConnectivity();
  }

  // Check connectivity (simplified version)
  private async checkConnectivity(): Promise<void> {
    try {
      const isConnected = await apiService.checkConnectivity();
      const wasOnline = this.isOnline;
      this.isOnline = isConnected;

      if (!wasOnline && this.isOnline) {
        // Came back online, sync pending requests
        this.syncPendingRequests();
      }
    } catch (error) {
      this.isOnline = false;
    }
  }

  // Start periodic sync for pending requests
  private startPeriodicSync(): void {
    this.syncInterval = setInterval(() => {
      if (this.isOnline) {
        this.syncPendingRequests();
      }
    }, OfflineQueueService.SYNC_INTERVAL);
  }

  // Stop periodic sync
  stopPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  // Join queue (works offline)
  async joinQueue(serviceId: number, priority: string = 'normal', symptoms?: string): Promise<QueueStatus> {
    const request: OfflineQueueRequest = {
      id: `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      serviceId,
      priority,
      symptoms,
      timestamp: Date.now(),
      synced: false,
      retryCount: 0,
    };

    try {
      // Save to offline storage
      await this.saveOfflineRequest(request);

      // Try to sync immediately if online
      if (this.isOnline) {
        const result = await this.syncRequest(request);
        if (result.success && result.data) {
          request.synced = true;
          await this.updateOfflineRequest(request);
          return result.data;
        }
      }

      // Return pending status for offline mode
      return {
        status: 'pending',
        error: 'Request saved offline. Will sync when connection is restored.',
      };

    } catch (error) {
      console.error('Error joining queue:', error);
      return {
        status: 'error',
        error: 'Failed to save queue request',
      };
    }
  }

  // Sync a single request
  private async syncRequest(request: OfflineQueueRequest): Promise<{success: boolean; data?: QueueStatus; error?: string}> {
    try {
      const response = await apiService.post('/api/queue/join', {
        service_id: request.serviceId,
        priority: request.priority,
        symptoms: request.symptoms,
      });

      if (response.success) {
        // Send success notification
        await notificationService.sendLocalNotification({
          type: 'queue_update',
          title: 'Queue Joined Successfully',
          message: `You have joined the queue. Your number is ${response.data?.queue_number || 'pending'}.`,
          data: response.data,
        });

        return {
          success: true,
          data: {
            queueNumber: response.data?.queue_number,
            position: response.data?.position,
            estimatedWait: response.data?.estimated_wait,
            status: 'confirmed',
          },
        };
      } else {
        throw new Error(response.error || 'Failed to join queue');
      }

    } catch (error) {
      console.error(`Failed to sync request ${request.id}:`, error);
      request.retryCount++;
      request.lastRetry = Date.now();
      await this.updateOfflineRequest(request);

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Sync failed',
      };
    }
  }

  // Sync all pending requests
  async syncPendingRequests(): Promise<void> {
    if (!this.isOnline) return;

    try {
      const pendingRequests = await this.getPendingRequests();

      if (pendingRequests.length === 0) return;

      console.log(`Syncing ${pendingRequests.length} pending queue requests...`);

      for (const request of pendingRequests) {
        // Skip if recently retried (avoid spam)
        if (request.lastRetry && Date.now() - request.lastRetry < 10000) {
          continue;
        }

        // Skip if too many retries
        if (request.retryCount >= 5) {
          console.warn(`Request ${request.id} has exceeded retry limit`);
          continue;
        }

        const result = await this.syncRequest(request);

        if (result.success) {
          request.synced = true;
          await this.updateOfflineRequest(request);

          // Send notification about successful sync
          await notificationService.sendLocalNotification({
            type: 'queue_update',
            title: 'Offline Queue Synced',
            message: 'Your offline queue request has been successfully processed.',
            data: result.data,
          });
        }
      }

    } catch (error) {
      console.error('Error syncing pending requests:', error);
    }
  }

  // Get pending offline requests
  async getPendingRequests(): Promise<OfflineQueueRequest[]> {
    try {
      const requests = await this.getAllOfflineRequests();
      return requests.filter(r => !r.synced);
    } catch (error) {
      console.error('Error getting pending requests:', error);
      return [];
    }
  }

  // Get all offline requests
  private async getAllOfflineRequests(): Promise<OfflineQueueRequest[]> {
    try {
      const data = await AsyncStorage.getItem(OfflineQueueService.STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error getting offline requests:', error);
      return [];
    }
  }

  // Save offline request
  private async saveOfflineRequest(request: OfflineQueueRequest): Promise<void> {
    try {
      const requests = await this.getAllOfflineRequests();
      requests.push(request);
      await AsyncStorage.setItem(OfflineQueueService.STORAGE_KEY, JSON.stringify(requests));
    } catch (error) {
      console.error('Error saving offline request:', error);
      throw error;
    }
  }

  // Update offline request
  private async updateOfflineRequest(updatedRequest: OfflineQueueRequest): Promise<void> {
    try {
      const requests = await this.getAllOfflineRequests();
      const index = requests.findIndex(r => r.id === updatedRequest.id);

      if (index !== -1) {
        requests[index] = updatedRequest;
        await AsyncStorage.setItem(OfflineQueueService.STORAGE_KEY, JSON.stringify(requests));
      }
    } catch (error) {
      console.error('Error updating offline request:', error);
      throw error;
    }
  }

  // Remove offline request
  async removeOfflineRequest(requestId: string): Promise<void> {
    try {
      const requests = await this.getAllOfflineRequests();
      const filteredRequests = requests.filter(r => r.id !== requestId);
      await AsyncStorage.setItem(OfflineQueueService.STORAGE_KEY, JSON.stringify(filteredRequests));
    } catch (error) {
      console.error('Error removing offline request:', error);
      throw error;
    }
  }

  // Clear all offline requests
  async clearAllOfflineRequests(): Promise<void> {
    try {
      await AsyncStorage.removeItem(OfflineQueueService.STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing offline requests:', error);
      throw error;
    }
  }

  // Get offline queue statistics
  async getOfflineStats(): Promise<{
    total: number;
    pending: number;
    synced: number;
    failed: number;
  }> {
    try {
      const requests = await this.getAllOfflineRequests();
      const pending = requests.filter(r => !r.synced).length;
      const synced = requests.filter(r => r.synced).length;
      const failed = requests.filter(r => r.retryCount >= 5 && !r.synced).length;

      return {
        total: requests.length,
        pending,
        synced,
        failed,
      };
    } catch (error) {
      console.error('Error getting offline stats:', error);
      return {
        total: 0,
        pending: 0,
        synced: 0,
        failed: 0,
      };
    }
  }

  // Check if device is online
  isDeviceOnline(): boolean {
    return this.isOnline;
  }

  // Force sync (manual trigger)
  async forceSync(): Promise<{synced: number; failed: number; total: number}> {
    const stats = await this.getOfflineStats();
    await this.syncPendingRequests();

    const newStats = await this.getOfflineStats();

    return {
      synced: newStats.synced - stats.synced,
      failed: newStats.failed - stats.failed,
      total: newStats.pending,
    };
  }

  // Get queue status for offline request
  async getOfflineQueueStatus(requestId: string): Promise<QueueStatus | null> {
    try {
      const requests = await this.getAllOfflineRequests();
      const request = requests.find(r => r.id === requestId);

      if (!request) return null;

      if (request.synced) {
        // Try to get real-time status
        try {
          const response = await apiService.get(`/api/queue/status/${request.serviceId}`);
          if (response.success) {
            return {
              queueNumber: response.data?.queue_number,
              position: response.data?.position,
              estimatedWait: response.data?.estimated_wait,
              status: 'confirmed',
            };
          }
        } catch (error) {
          console.warn('Could not get real-time status:', error);
        }
      }

      return {
        status: request.synced ? 'confirmed' : 'pending',
        error: request.synced ? undefined : 'Request pending sync',
      };

    } catch (error) {
      console.error('Error getting offline queue status:', error);
      return null;
    }
  }
}

export const offlineQueueService = new OfflineQueueService();